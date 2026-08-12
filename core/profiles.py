from __future__ import annotations
from .registry import ROOT
import json
PROFILE_FILE=ROOT/'config'/'benchmark_profiles.json'

def load_profiles():
    return json.loads(PROFILE_FILE.read_text())

def get_profile(name):
    data=load_profiles(); profiles=data.get('profiles',{})
    if name not in profiles: raise KeyError(f"Unknown profile {name!r}. Available: {', '.join(profiles)}")
    return profiles[name]

def print_profiles():
    data=load_profiles();print('\nLanguage Project benchmark profiles\n')
    for name,p in data.get('profiles',{}).items():
        print(f"{name:<12} {p.get('description','')}")
        print(f"             chain rounds={p['chain']['rounds']} warmups={p['chain']['warmups']} | race iterations={p['race']['iterations']} | matrix sizes={p['matrix']['sizes']} | stress cycles={p['stress']['cycles']}")
