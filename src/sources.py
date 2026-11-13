"""NBA news sources (RSS feeds).

Each source has a trust tier:
  1 = major outlet / established NBA insider reporting (can carry a rumor on its own)
  2 = aggregator or secondary outlet (needs a tier 1 confirmation for rumors)

Google News searches act as a wide net: they pull headlines from hundreds of
outlets, and the real publisher name is read from each item.
"""

# "when:1d" FIRST: at the end, after a "-word" exclusion, Google ignored it (2026-11-13: the
# podcast search returned 39 items, all from May, so every one was dropped as too old)
GOOGLE_NEWS = "https://news.google.com/rss/search?q=when:1d+{q}&hl=en-US&gl=US&ceid=US:en"

FEEDS = [
    # Direct outlet feeds
    # "fallback": the same outlet through Google News, used when its own feed gives nothing (ESPN's
    # feed gave 0 items on GitHub's servers in every run, 17 from elsewhere; HoopsHype's feed now
    # answers 402 Payment Required)
    {"name": "ESPN", "url": "https://www.espn.com/espn/rss/nba/news", "tier": 1,
     "fallback": GOOGLE_NEWS.format(q="site:espn.com/nba")},
    {"name": "CBS Sports", "url": "https://www.cbssports.com/rss/headlines/nba/", "tier": 1},
    {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/nba/rss/", "tier": 1},
    {"name": "HoopsHype", "url": "https://hoopshype.com/feed/", "tier": 2,
     "fallback": GOOGLE_NEWS.format(q="site:hoopshype.com+NBA")},
    {"name": "RealGM", "url": "https://basketball.realgm.com/rss/wiretap/0/0.xml", "tier": 2},
    # Added 2026-11-13 (the owner's source review; each answered GitHub's servers, run 43441957341).
    # "filter": the feed covers other sports too, so only clearly NBA items are kept.
    {"name": "ClutchPoints", "url": "https://clutchpoints.com/nba/feed", "tier": 2,
     "fallback": GOOGLE_NEWS.format(q="site:clutchpoints.com+NBA")},
    {"name": "Hoops Rumors", "url": "https://www.hoopsrumors.com/feed", "tier": 2},
    {"name": "SB Nation", "url": "https://www.sbnation.com/rss/nba/index.xml", "tier": 2},
    {"name": "Defector", "url": "https://defector.com/feed", "tier": 2, "filter": True},
    {"name": "TrueHoop", "url": "https://www.truehoop.com/feed", "tier": 2},
    # Google News searches (wide net, last 24 hours)
    {"name": "GN: trade rumors", "url": GOOGLE_NEWS.format(q="NBA+trade+rumors"), "tier": 2},
    {"name": "GN: injury", "url": GOOGLE_NEWS.format(q="NBA+injury+update"), "tier": 2},
    {"name": "GN: drama", "url": GOOGLE_NEWS.format(q="NBA+drama+OR+feud+OR+locker+room"), "tier": 2},
    {"name": "GN: free agency", "url": GOOGLE_NEWS.format(q="NBA+free+agency+OR+contract+extension"), "tier": 2},
    {"name": "GN: fired coach", "url": GOOGLE_NEWS.format(q="NBA+coach+fired+OR+suspended+OR+fined"), "tier": 2},
    # Drama and intrigue: the channel's main focus
    {"name": "GN: trade request", "url": GOOGLE_NEWS.format(q="NBA+%22trade+request%22+OR+%22wants+out%22+OR+%22requests+trade%22"), "tier": 2},
    {"name": "GN: beef", "url": GOOGLE_NEWS.format(q="NBA+beef+OR+%22calls+out%22+OR+%22fires+back%22+OR+%22responds+to%22"), "tier": 2},
    {"name": "GN: rift", "url": GOOGLE_NEWS.format(q="NBA+rift+OR+tension+OR+frustrated+OR+unhappy"), "tier": 2},
    {"name": "GN: ejected", "url": GOOGLE_NEWS.format(q="NBA+ejected+OR+altercation+OR+scuffle+OR+technical"), "tier": 2},
    {"name": "GN: front office", "url": GOOGLE_NEWS.format(q="NBA+%22front+office%22+OR+owner+OR+GM+controversy"), "tier": 2},
    {"name": "GN: investigation", "url": GOOGLE_NEWS.format(q="NBA+investigation+OR+%22league+office%22+OR+punishment"), "tier": 2},
    # C3 (owner's plan, 2026-11-11): podcasts and interviews, where many beefs start. Articles
    # about what was said on a show (free, readable, verifiable); never the audio or video.
    {"name": "GN: podcasts", "url": GOOGLE_NEWS.format(q="NBA+(%22All+the+Smoke%22+OR+%22Draymond+Green+Show%22+OR+%22Club+520%22+OR+%22Knuckleheads%22+OR+%22Old+Man+and+the+Three%22+OR+%22Gil%27s+Arena%22+OR+%22Podcast+P%22+OR+%22The+Pivot%22+OR+%22Mind+the+Game%22+OR+%22Road+Trippin%22)+-odds+-prediction"), "tier": 2},
    {"name": "GN: podcast clash", "url": GOOGLE_NEWS.format(q="NBA+podcast+(slams+OR+rips+OR+%22calls+out%22+OR+%22fires+back%22+OR+feud+OR+beef+OR+%22goes+off%22)+-odds"), "tier": 2},
    # Categories the searches above missed (2026-11-13, each measured: 10-13 new headlines a day,
    # e.g. Chris Bosh tied to an arson case, a Bucks tax-evasion report, Embiid "trolls")
    {"name": "GN: statements", "url": GOOGLE_NEWS.format(q="NBA+(%22speaks+out%22+OR+reveals+OR+admits+OR+%22opens+up%22+OR+%22tells+all%22)"), "tier": 2},
    {"name": "GN: scandal", "url": GOOGLE_NEWS.format(q="NBA+(scandal+OR+allegations+OR+misconduct+OR+lawsuit+OR+controversy)"), "tier": 2},
    {"name": "GN: vs coach or teammate", "url": GOOGLE_NEWS.format(q="NBA+(%22calls+out+coach%22+OR+%22criticizes+coach%22+OR+%22rips+coach%22+OR+%22calls+out+teammate%22+OR+benched)"), "tier": 2},
    {"name": "GN: viral", "url": GOOGLE_NEWS.format(q="NBA+(viral+OR+bizarre+OR+wild+OR+%22caught+on+camera%22+OR+trolls)"), "tier": 2},
    {"name": "GN: insiders", "url": GOOGLE_NEWS.format(q="NBA+(Shams+OR+Windhorst+OR+%22Chris+Haynes%22+OR+%22Marc+Stein%22+OR+%22Jake+Fischer%22+OR+%22Ramona+Shelburne%22+OR+%22Chris+Broussard%22)"), "tier": 2},
] + [
    # Podcast and show channels on YouTube (public RSS, free, no quota): the episode TITLES are a
    # beef radar ("Draymond Green Claps Back at Doc Rivers"); the story itself still comes from
    # articles (C3: never the audio or the video). Channel ids checked 2026-11-13.
    {"name": f"{show} (podcast)", "url": f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}",
     "tier": 2, "filter": True, "video": True}
    for show, cid in [("All the Smoke", "UC2ozVs4pg2K3uFLw6-0ayCQ"), ("Club 520", "UCoA3lm9UTWDWK8Z1kcoWQcA"),
                      ("Gil's Arena", "UCAvjYgmwadC682OoC4Cc6TQ"), ("The Draymond Green Show", "UCBNqqomXKPSWvcQDXOkRvRA"),
                      ("Pablo Torre Finds Out", "UCx3FZj77zMjFP4K_ig6dvnA"), ("The Old Man and the Three", "UCbPY1Efha9VPRBYW2x1M16A"),
                      ("Dan Patrick Show", "UCORy0Yqzd8bVj2Gb4xyq6HA")]
]

# Publishers found inside Google News items that count as tier 1.
TIER1_PUBLISHERS = {
    "espn", "the athletic", "nytimes", "new york times", "yahoo sports", "cbs sports",
    "bleacher report", "the ringer", "associated press", "ap news", "nba.com",
    "sports illustrated", "usa today", "fox sports", "nbc sports",
    "the stein line", "marc stein", "reuters",
}
