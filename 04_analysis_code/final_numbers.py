import io, contextlib, json
exec(open('robust.py').read().split('out={}')[0])
byid={i[0]:i for i in INV}
P=(1,2,7,9); sel=[byid[i] for i in P]; cost=sum(i[2] for i in sel)
def yearly(sel,scale=1.0):
    ys=[0,0,0]
    for m in range(36):
        live=[i for i in sel if m>=i[3]]
        ys[m//12]+=steady(live,scale)/12
    return ys
def payback(sel,scale=1.0):
    c=-cost
    for m in range(60):
        c+=steady([i for i in sel if m>=i[3]],scale)/12
        if c>=0: return m+1
ys=yearly(sel)
r=dict(ids=P,cost=cost,y1=ys[0],y2=ys[1],y3=ys[2],total3=sum(ys),net3=sum(ys)-cost,run=steady(sel),
       roi_y1=(ys[0]-cost)/cost,roi_3y=(sum(ys)-cost)/cost,payback={s:payback(sel,s) for s in (1,0.5,0.25)},
       net3_scaled={s:sum(yearly(sel,s))-cost for s in (0.75,0.5,0.25)},
       standalone={i[1]:dict(cost=i[2],months=i[3],run=steady([i])) for i in sel},
       ramp3_net=three_year(sel,ramp=3)-cost)
lo,hi=0,1
for _ in range(40):
    mid=(lo+hi)/2
    if sum(yearly(sel,mid))-cost>0: hi=mid
    else: lo=mid
r['breakeven_scale']=hi
# warranty vs rework split of run rate
tw=tr=0
for c,(n,wc,lab,mat,eh) in CELLS.items():
    rw=(lab+eh)*LR+mat;a=b=1
    for inv in sel:
        for rr,s in inv[5]:
            if s(c): a*=1-rr
        for rr,s in inv[6]:
            if s(c): b*=1-rr
    tw+=wc*(1-a);tr+=rw*(1-b)
r['run_warranty']=tw;r['run_rework']=tr
# downtime avoided (category level, warranty factors)
dB,dNB,dLP=6274,9932-6274,21906
r['downtime_avoided']=dB*(1-.95*.6*.75)+dNB*(1-.95*.6)+dLP*.15
r['downtime_total']=37611
# coverage of targeted cost pools
print(json.dumps(r,indent=1,default=lambda x:round(x,3)))
json.dump(r,open('final_portfolio.json','w'),indent=1,default=str)
