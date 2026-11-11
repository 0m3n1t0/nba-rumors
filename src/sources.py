"""NBA news sources (RSS feeds).

Each source has a trust tier:
  1 = major outlet / established NBA insider reporting (can carry a rumor on its own)
  2 = aggregator or secondary outlet (needs a tier 1 confirmation for rumors)

Google News searches act as a wide net: they pull headlines from hundreds of
outlets, and the real publisher name is read from each item.
"""

GOOGLE_NEWS = "https://news.google.com/rss/search?q={q}+when:1d&hl=en-US&gl=US&ceid=US:en"

FEEDS = [
    # Direct outlet feeds
    {"name": "ESPN", "url": "https://www.espn.com/espn/rss/nba/news", "tier": 1},
    {"name": "CBS Sports", "url": "https://www.cbssports.com/rss/headlines/nba/", "tier": 1},
    {"name": "Yahoo Sports", "url": "https://sports.yahoo.com/nba/rss/", "tier": 1},
    {"name": "HoopsHype", "url": "https://hoopshype.com/feed/", "tier": 2},
    {"name": "RealGM", "url": "https://basketball.realgm.com/rss/wiretap/0/0.xml", "tier": 2},
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
]

# Publishers found inside Google News items that count as tier 1.
TIER1_PUBLISHERS = {
    "espn", "the athletic", "nytimes", "new york times", "yahoo sports", "cbs sports",
    "bleacher report", "the ringer", "associated press", "ap news", "nba.com",
    "sports illustrated", "usa today", "fox sports", "nbc sports",
    "the stein line", "marc stein", "reuters",
}
