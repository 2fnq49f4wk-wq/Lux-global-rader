import json,collections
k=json.load(open('/tmp/claude-0/-home-user-Lux-global-rader/97abad5c-7d65-542a-bb5d-3692073d14d8/scratchpad/dl/keys_all.json'))
C='①②③④⑤'
def dist(d): 
    c=collections.Counter(v[0] for v in d.values() if isinstance(v[0],int)); return [c[i] for i in range(1,6)]
allch=[]
for yr in sorted(k):
  for sub in ['국어','수학','영어','한국사']:
    o,e=k[yr][sub]['홀'],k[yr][sub]['짝']
    for sec in o:
      ch=[]
      for q in sorted(o[sec],key=int):
        a,b=o[sec][q],e[sec][q]
        if a!=b: ch.append((int(q),a[1],a[0],b[0])); 
        assert a[1]==b[1]
      allch+= [(yr,sub,sec)+c for c in ch]
      do,de=dist(o[sec]),dist(e[sec])
      if ch or sec=='공통':
        s=', '.join(f"{q}번({p}점) {C[x-1]}→{C[y-1]}" for q,p,x,y in ch) or '변경 없음'
        print(f"{yr} {sub} [{sec}] 홀{do} 짝{de} {'동일' if do==de else '다름'} | {s}")
      else: print(f"{yr} {sub} [{sec}] 홀{do} 짝{de} | 변경 없음")
    if sub in('국어','수학'):
      for sec in o:
        if sec=='공통':continue
        a=[x+y for x,y in zip(dist(o['공통']),dist(o[sec]))];b=[x+y for x,y in zip(dist(e['공통']),dist(e[sec]))]
        print(f"    합계(공통+{sec}) 홀{a} 짝{b} {'동일' if a==b else '다름'}")
json.dump(allch,open('/tmp/claude-0/-home-user-Lux-global-rader/97abad5c-7d65-542a-bb5d-3692073d14d8/scratchpad/dl/changes.json','w'),ensure_ascii=False)
print(len(allch))
