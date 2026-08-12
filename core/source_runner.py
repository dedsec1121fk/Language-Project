from pathlib import Path
import shutil,subprocess,tempfile,os

INTERPRETED={
 '.py':['python'],'.js':['node'],'.mjs':['node'],'.rb':['ruby'],'.pl':['perl'],'.lua':['lua'],'.php':['php'],'.tcl':['tclsh'],'.sh':['bash'],'.zsh':['zsh'],'.fish':['fish'],'.dart':['dart','run'],'.exs':['elixir'],'.rkt':['racket'],'.scm':['guile','-s'],'.pro':['swipl','-q','-f'],'.awk':['awk','-f']
}

def _need(cmd):
    if shutil.which(cmd) is None:raise RuntimeError(f'Required runtime/compiler not found: {cmd}')

def run_source(path,args=None,timeout=30,stdin_data=None):
    p=Path(path).expanduser().resolve();args=list(args or [])
    if not p.is_file():raise FileNotFoundError(p)
    ext=p.suffix.lower()
    with tempfile.TemporaryDirectory(prefix='language-project-run-') as td:
        t=Path(td);cmd=None
        if ext in INTERPRETED:
            cmd=INTERPRETED[ext]+[str(p)]+args
        elif ext=='.c':
            _need('clang');exe=t/'app';subprocess.run(['clang','-O2',str(p),'-o',str(exe)],check=True,timeout=timeout);cmd=[str(exe)]+args
        elif ext in {'.cc','.cpp','.cxx'}:
            _need('clang++');exe=t/'app';subprocess.run(['clang++','-O2',str(p),'-o',str(exe)],check=True,timeout=timeout);cmd=[str(exe)]+args
        elif ext=='.rs':
            _need('rustc');exe=t/'app';subprocess.run(['rustc','-O',str(p),'-o',str(exe)],check=True,timeout=timeout);cmd=[str(exe)]+args
        elif ext=='.go':
            _need('go');cmd=['go','run',str(p)]+args
        elif ext=='.java':
            _need('javac');_need('java');subprocess.run(['javac','-d',str(t),str(p)],check=True,timeout=timeout);cmd=['java','-cp',str(t),p.stem]+args
        elif ext=='.kt':
            _need('kotlinc');_need('java');jar=t/'app.jar';subprocess.run(['kotlinc',str(p),'-include-runtime','-d',str(jar)],check=True,timeout=timeout);cmd=['java','-jar',str(jar)]+args
        elif ext=='.nim':
            _need('nim');exe=t/'app';subprocess.run(['nim','c','-d:release',f'-o:{exe}',str(p)],check=True,timeout=timeout,stdout=subprocess.PIPE,stderr=subprocess.PIPE);cmd=[str(exe)]+args
        elif ext=='.zig':
            _need('zig');exe=t/'app';subprocess.run(['zig','build-exe','-O','ReleaseFast',str(p),f'-femit-bin={exe}'],check=True,timeout=timeout);cmd=[str(exe)]+args
        elif ext=='.d':
            compiler=shutil.which('ldc2') or shutil.which('gdc') or shutil.which('dmd')
            if not compiler:raise RuntimeError('No D compiler found (ldc2/gdc/dmd)')
            exe=t/'app';subprocess.run([compiler,str(p),'-of='+str(exe)],check=True,timeout=timeout);cmd=[str(exe)]+args
        elif ext in {'.f90','.f95','.f03','.f08','.f'}:
            compiler=shutil.which('flang-new') or shutil.which('flang') or shutil.which('gfortran')
            if not compiler:raise RuntimeError('No Fortran compiler found')
            exe=t/'app';subprocess.run([compiler,str(p),'-O2','-o',str(exe)],check=True,timeout=timeout);cmd=[str(exe)]+args
        else:raise ValueError(f'Unsupported source extension: {ext or "(none)"}')
        _need(cmd[0]) if '/' not in cmd[0] else None
        r=subprocess.run(cmd,input=stdin_data,capture_output=True,timeout=timeout,cwd=p.parent)
        return {'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
