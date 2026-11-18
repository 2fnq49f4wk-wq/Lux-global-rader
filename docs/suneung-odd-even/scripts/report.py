import json,collections,os
D=os.path.join(os.path.dirname(__file__),'..','data')
k=json.load(open(f'{D}/keys_all.json')); ch=json.load(open(f'{D}/changes.json'))
C='①②③④⑤'; YRS=['2022','2023','2024','2025','2026']; SUBS=['국어','수학','영어','한국사']
FIX={('22','국어',44):[5,4,3,2,1],('22','국어',36):[5,4,3,2,1],('22','수학',9):[5,4,3,2,1],('22','수학',15):[5,4,3,2,1]}
def dist(d): c=collections.Counter(v[0] for v in d.values() if isinstance(v[0],int)); return [c[i] for i in range(1,6)]
def fd(l): return ' / '.join(f'{C[i]}{n}' for i,n in enumerate(l))
L=[]
for yr in YRS:
  L.append(f'\n## {yr}학년도\n')
  for sub in SUBS:
    o,e=k[yr][sub]['홀'],k[yr][sub]['짝']
    L.append(f'\n### {sub}\n')
    L.append('| 구분 | 문항 | 배점 | 홀수형 정답 | 짝수형 정답 |\n|---|---|---|---|---|')
    rows=[x for x in ch if x[0]==yr and x[1]==sub]
    for x in rows: L.append(f'| {x[2]} | {x[3]}번 | {x[4]}점 | {C[x[5]-1]} | {C[x[6]-1]} |')
    if not rows: L.append('| - | 정답 변경 문항 없음 | | | |')
    pf=f'{D}/perm_{yr[2:]}_{sub}.json'
    if os.path.exists(pf):
      P=json.load(open(pf)); hid=[]; perms=[]
      for qo,qe,p in P:
        p=FIX.get((yr[2:],sub,qo),p)
        perms.append(f"{qo}번 `{''.join(C[i-1] for i in p)}`")
        if p==[5,4,3,2,1]:
          ans=[d[str(qo)][0] for sec,d in o.items() if str(qo) in d]
          if 3 in ans and not any(x[3]==qo for x in rows): hid.append(qo)
      L.append(f"\n문제지 원문 대조(짝수형 ①~⑤ 자리에 홀수형 몇 번 선지가 왔는지): {', '.join(perms)}")
      if hid: L.append(f"\n→ 정답이 ③이라 정답표엔 안 드러나지만 선지가 역순으로 바뀐 문항: {', '.join(map(str,hid))}번")
    L.append('\n| 구분 | 홀수형 정답 분포 | 짝수형 정답 분포 | 일치 |\n|---|---|---|---|')
    for sec in o:
      a,b=dist(o[sec]),dist(e[sec]); L.append(f'| {sec} | {fd(a)} | {fd(b)} | {"O" if a==b else "**X**"} |')
    if sub in ('국어','수학'):
      for sec in o:
        if sec=='공통':continue
        a=[x+y for x,y in zip(dist(o['공통']),dist(o[sec]))]; b=[x+y for x,y in zip(dist(e['공통']),dist(e[sec]))]
        L.append(f'| 공통+{sec} | {fd(a)} | {fd(b)} | {"O" if a==b else "**X**"} |')
open(os.path.join(os.path.dirname(__file__),'..','detail.md'),'w').write('# 연도별 상세 (홀수형 vs 짝수형)\n'+'\n'.join(L)+'\n')
