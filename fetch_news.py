import json, time, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime
import re, html

FEEDS = [
 ("BBC","https://feeds.bbci.co.uk/news/world/rss.xml"),
 ("Al Jazeera","https://www.aljazeera.com/xml/rss/all.xml"),
 ("Guardian","https://www.theguardian.com/world/rss"),
 ("NPR","https://feeds.npr.org/1004/rss.xml"),
 ("DW","https://rss.dw.com/rdf/rss-en-all"),
 ("France 24","https://www.france24.com/en/rss"),
 ("NYT","https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
 ("ABC Australia","https://www.abc.net.au/news/feed/45910/rss.xml"),
 ("Times of India","https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"),
]

def tag(e): return e.tag.split('}')[-1].lower()
def txt(e,*names):
    for c in e.iter():
        if tag(c) in names and c.text and c.text.strip(): return c.text.strip()
    return ""
def clean(s): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",s or ""))).strip()
def ts(s):
    if not s: return 0
    try: return int(parsedate_to_datetime(s).timestamp()*1000)
    except Exception: pass
    try: return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)
    except Exception: return 0

out=[]; ok=0
for name,url in FEEDS:
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (WorldNewsApp)"})
        root=ET.fromstring(urllib.request.urlopen(req,timeout=25).read())
        n=0
        for it in root.iter():
            if tag(it) not in ("item","entry"): continue
            link=""
            for c in it:
                if tag(c)=="link":
                    link=c.get("href") or (c.text or "").strip()
                    if link: break
            img=""
            for c in it.iter():
                if tag(c) in ("thumbnail","content","enclosure") and c.get("url"):
                    t=(c.get("type") or "")+c.get("url")
                    if re.search(r"image|jpe?g|png|webp",t,re.I): img=c.get("url"); break
            title=clean(txt(it,"title"))
            if not title or not link: continue
            out.append({"src":name,"title":title,"link":link,
                "desc":clean(txt(it,"description","summary"))[:220],"img":img,
                "t":ts(txt(it,"pubdate","date","updated","published"))})
            n+=1
        ok+= n>0
        print(name,n)
    except Exception as e:
        print(name,"FAILED",e)

seen=set(); items=[]
for i in sorted(out,key=lambda x:-x["t"]):
    k=i["title"].lower()
    if k in seen: continue
    seen.add(k); items.append(i)
json.dump({"updated":int(time.time()*1000),"items":items[:300]},open("news.json","w"),ensure_ascii=False)
print("total",len(items),"sources ok",ok)
