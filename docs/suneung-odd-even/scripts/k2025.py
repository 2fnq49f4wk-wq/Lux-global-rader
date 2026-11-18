import json
P='/tmp/claude-0/-home-user-Lux-global-rader/97abad5c-7d65-542a-bb5d-3692073d14d8/scratchpad/dl/keys_text.json'
k=json.load(open(P))
def mk(start,ans,pts): return {str(start+i):[a,p] for i,(a,p) in enumerate(zip(ans,pts))}
def S(s): return [int(c) for c in s.split()]
E_o=S('2 5 1 3 1 4 3 4 5 2 2 1 5 1 2 3 4 1 2 1 3 2 1 5 4 4 3 3 2 4 5 3 2 5 4 5 3 4 4 1 2 5 2 3 4')
E_e=S('2 1 5 3 1 4 3 4 5 2 3 1 1 5 2 2 4 1 3 5 3 1 2 5 4 4 3 3 2 4 1 2 2 5 4 5 3 4 4 1 2 5 2 3 4')
E_p=S('2 2 2 2 2 2 2 2 2 2 3 2 2 3 3 2 2 2 2 2 3 2 2 2 2 2 2 2 2 3 2 2 3 3 2 2 3 3 2 2 2 3 2 2 2')
K_o=S('3 4 5 4 5 3 2 1 2 3 1 5 3 1 2 2 3 2 4 1 4 4 5 2 2 1 1 4 3 5 4 3 5 2')
K_e=S('3 4 5 4 5 3 2 1 1 3 1 5 3 1 2 2 3 2 2 1 4 4 5 4 2 1 1 4 3 5 4 3 5 2')
K_p=S('2 2 3 2 2 2 2 3 2 2 2 2 3 2 2 3 2 2 2 2 3 2 2 2 3 2 2 2 2 2 3 2 2 3')
H_o=S('2 4 3 4 5 4 3 1 1 5 2');H_e=S('2 4 3 4 5 4 3 1 2 5 2');H_p=S('2 2 2 2 2 3 2 2 2 2 3')
L_o=S('5 4 3 1 2 4 3 5 2 1 3');L_e=S('5 4 3 1 2 4 3 4 2 1 3');L_p=S('2 3 2 2 2 2 2 2 2 2 3')
M_o=S('5 4 5 2 4 5 3 1 4 3 2 1 5 4 2 7 33 96 41 36 16 64');M_p=S('2 2 3 3 3 3 3 3 4 4 4 4 4 4 4 3 3 3 3 4 4 4')
M_e=list(M_o);M_e[8]=2;M_e[10]=4
sp=S('2 3 3 3 3 4 4 4')
T=S('5 3 1 3 3 2 25 19');Mi=S('3 4 2 1 1 2 25 17');G=S('3 4 3 1 1 4 107 316')
Hs_o=S('5 1 3 3 1 4 5 2 5 3 5 4 1 3 2 2 4 3 2 1');Hs_p=S('2 3 3 2 2 3 2 3 3 2 3 2 3 3 2 2 3 2 3 2')
Hs_e=list(Hs_o);Hs_e[10]=1;Hs_e[12]=5
def fix(l): return [a if (i<15 or a<=5) else 'S%d'%a for i,a in enumerate(l)]
def mfix(l,base): return [ ('S%d'%a if (base+i)>=16+0 and (base+i) not in range(23,29) and (base+i)>=16 else a) for i,a in enumerate(l)]
mo=[a if i<15 else 'S%d'%a for i,a in enumerate(M_o)]; me=[a if i<15 else 'S%d'%a for i,a in enumerate(M_e)]
def sel(l): return [a if i<6 else 'S%d'%a for i,a in enumerate(l)]
k['2025']={
 '영어':{'홀':{'공통':mk(1,E_o,E_p)},'짝':{'공통':mk(1,E_e,E_p)}},
 '국어':{'홀':{'공통':mk(1,K_o,K_p),'화법과 작문':mk(35,H_o,H_p),'언어와 매체':mk(35,L_o,L_p)},
        '짝':{'공통':mk(1,K_e,K_p),'화법과 작문':mk(35,H_e,H_p),'언어와 매체':mk(35,L_e,L_p)}},
 '수학':{t:{'공통':mk(1,m,M_p),'확률과 통계':mk(23,sel(T),sp),'미적분':mk(23,sel(Mi),sp),'기하':mk(23,sel(G),sp)} for t,m in (('홀',mo),('짝',me))},
 '한국사':{'홀':{'공통':mk(1,Hs_o,Hs_p)},'짝':{'공통':mk(1,Hs_e,Hs_p)}},
}
json.dump(k,open(P.replace('keys_text','keys_all'),'w'),ensure_ascii=False,indent=0)
