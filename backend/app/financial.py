from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from .db import Transaction, Invoice
D=Decimal
CENT=D('0.01')
def money(value): return float(D(value).quantize(CENT,rounding=ROUND_HALF_UP))
def seed(db,org):
    today=date.today(); org.opening_balance=D('0')
    for month in range(6):
        start=today-timedelta(days=(6-month)*30)
        for day,amount,direction,category in [(2,18000,'inflow','Sales'),(9,9500,'inflow','Sales'),(12,8000,'outflow','Inventory'),(20,12000,'outflow','Payroll'),(23,2500,'outflow','Rent'),(26,1700,'outflow','Operations'),(28,300,'outflow','Software')]:
            db.add(Transaction(org_id=org.id,date=start+timedelta(days=day),amount=D(amount),direction=direction,category=category,description=f'{category} · synthetic monthly record',reference=f'seed-{month}-{day}',source='synthetic',currency=org.currency))
    for num,name,amount,days,direction in [('1042','Atlas Market',12600,-18,'receivable'),('1048','Forma Collective',8400,-7,'receivable'),('1053','Juniper Retail',16800,35,'receivable'),('1058','Maison West',6200,47,'receivable'),('2041','Horizon Supply',18500,12,'payable'),('2042','Logistics Partners',3100,21,'payable')]:
        db.add(Invoice(org_id=org.id,number='INV-'+num,counterparty=name,email=name.lower().replace(' ','')+'@example.com',amount=D(amount),paid=D(0),due_date=today+timedelta(days=days),direction=direction))
    db.flush()
def invoices(db,oid): return list(db.scalars(select(Invoice).where(Invoice.org_id==oid)))
def invoice_json(i):
    outstanding=i.amount-i.paid
    return dict(id=i.id,number=i.number,counterparty=i.counterparty,email=i.email,amount=money(i.amount),outstanding=money(outstanding),due_date=str(i.due_date),direction=i.direction,status='paid' if outstanding<=0 else 'overdue' if i.due_date<date.today() else 'unpaid')
def transactions(db,oid): return list(db.scalars(select(Transaction).where(Transaction.org_id==oid).order_by(Transaction.date)))
def current_cash(db,org):
    return org.opening_balance+sum((t.amount if t.direction=='inflow' else -t.amount for t in transactions(db,org.id) if t.date<=date.today()),D(0))
def forecast(db,org,options=None):
    o=options or {}; horizon=int(o.get('horizon_days',90)); today=date.today(); cash=current_cash(db,org)
    reduction=D(str(o.get('expense_reduction_pct',0)))/100
    revenue=D(str(o.get('revenue_change_pct',0)))/100
    schedule={}
    def add(day,amount,direction):
        if today<day<=today+timedelta(days=horizon):
            pair=schedule.setdefault(day,[D(0),D(0)]); pair[0 if direction=='inflow' else 1]+=amount.quantize(CENT,rounding=ROUND_HALF_UP)
    for i in invoices(db,org.id):
        outstanding=i.amount-i.paid
        if outstanding<=0: continue
        if i.direction=='receivable':
            # Overdue collection is uncertain; baseline assumes collection in 30 days.
            due=max(i.due_date,today+timedelta(days=30)) if i.due_date<today else i.due_date
            due+=timedelta(days=int(o.get('payment_delay_days',0))-int(o.get('collection_acceleration_days',0)))
            add(max(due,today+timedelta(days=1)),outstanding,'inflow')
        else: add(max(i.due_date,today+timedelta(days=1))+timedelta(days=int(o.get('payable_delay_days',0))),outstanding,'outflow')
    history=transactions(db,org.id)
    past=[t for t in history if t.date<=today and t.source!='manual_payment' and t.category!='Invoice payment']
    periods=max(1,round(((today-min(t.date for t in past)).days+1)/30)) if past else 1
    retail=sum((t.amount for t in past if t.direction=='inflow'),D(0))/periods
    costs={}
    for t in past:
        if t.direction=='outflow': costs[t.category]=costs.get(t.category,D(0))+t.amount/periods
    # Historical recurring retail activity; open wholesale invoices are additional.
    for offset in range(1,horizon+1):
        dt=today+timedelta(days=offset)
        if offset%30==5: add(dt,retail*D('0.6545454545454545')*(1+revenue),'inflow')
        if offset%30==10: add(dt,retail*(1-D('0.6545454545454545'))*(1+revenue),'inflow')
        for day,amount in [(14,costs.get('Payroll',D(0))),(18,costs.get('Rent',D(0))),(22,costs.get('Operations',D(0))),(25,costs.get('Software',D(0))),(27,costs.get('Inventory',D(0))),(23,sum((v for k,v in costs.items() if k not in ('Payroll','Rent','Operations','Software','Inventory')),D(0)))]:
            if offset%30==day: add(dt,D(amount)*(1-reduction),'outflow')
    add(today+timedelta(days=1),D(str(o.get('purchase_amount',0))),'outflow')
    points=[dict(date=str(today),balance=money(cash),inflow=0.0,outflow=0.0,kind='forecast')]
    minimum=cash; shortfall=None
    for offset in range(1,horizon+1):
        dt=today+timedelta(days=offset); inc,out=schedule.get(dt,[D(0),D(0)])
        cash+=inc-out;minimum=min(minimum,cash)
        if cash<0 and shortfall is None: shortfall=str(dt)
        points.append(dict(date=str(dt),balance=money(cash),inflow=money(inc),outflow=money(out),kind='forecast'))
    return dict(points=points,days_below_zero=sum(p['balance']<0 for p in points),min_balance=money(minimum),shortfall_date=shortfall,horizon_days=horizon,confidence='insufficient history; only recorded commitments' if not past else 'limited history; low confidence scenario assumptions' if periods<2 else 'scenario-based; not a guarantee',assumptions=[f'Historical recurring inflows {money(retail)} and expenses {money(sum(costs.values(),D(0)))} per 30 days, estimated from {periods} observed periods.','Open wholesale invoices are additional to recurring retail sales.','Overdue invoices assumed collected in 30 days; actual collection is uncertain.','No probabilistic uncertainty interval is claimed.'])
