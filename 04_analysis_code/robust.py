import itertools, io, contextlib, json
src=open('analysis.py').read().split('rows = []')[0]
g={}
with contextlib.redirect_stdout(io.StringIO()): exec(src,g)
INV=g['INV']; CELLS=g['CELLS']; LR=g['LABOR_RATE']
def steady(sel,scale=1.0):
    t=0
    for c,(n,wc,lab,mat,eh) in CELLS.items():
        rw=(lab+eh)*LR+mat; a=b=1.0
        for inv in sel:
            for r,s in inv[5]:
                if s(c): a*=1-r*scale
            for r,s in inv[6]:
                if s(c): b*=1-r*scale
        t+=wc*(1-a)+rw*(1-b)
    return t
def three_year(sel,scale=1.0,ramp=0):
    tot=0
    for m in range(36):
        live=[]
        for inv in sel:
            if m>=inv[3]:
                f=min(1,(m-inv[3]+1)/ramp) if ramp else 1
                live.append((inv,f))
        # apply partial ramp by scaling each inv
        t=0
        for c,(n,wc,lab,mat,eh) in CELLS.items():
            rw=(lab+eh)*LR+mat; a=b=1.0
            for inv,f in live:
                for r,s in inv[5]:
                    if s(c): a*=1-r*scale*f
                for r,s in inv[6]:
                    if s(c): b*=1-r*scale*f
            t+=wc*(1-a)+rw*(1-b)
        tot+=t/12
    return tot
def rank(invs,scale=1.0,ramp=0,target=(2,3,7,9)):
    rows=[]
    for k in range(1,11):
        for c in itertools.combinations(invs,k):
            cost=sum(i[2] for i in c)
            if cost>750000: continue
            rows.append((three_year(c,scale,ramp)-cost,tuple(i[0] for i in c)))
    rows.sort(reverse=True)
    ids=[r[1] for r in rows]
    d={r[1]:r[0] for r in rows}; return ids.index(target)+1, (round(rows[0][0]),rows[0][1]), round(d[target]), len(rows)
out={}
# Variant 1: Poka-Yoke covers fan only (not Rev A controls)
alt=[list(i) for i in INV]
alt[2][5]=[(0.40,lambda c:c[0]=='Fan')]; alt[2][6]=[(0.40,lambda c:c[0]=='Fan')]
alt=[tuple(i) for i in alt]
out['pokayoke_fan_only']=rank(alt)
# Variant 2: 3-month linear ramp after go-live
out['ramp3']=rank(INV,ramp=3)
# Variant 3: 50% benefit
out['half']=rank(INV,scale=0.5)
# Variant 4: Dashboard benefit halved (generic claim) 
alt2=[list(i) for i in INV]; alt2[3][5]=[(0.075,lambda c:True)]; alt2=[tuple(i) for i in alt2]
out['dashboard_half']=rank(alt2)
# Braze swap comparison
byid={i[0]:i for i in INV}
for ids in [(2,3,7,9),(1,3,7,9)]:
    sel=[byid[i] for i in ids]; cost=sum(i[2] for i in sel)
    out[str(ids)]=dict(cost=cost,net3=round(three_year(sel)-cost),run=round(steady(sel)),net3_ramp=round(three_year(sel,ramp=3)-cost))
for k,v in out.items(): print(k,v)
