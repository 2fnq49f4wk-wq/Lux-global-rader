import json, os, time, hashlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime

FEEDS = [
    ("https://feeds.bbci.co.uk/news/world/rss.xml","BBC","War"),
    ("https://feeds.bbci.co.uk/news/business/rss.xml","BBC Biz","Economy"),
    ("https://rss.dw.com/rdf/rss-en-world","DW","War"),
    ("https://www.aljazeera.com/xml/rss/all.xml","AlJazeera","War"),
    ("https://feeds.npr.org/1004/rss.xml","NPR","Politics"),
    ("https://www.theguardian.com/world/rss","Guardian","War"),
    ("https://feeds.skynews.com/feeds/rss/world.xml","SkyNews","War"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml","NYT","War"),
    ("https://www.ft.com/rss/home","FT","Economy"),
    ("https://feeds.marketwatch.com/marketwatch/topstories","MarketWatch","Economy"),
    ("https://finance.yahoo.com/news/rssindex","Yahoo","Economy"),
    ("https://www.economist.com/international/rss.xml","Economist","Politics"),
    ("https://asia.nikkei.com/rss/feed/nar","Nikkei","Economy"),
    ("https://moxie.foxnews.com/google-publisher/world.xml","Fox","War"),
    ("https://feeds.a.dj.com/rss/RSSWorldNews.xml","WSJ World","War"),
    ("https://feeds.content.dowjones.io/public/rss/RSSMarketsMain","WSJ Markets","Economy"),
    ("https://www.cbsnews.com/latest/rss/world","CBS","War"),
    ("https://abcnews.go.com/abcnews/internationalheadlines","ABC","War"),
    ("https://www.cnbc.com/id/100727362/device/rss/rss.html","CNBC","Economy"),
    ("https://chaski.huffpost.com/us/auto/vertical/world-news","HuffPost","Politics"),
    ("https://www.france24.com/en/rss","France24","War"),
    ("https://feeds.feedburner.com/time/world","TIME","Politics"),
    ("https://www.cfr.org/rss.xml","CFR","Politics"),
]

# fallback: 국가/수도 좌표 (GDELT가 못 잡을 때)
PLACES = {
    "russia":(55.7558,37.6173),"russian":(55.7558,37.6173),"moscow":(55.7558,37.6173),
    "ukraine":(50.4501,30.5234),"ukrainian":(50.4501,30.5234),"kyiv":(50.4501,30.5234),"kiev":(50.4501,30.5234),
    "china":(39.9042,116.4074),"chinese":(39.9042,116.4074),"beijing":(39.9042,116.4074),
    "united states":(38.8951,-77.0364),"washington":(38.8951,-77.0364),"america":(38.8951,-77.0364),"american":(38.8951,-77.0364),
    "japan":(35.6762,139.6503),"japanese":(35.6762,139.6503),"tokyo":(35.6762,139.6503),
    "britain":(51.5074,-0.1278),"london":(51.5074,-0.1278),"british":(51.5074,-0.1278),
    "korea":(37.5665,126.9780),"korean":(37.5665,126.9780),"seoul":(37.5665,126.9780),
    "north korea":(39.0194,125.7381),"pyongyang":(39.0194,125.7381),
    "israel":(31.7683,35.2137),"israeli":(31.7683,35.2137),"jerusalem":(31.7683,35.2137),"tel aviv":(32.0853,34.7818),
    "gaza":(31.3547,34.3088),"palestine":(31.9522,35.2332),"palestinian":(31.9522,35.2332),
    "iran":(35.6892,51.3890),"iranian":(35.6892,51.3890),"tehran":(35.6892,51.3890),
    "iraq":(33.3128,44.3615),"baghdad":(33.3128,44.3615),
    "taiwan":(23.6978,120.9605),"taipei":(25.0330,121.5654),
    "france":(46.2276,2.2137),"french":(46.2276,2.2137),"paris":(48.8566,2.3522),
    "germany":(51.1657,10.4515),"german":(51.1657,10.4515),"berlin":(52.5200,13.4050),
    "turkey":(39.9334,32.8597),"turkish":(39.9334,32.8597),"ankara":(39.9334,32.8597),"istanbul":(41.0082,28.9784),
    "syria":(34.8021,38.9968),"syrian":(34.8021,38.9968),"damascus":(33.5138,36.2765),
    "saudi":(23.8859,45.0792),"riyadh":(24.7136,46.6753),
    "india":(20.5937,78.9629),"indian":(20.5937,78.9629),"delhi":(28.6139,77.2090),"mumbai":(19.0760,72.8777),
    "pakistan":(30.3753,69.3451),"pakistani":(30.3753,69.3451),
    "venezuela":(6.4238,-66.5897),"yemen":(15.5527,48.5164),"sudan":(12.8628,30.2176),
    "egypt":(26.8206,30.8025),"cairo":(30.0444,31.2357),"lebanon":(33.8547,35.8623),"beirut":(33.8938,35.5018),
    "afghanistan":(33.9391,67.7100),"kabul":(34.5253,69.1783),
    "poland":(51.9194,19.1451),"italy":(41.8719,12.5674),"spain":(40.4637,-3.7492),
    "brazil":(-14.2350,-51.9253),"mexico":(23.6345,-102.5528),"canada":(56.1304,-106.3468),
    "australia":(-25.2744,133.7751),"taiwan strait":(24.0,119.0),"south china sea":(13.0,114.0),
    "nato":(50.8503,4.3517),"eu":(50.8503,4.3517),"european union":(50.8503,4.3517),"brussels":(50.8503,4.3517),
    "pentagon":(38.8719,-77.0563),"white house":(38.8977,-77.0365),"kremlin":(55.7520,37.6175),
}

IMPACT = {
    10:["nuclear","world war","invasion","genocide","collapse"],
    9:["emergency","coup","assassination","missile strike","rate hike","rate cut","default","airstrike"],
    8:["escalation","resignation","market crash","recession","sanctions","killed","attack"],
    7:["military","summit","election","protest","tariff","conflict","strike"],
    6:["warning","tension","talks","inflation"],
}
KW = {
    "War":["war","military","strike","missile","bomb","attack","invasion","troops","combat","shelling","ceasefire","conflict","weapon","killed","casualties","drone","explosion","offensive"],
    "Economy":["inflation","interest rate","recession","gdp","fed","ecb","default","market","stock","trade","tariff","bank","currency","oil","commodity","crypto","economy","economic"],
    "Politics":["election","president","minister","parliament","vote","coup","resign","summit","diplomacy","treaty","nato","congress","senate","sanction"],
}
WEEK = 7*24*3600

def mid(*p): return hashlib.sha1("|".join(str(x) for x in p).encode()).hexdigest()[:16]
def score(t):
    t=t.lower()
    for s in sorted(IMPACT,reverse=True):
        if any(w in t for w in IMPACT[s]): return s
    return 5
def category(t,d):
    t=t.lower(); sc={c:sum(1 for w in KW[c] if w in t) for c in KW}; b=max(sc,key=sc.get)
    return b if sc[b]>0 else d
def places(t):
    t=" "+t.lower()+" "; f={}
    for n,co in PLACES.items():
        if " "+n+" " in t or n in t: f[co]=n.title()
    return [(v,k[0],k[1]) for k,v in f.items()]
def parse_ts(s):
    if not s: return int(time.time())
    for fmt in ["%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S GMT","%a, %d %b %Y %H:%M:%S %Z","%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%M:%S%z"]:
        try: return int(datetime.strptime(s.strip(),fmt).timestamp())
        except: pass
    return int(time.time())
def sns(tag): return tag.split("}")[-1] if "}" in tag else tag

def fetch_rss(url,source,dc):
    out=[]
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (NewsBot/1.0)"})
        with urllib.request.urlopen(req,timeout=15) as r: raw=r.read()
        root=ET.fromstring(raw)
        for it in [e for e in root.iter() if sns(e.tag) in ("item","entry")][:20]:
            title=desc=link=pub=""
            for ch in it:
                tg=sns(ch.tag)
                if tg=="title": title=(ch.text or "").strip()
                elif tg in("description","summary","content"): desc=(ch.text or desc or "").strip()
                elif tg=="link": link=(ch.text or ch.get("href") or "").strip()
                elif tg in("pubDate","published","updated","date"): pub=pub or (ch.text or "").strip()
            if not title: continue
            out.append({"title":title[:200],"full":f"{title} {desc}","pub":pub,"link":link,"source":source,"cat":dc})
    except Exception as e:
        print(f"SKIP {source}: {type(e).__name__} {e}")
    return out

def fetch_gdelt(query, cat):
    """GDELT GEO API: 도시/지역 단위 정확한 좌표 자동 제공"""
    out=[]
    try:
        params=urllib.parse.urlencode({"query":query,"format":"GeoJSON","mode":"PointData","timespan":"3d","maxpoints":"60","sortby":"date"})
        url=f"https://api.gdeltproject.org/api/v2/geo/geo?{params}"
        req=urllib.request.Request(url,headers={"User-Agent":"NewsBot/1.0"})
        with urllib.request.urlopen(req,timeout=25) as r: data=json.loads(r.read())
        for f in data.get("features",[]):
            g=f.get("geometry") or {}; c=g.get("coordinates") or []; p=f.get("properties") or {}
            if len(c)!=2: continue
            lng,lat=c[0],c[1]
            name=(p.get("name") or "").split("<")[0].strip()[:160]
            if not name: continue
            url_src=p.get("url") or p.get("shareimage") or ""
            out.append({"title":name,"full":name,"lat":lat,"lng":lng,"place":p.get("name","").split(",")[0][:40] if p.get("name") else "","cat":cat,"link":url_src,"source":"GDELT","pub":""})
    except Exception as e:
        print(f"GDELT {cat} fail: {type(e).__name__} {e}")
    return out

def load_existing():
    try:
        with open("docs/data.json",encoding="utf-8") as f:
            return {e["id"]:e for e in json.load(f).get("events",[])}
    except: return {}

def compute_threat(events, now):
    """자체 THREAT INDEX (estimated). 최근 24h critical 밀집도로 1~5 산출. 5=가장 위험"""
    recent=[e for e in events if now-e["ts"]<=86400]
    crit=sum(1 for e in recent if e["impact_score"]>=8)
    war=sum(1 for e in recent if e["category"]=="War" and e["impact_score"]>=7)
    s=crit*2+war
    if s>=40: lvl=1
    elif s>=25: lvl=2
    elif s>=12: lvl=3
    elif s>=5: lvl=4
    else: lvl=5
    return {"level":lvl,"critical_24h":crit,"war_24h":war,"score":s}

def main():
    now=int(time.time())
    events=load_existing()
    print(f"기존 {len(events)}건 로드")

    # 1) RSS
    for url,source,cat in FEEDS:
        print(f"-> RSS {source}")
        for it in fetch_rss(url,source,cat):
            locs=places(it["full"])
            if not locs: continue
            cat2=category(it["full"],it["cat"]); imp=score(it["full"]); ts=parse_ts(it["pub"])
            if now-ts>WEEK: continue
            for name,lat,lng in locs[:1]:
                eid=mid(source,name,it["title"][:40])
                if eid in events: continue
                events[eid]={"id":eid,"title":it["title"],"lat":lat,"lng":lng,"category":cat2,
                    "impact_score":imp,"source":source,"url":it["link"],"place":name,"ts":ts}
        time.sleep(0.2)

    # 2) GDELT GEO (도시 단위 정확 좌표)
    gq={"War":'(war OR military OR strike OR missile OR invasion OR airstrike OR shelling OR offensive)',
        "Economy":'(inflation OR recession OR "central bank" OR default OR sanctions OR "stock market")',
        "Politics":'(election OR coup OR summit OR sanctions OR resignation OR "no confidence")'}
    for cat,q in gq.items():
        print(f"-> GDELT {cat}")
        for it in fetch_gdelt(q,cat):
            imp=score(it["full"]); ts=now
            eid=mid("GDELT",round(it["lat"],3),round(it["lng"],3),it["title"][:40])
            if eid in events: continue
            events[eid]={"id":eid,"title":it["title"],"lat":it["lat"],"lng":it["lng"],"category":cat,
                "impact_score":imp,"source":"GDELT","url":it["link"],"place":it["place"],"ts":ts}
        time.sleep(0.5)

    fresh=[e for e in events.values() if now-e["ts"]<=WEEK]
    fresh.sort(key=lambda x:x["ts"],reverse=True)
    fresh=fresh[:2000]
    threat=compute_threat(fresh,now)

    os.makedirs("docs",exist_ok=True)
    with open("docs/data.json","w",encoding="utf-8") as f:
        json.dump({"updated":datetime.utcnow().isoformat(),"total":len(fresh),"threat":threat,"events":fresh},f,ensure_ascii=False)
    print(f"DONE: {len(fresh)}건, THREAT L{threat['level']}")

if __name__=="__main__":
    try: main()
    except Exception as e:
        import traceback; traceback.print_exc()
        os.makedirs("docs",exist_ok=True)
        if not os.path.exists("docs/data.json"):
            with open("docs/data.json","w") as f: json.dump({"updated":"","total":0,"threat":{"level":5},"events":[]},f)
