import itertools, io, contextlib, json
exec(open('robust.py').read().split('out={}')[0])
def mk(fn):
    a=[list(i) for i in INV]; fn(a); return [tuple(i) for i in a]
def pk_fan(a):
    a[2][5]=[(0.40,lambda c:c[0]=='Fan')]; a[2][6]=[(0.40,lambda c:c[0]=='Fan')]
def dash_half(a): a[3][5]=[(0.075,lambda c:True)]
CELLS_ALL=dict(CELLS)
scen={}
scen['base']=dict(invs=INV)
scen['revA_phaseout']=dict(invs=INV,drop_controls=True)   # controls cost gone; poka/design only act on fan/others
scen['poka_fan_only']=dict(invs=mk(pk_fan))
scen['half_benefit']=dict(invs=INV,scale=0.5)
scen['ramp3']=dict(invs=INV,ramp=3)
scen['dashboard_half']=dict(invs=mk(dash_half))
pass
res={}
for name,s in scen.items():
    CELLS.clear(); CELLS.update({k:v for k,v in CELLS_ALL.items() if not (s.get('drop_controls') and k[0]=='Controls')})
    rows=[]
    for k in range(1,11):
        for c in itertools.combinations(s['invs'],k):
            cost=sum(i[2] for i in c)
            if cost>750000: continue
            rows.append((tuple(i[0] for i in c),three_year(c,s.get('scale',1.0),s.get('ramp',0))-cost))
    best=max(r[1] for r in rows)
    for ids,v in rows:
        res.setdefault(ids,{})[name]=(v,best-v)
CELLS.clear(); CELLS.update(CELLS_ALL)
# rank by max regret
summ=[]
for ids,d in res.items():
    if len(d)<len(scen): continue
    maxreg=max(x[1] for x in d.values()); meanreg=sum(x[1] for x in d.values())/len(d)
    summ.append((maxreg,meanreg,ids,{k:round(v[0]/1e6,2) for k,v in d.items()}))
summ.sort()
cost={i[0]:i[2] for i in INV}
for m,mr,ids,d in summ[:8]:
    print(ids,sum(cost[i] for i in ids),'maxRegret=%.2fM meanRegret=%.2fM'%(m/1e6,mr/1e6),d)
print('ours (2,3,7,9):',[ (round(s[0]/1e6,2),round(s[1]/1e6,2)) for s in summ if s[2]==(2,3,7,9)])
