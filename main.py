import json, os, time, re, hashlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime

FEEDS = [
    # === 글로벌 주요 (War)
    ("https://feeds.bbci.co.uk/news/world/rss.xml","BBC","War"),
    ("https://rss.dw.com/rdf/rss-en-world","DW","War"),
    ("https://www.aljazeera.com/xml/rss/all.xml","AlJazeera","War"),
    ("https://www.theguardian.com/world/rss","Guardian","War"),
    ("https://feeds.skynews.com/feeds/rss/world.xml","SkyNews","War"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml","NYT","War"),
    ("https://moxie.foxnews.com/google-publisher/world.xml","Fox","War"),
    ("https://feeds.a.dj.com/rss/RSSWorldNews.xml","WSJ World","War"),
    ("https://www.cbsnews.com/latest/rss/world","CBS","War"),
    ("https://abcnews.go.com/abcnews/internationalheadlines","ABC","War"),
    ("https://www.france24.com/en/rss","France24","War"),
    ("https://feeds.feedburner.com/ndtvnews-world-news","NDTV","War"),
    ("https://www.cbc.ca/webfeed/rss/rss-world","CBC","War"),
    ("https://www.rt.com/rss/news/","RT","War"),
    ("https://sputnikglobe.com/export/rss2/archive/index.xml","Sputnik","War"),
    ("https://english.kyodonews.net/rss/news.xml","Kyodo","War"),
    ("https://www.timesofisrael.com/feed/","TimesOfIsrael","War"),
    ("https://www.jpost.com/rss/rssfeedsheadlines.aspx","JPost","War"),
    ("https://english.alarabiya.net/.mrss/en.xml","AlArabiya","War"),
    ("https://www.scmp.com/rss/91/feed","SCMP","War"),
    # === Economy
    ("https://feeds.bbci.co.uk/news/business/rss.xml","BBC Biz","Economy"),
    ("https://www.ft.com/rss/home","FT","Economy"),
    ("https://feeds.marketwatch.com/marketwatch/topstories","MarketWatch","Economy"),
    ("https://finance.yahoo.com/news/rssindex","Yahoo","Economy"),
    ("https://www.economist.com/finance-and-economics/rss.xml","Economist Fin","Economy"),
    ("https://asia.nikkei.com/rss/feed/nar","Nikkei","Economy"),
    ("https://feeds.content.dowjones.io/public/rss/RSSMarketsMain","WSJ Markets","Economy"),
    ("https://www.cnbc.com/id/100727362/device/rss/rss.html","CNBC","Economy"),
    ("https://feeds.reuters.com/reuters/businessNews","Reuters Biz","Economy"),
    ("https://www.investing.com/rss/news.rss","Investing","Economy"),
    ("https://seekingalpha.com/feed.xml","SeekingAlpha","Economy"),
    ("https://www.zerohedge.com/fullrss2.xml","ZeroHedge","Economy"),
    # === Politics
    ("https://feeds.npr.org/1014/rss.xml","NPR Politics","Politics"),
    ("https://www.economist.com/international/rss.xml","Economist Intl","Politics"),
    ("https://feeds.feedburner.com/time/world","TIME","Politics"),
    ("https://www.cfr.org/rss.xml","CFR","Politics"),
    ("https://foreignpolicy.com/feed/","ForeignPolicy","Politics"),
    ("https://www.politico.com/rss/politicopicks.xml","Politico","Politics"),
    ("https://www.euractiv.com/feed/","Euractiv","Politics"),
    ("https://www.dailysabah.com/rssFeed/4","DailySabah","Politics"),
    ("https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf","AllAfrica","Politics"),
    ("https://www.batimes.com.ar/feed","BuenosAires","Politics"),
]

# Reddit 공개 JSON (텔레그램 대체 실시간 소스)
REDDIT_SUBS = [
    ("worldnews","War"),("geopolitics","Politics"),
    ("UkraineWarVideoReport","War"),("economics","Economy"),
    ("CombatFootage","War"),("anime_titties","Politics"),
]

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
    "saudi":(23.8859,45.0792),"riyadh":(24.7136,46.6753),"saudi arabia":(23.8859,45.0792),
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
    "argentina":(-38.4161,-63.6167),"nigeria":(9.0820,8.6753),"ethiopia":(9.1450,40.4897),
    "south africa":(-30.5595,22.9375),"kenya":(-0.0236,37.9062),"libya":(26.3351,17.2283),
    "qatar":(25.3548,51.1839),"uae":(23.4241,53.8478),"dubai":(25.2048,55.2708),
    "philippines":(12.8797,121.7740),"indonesia":(-0.7893,113.9213),"thailand":(15.8700,100.9925),
    "vietnam":(14.0583,108.2772),"myanmar":(21.9162,95.9560),"bangladesh":(23.6850,90.3563),
    "greece":(39.0742,21.8243),"netherlands":(52.1326,5.2913),"sweden":(60.1282,18.6435),
    "norway":(60.4720,8.4689),"finland":(61.9241,25.7482),"switzerland":(46.8182,8.2275),
    "colombia":(4.5709,-74.2973),"chile":(-35.6751,-71.5430),"peru":(-9.1900,-75.0152),
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
# 카테고리별 보관 기간 (초)
RETAIN = {"War":7*24*3600, "Politics":5*24*3600, "Economy":3*24*3600}
MAXRETAIN = 7*24*3600

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
        for it in [e for e in root.iter() if sns(e.tag) in ("item","entry")][:40]:
            title=desc=link=pub=img=""
            for ch in it:
                tg=sns(ch.tag)
                if tg=="title": title=(ch.text or "").strip()
                elif tg in("description","summary"): desc=(ch.text or desc or "").strip()
                elif tg=="encoded": desc=(ch.text or desc or "").strip()
                elif tg=="link": link=(ch.text or ch.get("href") or "").strip()
                elif tg in("pubDate","published","updated","date"): pub=pub or (ch.text or "").strip()
                elif tg in("thumbnail","image"):
                    u=ch.get("url")
                    if u and not img: img=u
                elif tg=="content":
                    u=ch.get("url")
                    if u and not img and re.search(r'\.(jpg|jpeg|png|webp)',u,re.I): img=u
                    elif ch.text and not desc: desc=ch.text.strip()
                elif tg=="enclosure":
                    u=ch.get("url"); ty=ch.get("type","")
                    if u and ("image" in ty or re.search(r'\.(jpg|jpeg|png|webp)',u,re.I)) and not img: img=u
                elif tg=="group":
                    for sub in ch:
                        if sns(sub.tag) in("content","thumbnail"):
                            u=sub.get("url")
                            if u and not img: img=u
            if not img and desc:
                m=re.search(r'<img[^>]+src=["\']([^"\']+)',desc)
                if m: img=m.group(1)
            clean=re.sub(r'<[^>]+>','',desc); clean=re.sub(r'\s+',' ',clean).strip()[:280]
            if not title: continue
            out.append({"title":title[:200],"full":f"{title} {clean}","pub":pub,"link":link,
                "source":source,"cat":dc,"img":img,"summary":clean})
    except Exception as e:
        print(f"SKIP {source}: {type(e).__name__} {e}")
    return out

def fetch_reddit(sub,dc):
    out=[]
    try:
        url=f"https://www.reddit.com/r/{sub}/hot.json?limit=40"
        req=urllib.request.Request(url,headers={"User-Agent":"NewsBot/1.0 (radar)"})
        with urllib.request.urlopen(req,timeout=15) as r: data=json.loads(r.read())
        for c in data.get("data",{}).get("children",[]):
            d=c.get("data",{})
            title=d.get("title","").strip()
            if not title: continue
            img=""
            pv=d.get("preview",{}).get("images",[])
            if pv:
                img=pv[0].get("source",{}).get("url","").replace("&amp;","&")
            elif d.get("thumbnail","").startswith("http"):
                img=d["thumbnail"]
            out.append({"title":title[:200],"full":title,"pub":"","link":"https://reddit.com"+d.get("permalink",""),
                "source":f"r/{sub}","cat":dc,"img":img,"summary":(d.get("selftext","") or "")[:280],
                "ts":int(d.get("created_utc",time.time()))})
    except Exception as e:
        print(f"REDDIT {sub} fail: {type(e).__name__} {e}")
    return out

def fetch_gdelt(query, cat):
    out=[]
    try:
        params=urllib.parse.urlencode({"query":query,"format":"GeoJSON","mode":"PointData","timespan":"2d","maxpoints":"150","sortby":"date"})
        url=f"https://api.gdeltproject.org/api/v2/geo/geo?{params}"
        req=urllib.request.Request(url,headers={"User-Agent":"NewsBot/1.0"})
        with urllib.request.urlopen(req,timeout=25) as r: data=json.loads(r.read())
        for f in data.get("features",[]):
            g=f.get("geometry") or {}; c=g.get("coordinates") or []; p=f.get("properties") or {}
            if len(c)!=2: continue
            lng,lat=c[0],c[1]
            name=(p.get("name") or "").split("<")[0].strip()[:160]
            if not name: continue
            out.append({"title":name,"full":name,"lat":lat,"lng":lng,"place":p.get("name","").split(",")[0][:40] if p.get("name") else "","cat":cat,"link":p.get("url","")})
    except Exception as e:
        print(f"GDELT {cat} fail: {type(e).__name__} {e}")
    return out

def fetch_frontline():
    try:
        u="https://deepstatemap.live/api/history/last/geojson"
        req=urllib.request.Request(u,headers={"User-Agent":"deepstate-scraper/0.1"})
        with urllib.request.urlopen(req,timeout=30) as r: data=json.loads(r.read())
        feats=data.get("features") if isinstance(data,dict) else None
        if feats:
            print(f"frontline OK (official): {len(feats)}")
            return simplify_fc(feats)
    except Exception as e:
        print(f"frontline official fail: {type(e).__name__} {e}")
    try:
        idx="https://api.github.com/repos/cyterat/deepstate-map-data/contents/data"
        req=urllib.request.Request(idx,headers={"User-Agent":"NewsBot/1.0","Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(req,timeout=20) as r: files=json.loads(r.read())
        gj=sorted([f for f in files if f["name"].endswith(".geojson")],key=lambda x:x["name"])
        latest=gj[-1]["download_url"]
        req2=urllib.request.Request(latest,headers={"User-Agent":"NewsBot/1.0"})
        with urllib.request.urlopen(req2,timeout=30) as r: data=json.loads(r.read())
        feats=data.get("features",[])
        if feats:
            print(f"frontline OK (mirror): {len(feats)}")
            return simplify_fc(feats)
    except Exception as e:
        print(f"frontline mirror fail: {type(e).__name__} {e}")
    return None

def simplify_fc(feats):
    out=[]
    for f in feats:
        p=f.get("properties") or {}
        out.append({"type":"Feature","geometry":f.get("geometry"),"properties":{"name":p.get("name","")}})
    return {"type":"FeatureCollection","features":out}

def fetch_earthquakes():
    """USGS 지진 (M4.5+, 최근 1일). 폭발/대형 사건 보조 탐지"""
    try:
        u="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
        req=urllib.request.Request(u,headers={"User-Agent":"NewsBot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r: data=json.loads(r.read())
        out=[]
        for f in data.get("features",[]):
            g=f.get("geometry") or {}; c=g.get("coordinates") or []; p=f.get("properties") or {}
            if len(c)<2: continue
            mag=p.get("mag") or 0
            out.append({"lng":c[0],"lat":c[1],"mag":mag,"place":p.get("place","")[:80],
                "title":f"M{mag} earthquake — {p.get('place','')}"[:160],
                "url":p.get("url",""),"ts":int((p.get("time") or 0)/1000) or int(time.time())})
        print(f"quakes OK: {len(out)}")
        return out
    except Exception as e:
        print(f"quakes fail: {type(e).__name__} {e}")
        return []

def load_existing():
    try:
        with open("docs/data.json",encoding="utf-8") as f:
            return {e["id"]:e for e in json.load(f).get("events",[])}
    except: return {}

def compute_threat(events, now):
    recent=[e for e in events if now-e["ts"]<=86400]
    crit=sum(1 for e in recent if e["impact_score"]>=8)
    war=sum(1 for e in recent if e["category"]=="War" and e["impact_score"]>=7)
    eco=sum(1 for e in recent if e["category"]=="Economy" and e["impact_score"]>=8)
    s=crit*2+war+eco
    if s>=180: lvl=1
    elif s>=120: lvl=2
    elif s>=70: lvl=3
    elif s>=30: lvl=4
    else: lvl=5
    return {"level":lvl,"critical_24h":crit,"war_24h":war,"eco_24h":eco,"score":s,"total_24h":len(recent)}

def keep(e, now):
    return (now-e["ts"]) <= RETAIN.get(e["category"], MAXRETAIN)

def main():
    now=int(time.time())
    events=load_existing()
    print(f"기존 {len(events)}건 로드")

    for url,source,cat in FEEDS:
        print(f"-> RSS {source}")
        for it in fetch_rss(url,source,cat):
            locs=places(it["full"])
            if not locs: continue
            cat2=category(it["full"],it["cat"]); imp=score(it["full"]); ts=parse_ts(it["pub"])
            if now-ts>MAXRETAIN: continue
            for name,lat,lng in locs[:1]:
                eid=mid(source,name,it["title"][:40])
                if eid in events: continue
                events[eid]={"id":eid,"title":it["title"],"lat":lat,"lng":lng,"category":cat2,
                    "impact_score":imp,"source":source,"url":it["link"],"place":name,"ts":ts,
                    "img":it.get("img",""),"summary":it.get("summary","")}
        time.sleep(0.15)

    for sub,cat in REDDIT_SUBS:
        print(f"-> Reddit r/{sub}")
        for it in fetch_reddit(sub,cat):
            locs=places(it["full"])
            if not locs: continue
            cat2=category(it["full"],it["cat"]); imp=score(it["full"]); ts=it.get("ts",now)
            for name,lat,lng in locs[:1]:
                eid=mid(it["source"],name,it["title"][:40])
                if eid in events: continue
                events[eid]={"id":eid,"title":it["title"],"lat":lat,"lng":lng,"category":cat2,
                    "impact_score":imp,"source":it["source"],"url":it["link"],"place":name,"ts":ts,
                    "img":it.get("img",""),"summary":it.get("summary","")}
        time.sleep(0.3)

    gq={"War":'(war OR military OR strike OR missile OR invasion OR airstrike OR shelling OR offensive)',
        "Economy":'(inflation OR recession OR "central bank" OR default OR sanctions OR "stock market")',
        "Politics":'(election OR coup OR summit OR sanctions OR resignation OR "no confidence")'}
    for cat,q in gq.items():
        print(f"-> GDELT {cat}")
        for it in fetch_gdelt(q,cat):
            imp=score(it["full"])
            eid=mid("GDELT",round(it["lat"],3),round(it["lng"],3),it["title"][:40])
            if eid in events: continue
            events[eid]={"id":eid,"title":it["title"],"lat":it["lat"],"lng":it["lng"],"category":cat,
                "impact_score":imp,"source":"GDELT","url":it["link"],"place":it["place"],"ts":now,
                "img":"","summary":""}
        time.sleep(0.5)

    frontline=fetch_frontline()
    quakes=fetch_earthquakes()

    fresh=[e for e in events.values() if keep(e,now)]
    fresh.sort(key=lambda x:x["ts"],reverse=True)
    fresh=fresh[:4000]
    threat=compute_threat(fresh,now)

    os.makedirs("docs",exist_ok=True)
    out={"updated":datetime.utcnow().isoformat(),"total":len(fresh),"threat":threat,"events":fresh}
    if frontline: out["frontline"]=frontline
    if quakes: out["quakes"]=quakes
    with open("docs/data.json","w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False)
    print(f"DONE: {len(fresh)}건, THREAT L{threat['level']}, frontline={'Y' if frontline else 'N'}, quakes={len(quakes)}")

if __name__=="__main__":
    try: main()
    except Exception as e:
        import traceback; traceback.print_exc()
        os.makedirs("docs",exist_ok=True)
        if not os.path.exists("docs/data.json"):
            with open("docs/data.json","w") as f: json.dump({"updated":"","total":0,"threat":{"level":5},"events":[]},f)
