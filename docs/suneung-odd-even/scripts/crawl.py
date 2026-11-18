import re,subprocess,json,os
D='/tmp/claude-0/-home-user-Lux-global-rader/97abad5c-7d65-542a-bb5d-3692073d14d8/scratchpad/dl'
B='https://www.suneung.re.kr'
def get(u):
    return subprocess.run(['curl','-sS','-m','40',u],capture_output=True).stdout.decode('utf-8','ignore')
rows=[]
for p in range(1,6):
    h=get(f'{B}/boardCnts/list.do?boardID=1500234&m=0403&s=suneung&page={p}')
    t=re.sub(r'<[^>]+>','\n',h[h.find('<th scope=\'col\'>번호'):])
    toks=[x.strip() for x in t.split('\n') if x.strip() and x.strip()!='&nbsp;' and '&nbsp;' not in x]
    i=0
    while i<len(toks)-3:
        if re.fullmatch(r'\d{7}',toks[i]) and re.fullmatch(r'20\d\d',toks[i+1]):
            rows.append((toks[i],toks[i+1],toks[i+2]));i+=3
        else:i+=1
rows=sorted(set(r for r in rows if 2022<=int(r[1])<=2026))
out=[]
for seq,yr,sub in rows:
    h=get(f'{B}/boardCnts/view.do?boardID=1500234&boardSeq={seq}&lev=0&m=0403&searchType=S&statusYN=W&page=1&s=suneung')
    fs=re.findall(r"fileDown\.do\?fileSeq=([0-9a-f]+)'[^>]*>([^<]+)</a>",h)
    out.append(dict(seq=seq,yr=yr,sub=sub,files=fs))
    print(yr,sub,[f[1] for f in fs])
json.dump(out,open(D+'/index.json','w'),ensure_ascii=False,indent=1)