def summary(db,org):
    tx=transactions(db,org.id); today=date.today(); recent=[t for t in tx if today-timedelta(days=30)<=t.date<=today]
    inc=sum((t.amount for t in recent if t.direction=='inflow'),D(0));out=sum((t.amount for t in recent if t.direction=='outflow'),D(0));cash=current_cash(db,org)
    inv=invoices(db,org.id); fc=forecast(db,org); bal=org.opening_balance;history=[]
    bydate={}
    for t in tx:
        if t.date<=today:
            pair=bydate.setdefault(t.date,[D(0),D(0)]);pair[0 if t.direction=='inflow' else 1]+=t.amount
    for dt,(i,o) in sorted(bydate.items()):
        bal+=i-o;history.append(dict(date=str(dt),balance=money(bal),inflow=money(i),outflow=money(o),kind='actual'))
    overdue=sum((i.amount-i.paid for i in inv if i.direction=='receivable' and i.due_date<today),D(0))
    upcoming=sum((i.amount-i.paid for i in inv if i.direction=='payable' and i.due_date<=today+timedelta(days=30)),D(0))
    risks=[]
    if fc['shortfall_date']: risks.append(dict(id='liquidity',severity='critical',title='Projected cash shortfall',description='Scheduled supplier obligations arrive before uncertain receivable collections.',date=fc['shortfall_date'],amount=abs(fc['min_balance'])))
    if overdue: risks.append(dict(id='collections',severity='warning',title='Overdue customer invoices',description='Prioritize collections to protect working capital.',date=str(today),amount=money(overdue)))
    metrics=dict(current_cash=money(cash),monthly_net_flow=money(inc-out),projected_30d=fc['points'][30]['balance'],runway_months=money(cash/(out-inc)) if out>inc and cash>0 else None,overdue_receivables=money(overdue),upcoming_obligations=money(upcoming),outstanding_receivables=money(sum((i.amount-i.paid for i in inv if i.direction=='receivable'),D(0))),outstanding_payables=money(sum((i.amount-i.paid for i in inv if i.direction=='payable'),D(0))),monthly_inflows=money(inc),monthly_outflows=money(out))
    return dict(metrics=metrics,history=history,forecast=fc['points'],risks=risks,invoices=[invoice_json(i) for i in inv],assumptions=fc['assumptions'],demo=org.demo,currency=org.currency,as_of=str(today))
