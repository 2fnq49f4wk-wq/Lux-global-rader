import subprocess,re,json,glob,os,sys
A='/tmp/claude-0/-home-user-Lux-global-rader/97abad5c-7d65-542a-bb5d-3692073d14d8/scratchpad/dl/ans'
C='①②③④⑤'
SEL={'국어':(35,['화법과 작문','언어와 매체']),'수학':(23,['확률과 통계','미적분','기하'])}
res={}
for f in sorted(glob.glob(A+'/20*_*.pdf')):
    b=os.path.basename(f); yr=b[:4]; sub=b.split('_')[1]
    if sub not in ('국어','수학','영어','한국사'): continue
    t=subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True).stdout.decode()
    for page in t.split('\f'):
        m=re.search(r'\(\s*(홀|짝)\s*수\s*\)',page)
        if not m: continue
        typ=m.group(1)
        d={}
        for line in page.split('\n'):
            toks=re.findall(r'\d+|[①②③④⑤]',line)
            if len(toks)<3 or len(toks)%3: continue
            trip=[toks[i:i+3] for i in range(0,len(toks),3)]
            if not all(x[0].isdigit() and x[2].isdigit() and int(x[2])<=4 for x in trip): continue
            si=0
            for q,a,p in trip:
                q=int(q); a=C.index(a)+1 if a in C else ('S'+a)
                sec='공통'
                if sub in SEL and q>=SEL[sub][0]:
                    sec=SEL[sub][1][si]; si+=1
                d.setdefault(sec,{})[q]=(a,int(p))
        res.setdefault(yr,{}).setdefault(sub,{})[typ]=d
for yr in sorted(res):
    for sub in res[yr]:
        for typ in res[yr][sub]:
            print(yr,sub,typ,{k:len(v) for k,v in res[yr][sub][typ].items()})
json.dump({y:{s:{t:{k:{str(q):v for q,v in d.items()} for k,d in td.items()} for t,td in sd.items()} for s,sd in yd.items()} for y,yd in res.items()},open(A+'/../keys_text.json','w'),ensure_ascii=False)
