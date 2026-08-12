from pathlib import Path
import json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'languages.json'
def load_registry(): return json.loads(REGISTRY.read_text())['languages']
def expand(parts): return [str(x).replace('{root}',str(ROOT)) for x in parts]
def executable_exists(cmd):
    p=expand(cmd)[0]
    return Path(p).exists() if '/' in p else shutil.which(p) is not None
def command_version(lang):
    cmd=expand(lang['run']); exe=Path(cmd[0]).name
    probes={
      'python':['python','--version'],'node':['node','--version'],'perl':['perl','-v'],'ruby':['ruby','--version'],
      'lua':['lua','-v'],'php':['php','-v'],'go':['go','version'],
      'java':['java','-version'],'guile':['guile','--version'],'escript':['erl','-noshell','-eval','io:format("~s",[erlang:system_info(otp_release)]),halt().'],
      'elixir':['elixir','--version'],'swipl':['swipl','--version'],'scala':['scala','-version'],'dart':['dart','--version'],
      'dash':['dash','-c','echo dash'],'zsh':['zsh','--version'],'fish':['fish','--version'],'sed':['sed','--version'],'jq':['jq','--version']
    }
    c=probes.get(exe,[cmd[0],'--version'])
    try:
      if exe=='tclsh': r=subprocess.run(['tclsh'],input='puts $tcl_version\nexit\n',capture_output=True,text=True,timeout=8,cwd=ROOT)
      else: r=subprocess.run(c,capture_output=True,text=True,timeout=8,cwd=ROOT)
      text=(r.stdout or r.stderr).strip().splitlines()
      return text[0][:200] if text else 'available'
    except Exception:return 'unknown'
