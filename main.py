import json, os, time, hashlib, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    ("https://feeds.bbci.co.uk/news/world/rss.xml", "BBC", "War"),
    ("https://feeds.bbci.co.uk/news/business/rss.xml", "BBC Biz", "Economy"),
    ("https://rss.dw.com/rdf/rss-en-world", "DW", "War"),
    ("https://www.aljazeera.com/xml/rss/all.xml", "AlJazeera", "War"),
    ("https://feeds.npr.org/1004/rss.xml", "NPR", "Politics"),
    ("https://www.theguardian.com/world/rss", "Guardian", "War"),
    ("https://feeds.skynews.com/feeds/rss/world.xml", "SkyNews", "War"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "NYT", "War"),
    ("https://feeds.washingtonpost.com/rss/world", "WashPost", "War"),
    ("https://www.ft.com/rss/home", "FT", "Economy"),
    ("https://feeds.marketwatch.com/marketwatch/topstories", "MarketWatch", "Economy"),
    ("https://finance.yahoo.com/news/rssindex", "Yahoo Finance", "Economy"),
    ("https://www.economist.com/international/rss.xml", "Economist", "Politics"),
    ("https://asia.nikkei.com/rss/feed/nar", "Nikkei", "Economy"),
    ("https://www.foreignpolicy.com/feed", "ForeignPolicy", "Politics"),
    ("https://www.cfr.org/rss.xml", "CFR", "Politics"),
    ("https://feeds.reuters.com/reuters/topNews", "Reuters", "War"),
    ("https://feeds.reuters.com/reuters/businessNews", "Reuters Biz", "Economy"),
    ("https://feeds.reuters.com/Reuters/PoliticsNews", "Reuters Politics", "Politics"),
]

CITIES = {
    "moscow":(55.7558,37.6173), "kyiv":(50.4501,30.5234), "kiev":(50.4501,30.5234),
    "beijing":(39.9042,116.4074), "washington":(38.8951,-77.0364),
    "tokyo":(35.6762,139.6503), "london":(51.5074,-0.1278),
    "seoul":(37.5665,126.9780), "shanghai":(31.2304,121.4737),
    "tel aviv":(32.0853,34.7818), "gaza":(31.9250,35.2028),
    "jerusalem":(31.7683,35.2137), "baghdad":(33.3128,44.3615),
    "tehran":(35.6892,51.3890), "taipei":(25.0330,121.5654),
    "hong kong":(22.3193,114.1694), "paris":(48.8566,2.3522),
    "berlin":(52.5200,13.4050), "new york":(40.7128,-74.0060),
    "dubai":(25.2048,55.2708), "singapore":(1.3521,103.8198),
    "ankara":(39.9334,32.8597), "istanbul":(41.0082,28.9784),
    "cairo":(30.0444,31.2357), "riyadh":(24.7136,46.6753),
    "brussels":(50.8503,4.3517), "rome":(41.9028,12.4964),
    "madrid":(40.4168,-3.7038), "warsaw":(52.2297,21.0122),
    "pyongyang":(39.0194,125.7381), "manila":(14.5995,120.9842),
    "jakarta":(-6.2088,106.8456), "bangkok":(13.7563,100.5018),
    "islamabad":(33.6844,73.0479), "kabul":(34.5253,69.1783),
    "nairobi":(-1.2921,36.8219), "brasilia":(-15.7975,-47.8919),
    "ottawa":(45.4215,-75.6972), "canberra":(-35.2809,149.1300),
    "vienna":(48.2082,16.3738), "kiev":(50.4501,30.5234),
    "mumbai":(19.0760,72.8777), "delhi":(28.7041,77.1025),
    "new delhi":(28.6139,77.2090), "sydney":(-33.8688,151.2093),
}

IMPACT = {
    10:["nuclear","world war","invasion","genocide","collapse"],
    9:["emergency","coup","assassination","missile strike","rate hike","rate cut","default"],
    8:["airstrike","escalation","resignation","market crash","recession","sanctions"],
    7:["military","summit","election","protest","tariff","conflict"],
    6:["warning","tension","talks","inflation"],
}

KW = {
    "War":["war","military","strike","missile","bomb","attack","invasion","troops","combat","shelling","ceasefire","conflict","weapon","killed","casualties","drone","explosion"],
    "Economy":["inflation","rate","recession","gdp","fed","ecb","default","market","stock","trade","tariff","sanction","bank","currency","oil","commodity","crypto"],
    "Politics":["election","president","minister","parliament","vote","coup","resign","summit","diplomacy","treaty","nato","congress","senate"],
}

def make_id(*p): return hashlib.sha1("|".join(str(x) for x in p).encode()).hexdigest()[:16]

def score(text):
    t = text.lower()
    for s in sorted(IMPACT, reverse=True):
        if any(w in t for w in IMPACT[s]): return s
    return 5

def category(text, default):
    t = text.lower()
    s = {c: sum(1 for w in KW[c] if w in t) for c in KW}
    best = max(s, key=s.get)
    return best if s[best] > 0 else default

def locations(text):
    t = text.lower()
    return [(c.title(), *v) for c,v in CITIES.items() if c in t]

def parse_ts(s):
    if not s: return int(time.time())
    for fmt in ["%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S GMT","%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%M:%S%z"]:
        try: return int(datetime.strptime(s.strip(), fmt).timestamp())
        except: pass
    return int(time.time())

def fetch(url, source, default_cat):
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"NewsBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            root = ET.fromstring(r.read())
        for item in (root.findall(".//item") or [])[:15]:
            t = (item.findtext("title") or "").strip()
            d = (item.findtext("description") or "").strip()
            if not t: continue
            out.append({
                "title": t[:200],
                "full": f"{t} {d}",
                "pub": item.findtext("pubDate") or "",
                "link": item.findtext("link") or "",
                "source": source,
                "cat": default_cat,
            })
    except Exception as e:
        print(f"SKIP {source}: {e}")
    return out

def main():
    events, seen = [], set()
    for url, source, cat in FEEDS:
        print(f"→ {source}")
        for item in fetch(url, source, cat):
            locs = locations(item["full"])
            if not locs: continue
            cat2 = category(item["full"], item["cat"])
            imp = score(item["full"])
            for city, lat, lng in locs[:2]:
                eid = make_id(source, city, item["title"][:30])
                if eid in seen: continue
                seen.add(eid)
                events.append({
                    "id": eid, "title": item["title"],
                    "lat": lat, "lng": lng,
                    "category": cat2, "impact_score": imp,
                    "source": source, "url": item["link"],
                    "ts": parse_ts(item["pub"]),
                })
        time.sleep(0.2)

    events.sort(key=lambda x: x["ts"], reverse=True)
    events = events[:500]
    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.utcnow().isoformat(), "total": len(events), "events": events}, f, ensure_ascii=False)
    print(f"✅ {len(events)} events")

main()
