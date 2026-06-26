import asyncio, json, os
from datetime import datetime
from pyrogram import Client

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION = "anon"

CHANNELS = [
    "@liveuamap", "@wartranslated", "@rybar", "@militarylandnet",
    "@conflictforensics", "@GeoConfirmed", "@FrontoVsUA", "@ISWresearch",
    "@SouthFrontEN", "@CoalitionNews", "@mod_russia_en", "@DefenseMinistryUA",
    "@OSINT_RESEARCH", "@Slavyangrad", "@Artelenka_EN", "@MotolkoHelp",
    "@NOABBmapper", "@type_95_tank", "@Topografist", "@WarTranslated",
    "@RusWarMap", "@Geolocation_N", "@HotlineHeadquarters", "@mariupol_now",
    "@CensorNet", "@moklasen", "@Andriy_Dubov", "@TelecomDoctrine",
    "@ReutersLive", "@Reuters", "@Bloomberg", "@FT",
    "@YahooFinance", "@CNBC", "@WSJ", "@MarketWatch",
    "@ECB", "@FederalReserve", "@bankofengland", "@BoJ_en",
    "@BankofKorea", "@InvestorsDaily", "@DeItaliaBanca",
    "@BBCNews", "@AP", "@AFP", "@DW_News",
    "@EURACTIV_EN", "@GlobalTimes_CN", "@chinadailyusa", "@NHK_WORLD",
    "@YonhapNews_en", "@ArirangNewsTV", "@kbsworld",
    "@UN", "@WhiteHouse", "@StateDept", "@UKForeignOffice",
    "@TechCrunch", "@cnbc_tv", "@ZeroHedge",
]

KEYWORDS = {
    "War": ["strike", "missile", "shelling", "bombing", "invasion", "military", "combat", "attack", "offensive", "ceasefire", "evacuation", "casualty", "drone", "artillery", "tank", "battalion", "regiment", "frontline"],
    "Economy": ["rate", "inflation", "recession", "gdp", "interest", "fed", "ecb", "default", "crisis", "market", "stock", "crypto", "oil", "commodity", "export", "import", "tariff", "sanction"],
    "Politics": ["election", "summit", "meeting", "diplomacy", "negotiation", "vote", "parliament", "congress", "minister", "president", "sanctions", "treaty", "coup", "resign"],
}

def extract_category(text):
    t = text.lower()
    scores = {}
    for cat, kws in KEYWORDS.items():
        scores[cat] = sum(1 for kw in kws if kw.lower() in t)
    return max(scores, key=scores.get) if max(scores.values()) > 0 else None

def extract_locations(text):
    major_cities = {
        "Moscow": (55.7558, 37.6173), "Kyiv": (50.4501, 30.5234),
        "Beijing": (39.9042, 116.4074), "Washington": (38.8951, -77.0364),
        "Tokyo": (35.6762, 139.6503), "London": (51.5074, -0.1278),
        "Seoul": (37.5665, 126.9780), "Shanghai": (31.2304, 121.4737),
        "Tel Aviv": (32.0853, 34.7818), "Gaza": (31.9250, 35.2028),
        "Baghdad": (33.3128, 44.3615), "Tehran": (35.6892, 51.3890),
        "Taipei": (25.0330, 121.5654), "Hong Kong": (22.3193, 114.1694),
        "Mumbai": (19.0760, 72.8777), "Delhi": (28.7041, 77.1025),
        "Paris": (48.8566, 2.3522), "Berlin": (52.5200, 13.4050),
        "New York": (40.7128, -74.0060), "Dubai": (25.2048, 55.2708),
        "Singapore": (1.3521, 103.8198), "Sydney": (-33.8688, 151.2093),
    }
    locs = []
    for city, (lat, lng) in major_cities.items():
        if city.lower() in text.lower():
            locs.append((city, lat, lng))
    return locs

async def fetch_channel_messages(client, channel, limit=20):
    messages = []
    try:
        async for msg in client.get_chat_history(channel, limit=limit):
            if msg.text:
                messages.append({"text": msg.text[:300], "channel": channel, "timestamp": int(msg.date.timestamp())})
    except Exception as e:
        print(f"Channel {channel} error: {e}")
    await asyncio.sleep(0.5)
    return messages

async def main():
    print(f"API_ID: {API_ID}")
    print(f"API_HASH: {API_HASH[:10]}...")
    
    if not API_HASH or API_ID == 0:
        print("ERROR: Set TELEGRAM_API_ID & TELEGRAM_API_HASH")
        return False
    
    try:
        client = Client(SESSION, API_ID, API_HASH, no_updates=True)
        async with client:
            all_events = []
            print(f"Monitoring {len(CHANNELS)} channels...")
            
            tasks = [fetch_channel_messages(client, ch, limit=15) for ch in CHANNELS]
            results = await asyncio.gather(*tasks)
            
            seen = set()
            for msgs in results:
                for msg in msgs:
                    text = msg["text"]
                    cat = extract_category(text)
                    if not cat:
                        continue
                    
                    locs = extract_locations(text)
                    if not locs:
                        continue
                    
                    for city, lat, lng in locs:
                        event_id = f"{msg['channel']}-{round(lat,2)}-{text[:20]}"
                        if event_id in seen:
                            continue
                        seen.add(event_id)
                        
                        keywords_hit = sum(1 for kw in KEYWORDS[cat] if kw.lower() in text.lower())
                        impact = min(10, 5 + keywords_hit)
                        
                        all_events.append({
                            "id": event_id[:40],
                            "title": text,
                            "lat": lat,
                            "lng": lng,
                            "category": cat,
                            "impact_score": impact,
                            "source": msg["channel"],
                            "ts": msg["timestamp"],
                        })
            
            all_events.sort(key=lambda x: x["ts"], reverse=True)
            all_events = all_events[:500]
            
            output = {"updated": datetime.utcnow().isoformat(), "total": len(all_events), "events": all_events}
            
            import os
            os.makedirs("docs", exist_ok=True)
            with open("docs/data.json", "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"SUCCESS: {len(all_events)} events saved")
            return True
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
