import json, os, time, hashlib
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

RSS_FEEDS = [
    # War / Conflict
    ("https://feeds.reuters.com/reuters/topNews", "Reuters", "War"),
    ("https://feeds.bbci.co.uk/news/world/rss.xml", "BBC", "War"),
    ("https://www.aljazeera.com/xml/rss/all.xml", "AlJazeera", "War"),
    ("https://rss.dw.com/rdf/rss-en-world", "DW", "War"),
    ("https://feeds.npr.org/1004/rss.xml", "NPR World", "War"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "NYT World", "War"),
    ("https://feeds.washingtonpost.com/rss/world", "WashPost", "War"),
    ("https://www.theguardian.com/world/rss", "Guardian", "War"),
    ("https://www.independent.co.uk/news/world/rss", "Independent", "War"),
    ("https://feeds.skynews.com/feeds/rss/world.xml", "SkyNews", "War"),
    # Economy
    ("https://feeds.reuters.com/reuters/businessNews", "Reuters Biz", "Economy"),
    ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg", "Economy"),
    ("https://www.ft.com/rss/home", "FT", "Economy"),
    ("https://feeds.marketwatch.com/marketwatch/topstories", "MarketWatch", "Economy"),
    ("https://finance.yahoo.com/news/rssindex", "Yahoo Finance", "Economy"),
    ("https://feeds.cnbc.com/cnbc/ID/100003114/device/rss/rss.html", "CNBC", "Economy"),
    ("https://www.wsj.com/xml/rss/3_7085.xml", "WSJ Economy", "Economy"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "NYT Economy", "Economy"),
    # Politics
    ("https://feeds.reuters.com/Reuters/PoliticsNews", "Reuters Politics", "Politics"),
    ("https://rss.politico.com/politics-news.xml", "Politico", "Politics"),
    ("https://feeds.npr.org/1014/rss.xml", "NPR Politics", "Politics"),
    ("https://www.foreignpolicy.com/feed", "ForeignPolicy", "Politics"),
    ("https://feeds.washingtonpost.com/rss/politics", "WashPost Politics", "Politics"),
    ("https://www.cfr.org/rss.xml", "CFR", "Politics"),
    ("https://www.economist.com/international/rss.xml", "Economist", "Politics"),
    ("https://asia.nikkei.com/rss/feed/nar", "Nikkei Asia", "Politics"),
    ("https://www.scmp.com/rss/91/feed", "SCMP", "Politics"),
    ("https://koreajoongangdaily.joins.com/rss/feed", "Korea JoongAng", "Politics"),
]

IMPACT_TERMS = {
    10: ["nuclear", "invasion", "world war", "default", "collapse", "war declared", "genocide"],
    9:  ["emergency", "crisis", "missile strike", "sanctions", "rate hike", "rate cut", "coup", "assassination"],
    8:  ["escalation", "airstrike", "resignation", "shutdown", "market crash", "recession"],
    7:  ["tension", "military", "protest", "summit", "election", "tariff"],
    6:  ["warning", "talks", "sanction", "conflict", "inflation"],
}

KEYWORDS = {
    "War": ["war", "military", "strike", "missile", "bomb", "attack", "invasion", "troops", "combat", "shelling", "ceasefire", "conflict", "weapon", "artillery", "drone", "explosion", "killed", "casualties"],
    "Economy": ["inflation", "rate", "recession", "gdp", "fed", "ecb", "default", "market", "stock", "bond", "trade", "tariff", "sanction", "bank", "currency", "oil", "commodity"],
    "Politics": ["election", "president", "minister", "parliament", "vote", "coup", "resign", "summit", "diplomacy", "treaty", "sanction", "congress", "senate", "nato", "un"],
}

