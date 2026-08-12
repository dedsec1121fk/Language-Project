from pathlib import Path
import json, re
from .registry import ROOT
CATALOG=ROOT/'catalog'/'known_languages.json'
def load_catalog():
    if not CATALOG.exists(): return {'languages':[],'count':0}
    return json.loads(CATALOG.read_text())
def search_catalog(query):
    q=query.casefold().strip(); out=[]
    for x in load_catalog().get('languages',[]):
        hay=' '.join([x.get('name',''),*x.get('aliases',[]),*x.get('extensions',[])]).casefold()
        if q in hay: out.append(x)
    return out
def catalog_stats():
    xs=load_catalog().get('languages',[])
    return {'total':len(xs),'termux_workers':sum(bool(x.get('termux_worker')) for x in xs),'catalog_only':sum(not x.get('termux_worker') for x in xs),'letters':len({x.get('letter') for x in xs})}
