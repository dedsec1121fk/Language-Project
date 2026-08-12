from __future__ import annotations
from pathlib import Path
import importlib.util,os,traceback
from .registry import ROOT
PLUGINS=ROOT/'plugins'

def enabled():return os.environ.get('LANGUAGE_PROJECT_PLUGINS','').strip().lower() in {'1','true','yes','on'}

def load_plugins():
    if not enabled() or not PLUGINS.exists():return []
    out=[]
    for p in sorted(PLUGINS.glob('*.py')):
        if p.name.startswith('_'):continue
        try:
            spec=importlib.util.spec_from_file_location('language_project_plugin_'+p.stem,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);out.append((p.stem,m))
        except Exception as e:out.append((p.stem,e))
    return out

def emit(event,context):
    errors=[]
    for name,obj in load_plugins():
        if isinstance(obj,Exception):errors.append({'plugin':name,'error':str(obj)});continue
        fn=getattr(obj,event,None)
        if callable(fn):
            try:fn(context)
            except Exception as e:errors.append({'plugin':name,'error':f'{type(e).__name__}: {e}'})
    return errors
