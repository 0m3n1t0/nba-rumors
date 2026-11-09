"""Weekly skills: yt-plan, yt-audit, yt-retention, yt-comment.

Runs every Monday. Each skill checks for its own material and sleeps until it exists:

  yt-plan       always: plans the coming week from today's stories, audience signals and
                (once there is data) what worked. Saved to plan/week.json, which the AI editor
                reads, so the plan steers the daily picks.
  yt-audit      once the channel has 5+ public videos: the whole-channel review.
  yt-retention  once videos have 200+ views: pulls each video's audience-retention curve from
                the YouTube Analytics API, runs retention.py on it, and says what to change.
                Needs the yt-analytics.readonly permission (a one-time step); until then it
                says so and sleeps.
  yt-comment    switched OFF (owner's choice). It stays installed and can be turned on later
                with the repository variable COMMENTS=on; nothing is ever posted automatically.

The report is saved to the PRIVATE state repository (reports/), never a public GitHub Issue
or the public run summary (this repository is public).
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skills import claude, summary, tool  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PLAN = ROOT / "plan" / "week.json"
AUDIT_MIN_VIDEOS = 5
RETENTION_MIN_VIEWS = 200


def creds(scopes: list[str]):
    from google.oauth2.credentials import Credentials
    info = json.loads(os.environ["YT_CLIENT_SECRET"])
    c = info.get("installed") or info.get("web")
    return Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri=c["token_uri"],
                       client_id=c["client_id"], client_secret=c["client_secret"], scopes=scopes)


def service(name: str, version: str, scopes: list[str]):
    from googleapiclient.discovery import build
    return build(name, version, credentials=creds(scopes), cache_discovery=False)


def channel_videos(yt) -> tuple[str, list[dict]]:
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        res = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50,
                                      pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in res.get("items", [])]
        token = res.get("nextPageToken")
        if not token or len(ids) >= 200:
            break
    videos = []
    for chunk in (ids[i:i + 50] for i in range(0, len(ids), 50)):
        res = yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(chunk)).execute()
        for v in res.get("items", []):
            videos.append({"id": v["id"], "title": v["snippet"]["title"],
                           "published": v["snippet"]["publishedAt"], "privacy": v["status"]["privacyStatus"],
                           "duration": v["contentDetails"]["duration"],
                           "views": int(v["statistics"].get("viewCount", 0)),
                           "likes": int(v["statistics"].get("likeCount", 0)),
                           "comments": int(v["statistics"].get("commentCount", 0))})
    return ch["id"], videos


# ---------- yt-retention ----------

def retention(videos: list[dict]) -> tuple[list[dict], str | None]:
    eligible = [v for v in videos if v["privacy"] == "public" and v["views"] >= RETENTION_MIN_VIEWS][:10]
    if not eligible:
        return [], "sleeping: no public video has 200+ views yet"
    try:
        ya = service("youtubeAnalytics", "v2", ["https://www.googleapis.com/auth/yt-analytics.readonly"])
    except Exception as exc:
        return [], f"cannot start Analytics: {exc}"
    out = []
    for v in eligible:
        try:
            res = ya.reports().query(ids="channel==MINE", startDate=v["published"][:10],
                                     endDate=date.today().isoformat(), dimensions="elapsedVideoTimeRatio",
                                     metrics="audienceWatchRatio", filters=f"video=={v['id']}").execute()
        except Exception as exc:
            if "insufficient" in str(exc).lower() or "403" in str(exc):
                return [], "needs the yt-analytics.readonly permission (one-time step), sleeping"
            continue
        rows = res.get("rows", [])
        if len(rows) < 8:
            continue
        path = DATA / f"retention_{v['id']}.csv"
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["position", "watching"])
            w.writerows([[round(r[0] * 100, 1), round(r[1] * 100, 1)] for r in rows])
        report = tool("yt-retention", "retention.py", str(path))
        if report:
            out.append({"video": v["title"], "views": v["views"], "report": report})
    return out, None if out else "sleeping: no retention data yet"


# ---------- yt-comment ----------

def comments(yt, channel_id: str) -> list[dict]:
    res = yt.commentThreads().list(part="snippet", allThreadsRelatedToChannelId=channel_id,
                                   maxResults=100, order="time").execute()
    out = []
    for t in res.get("items", []):
        top = t["snippet"]["topLevelComment"]["snippet"]
        if t["snippet"].get("totalReplyCount", 0) == 0:
            out.append({"thread_id": t["id"], "author": top.get("authorDisplayName", ""),
                        "text": top.get("textOriginal", "")[:500], "likes": top.get("likeCount", 0),
                        "video_id": t["snippet"].get("videoId", "")})
    return out


# ---------- report ----------

def main() -> None:
    DATA.mkdir(exist_ok=True)
    yt = service("youtube", "v3", ["https://www.googleapis.com/auth/youtube.readonly"])
    channel_id, videos = channel_videos(yt)
    public = [v for v in videos if v["privacy"] == "public"]
    report = [f"# 📅 NBA Rumors weekly report, {date.today().isoformat()}", "",
              f"Channel: {len(videos)} videos ({len(public)} public)", ""]

    # yt-retention first: its lessons feed the plan
    lessons, why = retention(videos)
    report += ["## 📉 yt-retention", ""]
    if lessons:
        fix = claude("yt-retention", "From these retention reports, list what to change in our scripts "
                     'and pacing. Return {"findings": ["..."], "change_next_week": ["..."]}',
                     json.dumps(lessons, indent=1))
        report += [f"- {x}" for x in fix.get("findings", [])] + ["", "**Change next week:**"]
        report += [f"- {x}" for x in fix.get("change_next_week", [])]
    else:
        report.append(f"_{why}_")
        fix = {}

    # yt-audit
    report += ["", "## 🩺 yt-audit", ""]
    if len(public) >= AUDIT_MIN_VIDEOS:
        audit = claude("yt-audit", "Audit the channel from these videos (titles, length, views, likes, "
                       "comments). Return {\"verdict\": \"...\", \"fix_first\": [\"...\"], \"keep\": [\"...\"]}",
                       json.dumps(public[:60], indent=1))
        report += [f"**Verdict:** {audit.get('verdict', '')}", "", "**Fix first:**"]
        report += [f"- {x}" for x in audit.get("fix_first", [])] + ["", "**Keep doing:**"]
        report += [f"- {x}" for x in audit.get("keep", [])]
    else:
        audit = {}
        report.append(f"_sleeping: {len(public)}/{AUDIT_MIN_VIDEOS} public videos_")

    # yt-comment: switched off by the owner's choice. To turn it on later, set the repository
    # variable COMMENTS=on (Settings > Secrets and variables > Actions > Variables).
    if os.environ.get("COMMENTS", "off").lower() == "on":
        report += ["", "## 💬 yt-comment", ""]
        try:
            threads = comments(yt, channel_id) if public else []
        except Exception as exc:
            threads, report = [], report + [f"_comments unavailable: {exc}_"]
        if threads:
            drafts = claude("yt-comment", "Triage these comments (reply / like only / ignore / hide). Draft a "
                            "short reply in the channel voice for the ones worth answering. No pet names, no "
                            "flirting, never argue, never invent facts. Return {\"drafts\": [{\"thread_id\": "
                            "\"...\", \"comment\": \"...\", \"triage\": \"reply\", \"reply\": \"...\"}]}",
                            json.dumps(threads[:80], indent=1)).get("drafts", [])
            for d in [d for d in drafts if d.get("triage") == "reply"][:30]:
                report.append(f"- **{d.get('comment', '')[:120]}**  \n  ↳ {d.get('reply', '')}")

    # yt-plan (always)
    topics = json.loads((DATA / "topics.json").read_text()) if (DATA / "topics.json").exists() else []
    plan = claude("yt-plan",
                  "Plan next week for NBA Rumors. Capacity: 3 Shorts a day (automatic) and 2 long videos "
                  "(8-10 min) a week. Drama and intrigue first, but the biggest viral stories always get in. "
                  "Use the stories and audience signals below, and the retention/audit lessons if any. "
                  "Plan themes, not invented facts: news decides the exact stories each day. "
                  'Return {"focus": "...", "long_videos": [{"day": "Tue", "title_idea": "...", "angle": "..."}], '
                  '"shorts_themes": ["..."], "series": ["..."], "experiments": ["..."]}',
                  json.dumps({"stories": [{"headline": t["headline"], "youtube_heat": t.get("youtube_heat", 0),
                                           "search_hits": t.get("search_hits", 0)} for t in topics[:25]],
                              "retention_lessons": fix, "audit": audit,
                              "recent_videos": public[:20]}, indent=1))
    plan["week_of"] = date.today().isoformat()
    PLAN.parent.mkdir(exist_ok=True)
    PLAN.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    report += ["", "## 🗓️ yt-plan: next week", "", f"**Focus:** {plan.get('focus', '')}", ""]
    report += [f"- {l.get('day', '')}: **{l.get('title_idea', '')}** ({l.get('angle', '')})"
               for l in plan.get("long_videos", [])]
    report += ["", "**Shorts themes:** " + ", ".join(plan.get("shorts_themes", [])),
               "**Experiments:** " + ", ".join(plan.get("experiments", []))]

    text = "\n".join(report)
    summary(f"Weekly report {date.today().isoformat()} saved to the private state repository "
            f"(nba/history/reports/). Not shown here: this repository is public.")
    # private: saved to the private state repository (state.py save), never a public GitHub Issue
    reports = DATA / "history" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"weekly_{date.today().isoformat()}.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
