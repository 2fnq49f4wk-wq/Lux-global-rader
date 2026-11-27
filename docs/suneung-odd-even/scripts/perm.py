import re,sys,json
C='①②③④⑤'
def groups(path):
    t=open(path,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'[ \t]+',' ',t)
    res=[]
    for m in re.finditer('①',t):
        s=m.start()
        # require ②..⑤ after in order, within 1500 chars
        seg=t[s:s+2500]; pos=[0]
        ok=True
        for c in C[1:]:
            p=seg.find(c,pos[-1]+1)
            if p<0: ok=False;break
            pos.append(p)
        if not ok: continue
        end=seg.find('\n',pos[4]); end=len(seg) if end<0 else end
        opts=[seg[pos[i]+1:(pos[i+1] if i<4 else end)].strip() for i in range(5)]
        if max(len(o) for o in opts)>400: continue
        qs=re.findall(r'(?m)^(\d{1,2})\. ',t[:s])
        res.append((int(qs[-1]) if qs else 0,[re.sub(r'\s+',' ',o) for o in opts]))
    return res
def norm(o): return re.sub(r'\s','',o)[:14]
o,e=groups(sys.argv[1]),groups(sys.argv[2])
print('groups',len(o),len(e))
out=[]
for (qo,oo),(qe,ee) in zip(o,e):
    if [norm(x) for x in oo]==[norm(x) for x in ee]: continue
    perm=[]
    for x in ee:
        idx=[i for i,y in enumerate(oo) if norm(y)==norm(x)]
        perm.append(idx[0]+1 if len(idx)==1 else '?')
    out.append((qo,qe,perm))
    print(qo,qe,'짝 선지 = 홀 선지 순서',''.join(C[p-1] if p!='?' else '?' for p in perm))
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False)
