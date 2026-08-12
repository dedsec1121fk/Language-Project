#!/usr/bin/env python3
import json,sys
if len(sys.argv)<2 or sys.argv[1]=='--help': print('Usage: jsonl-check FILE  # validate JSON Lines and count top-level types'); raise SystemExit(0 if len(sys.argv)>1 else 2)
counts={}; errors=[]; rows=0
with open(sys.argv[1],encoding='utf-8',errors='replace') as f:
 for n,line in enumerate(f,1):
  if not line.strip(): continue
  rows+=1
  try:
   v=json.loads(line); t='null' if v is None else type(v).__name__; counts[t]=counts.get(t,0)+1
  except Exception as e: errors.append({'line':n,'error':str(e)})
print(json.dumps({'rows':rows,'valid':rows-len(errors),'invalid':len(errors),'types':counts,'errors':errors[:25]},indent=2))
raise SystemExit(1 if errors else 0)