CITY_MAP = {
    "moscow": (55.7558, 37.6173), "kyiv": (50.4501, 30.5234), "kiev": (50.4501, 30.5234),
    "beijing": (39.9042, 116.4074), "washington": (38.8951, -77.0364),
    "tokyo": (35.6762, 139.6503), "london": (51.5074, -0.1278),
    "seoul": (37.5665, 126.9780), "shanghai": (31.2304, 121.4737),
    "tel aviv": (32.0853, 34.7818), "gaza": (31.9250, 35.2028),
    "jerusalem": (31.7683, 35.2137), "baghdad": (33.3128, 44.3615),
    "tehran": (35.6892, 51.3890), "taipei": (25.0330, 121.5654),
    "hong kong": (22.3193, 114.1694), "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025), "paris": (48.8566, 2.3522),
    "berlin": (52.5200, 13.4050), "new york": (40.7128, -74.0060),
    "dubai": (25.2048, 55.2708), "singapore": (1.3521, 103.8198),
    "sydney": (-33.8688, 151.2093), "ankara": (39.9334, 32.8597),
    "istanbul": (41.0082, 28.9784), "cairo": (30.0444, 31.2357),
    "riyadh": (24.7136, 46.6753), "brussels": (50.8503, 4.3517),
    "rome": (41.9028, 12.4964), "madrid": (40.4168, -3.7038),
    "warsaw": (52.2297, 21.0122), "kyiv": (50.4501, 30.5234),
    "beijing": (39.9042, 116.4074), "pyongyang": (39.0194, 125.7381),
    "manila": (14.5995, 120.9842), "jakarta": (-6.2088, 106.8456),
    "bangkok": (13.7563, 100.5018), "hanoi": (21.0285, 105.8542),
    "kabul": (34.5253, 69.1783), "islamabad": (33.6844, 73.0479),
    "new delhi": (28.6139, 77.2090), "nairobi": (-1.2921, 36.8219),
    "accra": (5.6037, -0.1870), "pretoria": (-25.7479, 28.2293),
    "brasilia": (-15.7975, -47.8919), "ottawa": (45.4215, -75.6972),
    "canberra": (-35.2809, 149.1300), "vienna": (48.2082, 16.3738),
}

def make_id(*parts):
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]

def score_impact(text):
    t = text.lower()
    for score in sorted(IMPACT_TERMS, reverse=True):
        if any(term in t for term in IMPACT_TERMS[score]):
            return score
    return 5

def detect_category(text, default_cat):
    t = text.lower()
    scores = {cat: sum(1 for kw in kws if kw in t) for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default_cat

def extract_locations(text):
    t = text.lower()
    found = []
    for city, coords in CITY_MAP.items():
        if city in t:
            found.append((city.title(), coords[0], coords[1]))
    return found

def fetch_rss(url, source, default_cat):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"}
    items = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            root = ET.fromstring(r.read())
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for entry in entries[:20]:
            title = (entry.findtext("title") or entry.findtext("atom:title", namespaces=ns) or "").strip()
            desc = (entry.findtext("description") or entry.findtext("atom:summary", namespaces=ns) or "").strip()
            pub = entry.findtext("pubDate") or entry.findtext("atom:published", namespaces=ns) or ""
            link = entry.findtext("link") or entry.findtext("atom:link", namespaces=ns) or ""
            if not title:
                continue
            full = f"{title} {desc}"
            items.append({"title": title[:200], "full": full, "pub": pub, "link": link, "source": source, "cat": default_cat})
    except Exception as e:
        print(f"⚠ RSS {source}: {e}")
    return items

def parse_time(pub):
    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"]:
        try:
            from datetime import timezone
            dt = datetime.strptime(pub.strip(), fmt)
            return int(dt.timestamp())
        except:
            continue
    return int(time.time())

def main():
    all_events = []
    seen = set()
    
    for url, source, default_cat in RSS_FEEDS:
        print(f"Fetching {source}...")
        items = fetch_rss(url, source, default_cat)
        
        for item in items:
            text = item["full"]
            locs = extract_locations(text)
            if not locs:
                continue
            
            cat = detect_category(text, item["cat"])
            impact = score_impact(text)
            
            for city, lat, lng in locs[:2]:
                eid = make_id(source, city, item["title"][:30])
                if eid in seen:
                    continue
                seen.add(eid)
                
                all_events.append({
                    "id": eid,
                    "title": item["title"],
                    "lat": lat,
                    "lng": lng,
                    "category": cat,
                    "impact_score": impact,
                    "source": source,
                    "url": item["link"],
                    "ts": parse_time(item["pub"]),
                })
        
        time.sleep(0.3)
    
    all_events.sort(key=lambda x: x["ts"], reverse=True)
    all_events = all_events[:500]
    
    os.makedirs("docs", exist_ok=True)
    output = {"updated": datetime.utcnow().isoformat(), "total": len(all_events), "events": all_events}
    
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(all_events)}개 이벤트 저장 완료")

if __name__ == "__main__":
    main()
