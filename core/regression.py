from __future__ import annotations
from .store import recent

def check(mode='chain',threshold_pct=15.0):
    rows=[x for x in recent(20,mode) if x.get('duration_ns')]
    if len(rows)<2:return {'ok':False,'reason':f'Need at least two stored {mode} sessions with comparable duration metrics.','mode':mode}
    new,old=rows[0],rows[1];a=old['duration_ns'];b=new['duration_ns'];delta=((b-a)/a*100.0) if a else 0.0
    return {'ok':bool(new.get('integrity')) and delta<=threshold_pct,'mode':mode,'threshold_pct':float(threshold_pct),'old_session':old['session_id'],'new_session':new['session_id'],'old_ns':a,'new_ns':b,'delta_pct':delta,'integrity':bool(new.get('integrity'))}

def print_check(r):
    if 'delta_pct' not in r:print(r.get('reason','No comparison available.'));return r
    state='PASS' if r['ok'] else 'FAIL';print(f"Regression gate {state}: {r['mode']} {r['old_ns']/1e6:.4f} -> {r['new_ns']/1e6:.4f} ms ({r['delta_pct']:+.2f}%), threshold +{r['threshold_pct']:.2f}%")
    return r
