#!/usr/bin/env python3
from pathlib import Path
import sys,subprocess,json,shutil,os,time,platform,datetime
import select
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core.registry import load_registry,expand,executable_exists,command_version
STATE=ROOT/'state'/'active.json'
TEST_VECTORS=[
 '466c65782050726f6a656374',
 '00ff0102037f80fe',
 'ce95cebbcebbceb7cebdceb9cebaceac',
 'f09f9aa000112233445566778899aabbccddeeff'
]
def run(c,timeout=1200,quiet=False):
 if not quiet:print('  $',' '.join(map(str,c)))
 try:return subprocess.run(c,cwd=ROOT,timeout=timeout).returncode==0
 except Exception as e:
  if not quiet:print('  !',e)
  return False
def installed_pkg(p):
 if shutil.which('dpkg') is None:return False
 return subprocess.run(['dpkg','-s',p],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
def install_pkg(p):
 if installed_pkg(p):return True
 if shutil.which('pkg') is None:return False
 return run(['pkg','install','-y',p])
def _readline_timeout(pipe, timeout=6):
 fd=pipe.fileno()
 ready,_,_=select.select([fd],[],[],timeout)
 if not ready: raise TimeoutError(f'worker response timeout after {timeout}s')
 line=pipe.readline()
 if line=='': raise RuntimeError('worker exited before responding')
 return line.rstrip('\r\n')
def worker_test(lang):
 started=time.perf_counter_ns(); p=None
 try:
  p=subprocess.Popen(expand(lang['run']),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=ROOT)
  p.stdin.write('PING\n');p.stdin.flush();pong=_readline_timeout(p.stdout).strip()
  if pong!='PONG':return False,f'PING failed: {pong!r}',None
  samples=[]
  for sample in TEST_VECTORS:
   t=time.perf_counter_ns();p.stdin.write('E '+sample+'\n');p.stdin.flush();enc=_readline_timeout(p.stdout).strip().lower()
   if len(enc)!=len(sample) or any(c not in '0123456789abcdef' for c in enc):return False,'invalid encoded hex',None
   p.stdin.write('D '+enc+'\n');p.stdin.flush();dec=_readline_timeout(p.stdout).strip().lower();samples.append(time.perf_counter_ns()-t)
   if dec!=sample.lower():return False,'round-trip mismatch',None
  p.stdin.write('QUIT\n');p.stdin.flush();p.wait(timeout=4)
  return True,'ok',{'startup_and_test_ns':time.perf_counter_ns()-started,'median_vector_ns':sorted(samples)[len(samples)//2]}
 except Exception as e:return False,str(e),None
 finally:
  if p and p.poll() is None:
   try:p.kill()
   except Exception:pass
def main():
 install='--install' in sys.argv; update='--update' in sys.argv; refresh='--refresh-catalog' in sys.argv
 termux=bool(shutil.which('pkg')) and 'com.termux' in os.environ.get('PREFIX','')
 if install and shutil.which('pkg'):
  print('Updating Termux package indexes...');run(['pkg','update','-y'])
  if update:run(['pkg','upgrade','-y'],timeout=2400)
 (ROOT/'build'/'java').mkdir(parents=True,exist_ok=True);(ROOT/'build'/'scala').mkdir(parents=True,exist_ok=True)
 active=[];failed={};versions={};metrics={};installed=set();package_status={};build_metrics={};registry=load_registry()
 for i,l in enumerate(registry,1):
  print(f"\n[{i:02d}/{len(registry):02d}] {l['name']} ({l['kind']})")
  if install:
   for pkg in l.get('packages',[]):
    if pkg in installed:continue
    if install_pkg(pkg): installed.add(pkg);package_status[pkg]='installed'
    else: package_status[pkg]='failed-or-unavailable';print(f'  ! package unavailable/failed: {pkg}')
  if l.get('build'):
   cmd=expand(l['build']);tool=cmd[0];build_started=time.perf_counter_ns()
   if shutil.which(tool) is None:
    failed[l['id']]=f'missing build tool: {tool}';print('  SKIP',failed[l['id']]);continue
   if not run(cmd):failed[l['id']]='build failed';build_metrics[l['id']]={'ok':False,'duration_ns':time.perf_counter_ns()-build_started};print('  SKIP build failed');continue
   build_metrics[l['id']]={'ok':True,'duration_ns':time.perf_counter_ns()-build_started}
  if not executable_exists(l['run']):failed[l['id']]='runtime missing';print('  SKIP runtime missing');continue
  ok,msg,metric=worker_test(l)
  if ok:
   active.append(l['id']);versions[l['id']]=command_version(l);metrics[l['id']]=metric;print('  VERIFIED')
  else:failed[l['id']]=msg;print('  SKIP',msg)
 state={
  'schema':3,'project':'Language Project','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'active':active,'failed':failed,'versions':versions,'metrics':metrics,'registry_count':len(registry),'validation_vectors':len(TEST_VECTORS),
  'package_status':package_status,'build_metrics':build_metrics,'installed_package_count':len(installed),
  'termux':termux,'prefix':os.environ.get('PREFIX',''),'machine':platform.machine(),'platform':platform.platform(),
  'python':platform.python_version()
 }
 STATE.parent.mkdir(exist_ok=True);STATE.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
 if refresh:
  print('\nRefreshing global language catalog (best effort)...')
  subprocess.run([sys.executable,str(ROOT/'scripts'/'refresh_catalog.py')],cwd=ROOT)
 print('\n'+'='*68);print(f'VERIFIED EXECUTABLE WORKERS: {len(active)}/{len(registry)}')
 if failed:print('Skipped:',', '.join(failed))
 print('State:',STATE);print('='*68)
 return 0 if active else 1
if __name__=='__main__':raise SystemExit(main())
