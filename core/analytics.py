from __future__ import annotations
from pathlib import Path
import hashlib, math, os, platform, statistics, subprocess, time


def percentile(values, pct):
    if not values:
        return 0
    vals=sorted(values)
    if len(vals)==1:
        return int(vals[0])
    pos=(len(vals)-1)*(pct/100.0)
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi:
        return int(vals[lo])
    return int(vals[lo]+(vals[hi]-vals[lo])*(pos-lo))


def timing_stats(values, payload_bytes=0):
    vals=[int(v) for v in values]
    if not vals:
        return {'samples':0,'min_ns':0,'p50_ns':0,'median_ns':0,'p90_ns':0,'p95_ns':0,'p99_ns':0,'mean_ns':0,'stdev_ns':0,'max_ns':0,'jitter_pct':0.0,'throughput_mib_s':0.0}
    mean=statistics.fmean(vals)
    stdev=statistics.pstdev(vals) if len(vals)>1 else 0.0
    median=int(statistics.median(vals))
    throughput=(payload_bytes/(1024*1024))/(median/1e9) if payload_bytes and median else 0.0
    return {
        'samples':len(vals),'min_ns':min(vals),'p50_ns':median,'median_ns':median,
        'p90_ns':percentile(vals,90),'p95_ns':percentile(vals,95),'p99_ns':percentile(vals,99),
        'mean_ns':int(mean),'stdev_ns':int(stdev),'max_ns':max(vals),
        'jitter_pct':(stdev/mean*100.0) if mean else 0.0,'throughput_mib_s':throughput,
    }


def shannon_entropy(data:bytes):
    if not data:
        return 0.0
    counts=[0]*256
    for b in data: counts[b]+=1
    n=len(data)
    return -sum((c/n)*math.log2(c/n) for c in counts if c)


def _read_first(path):
    try:return Path(path).read_text(errors='ignore').strip()
    except Exception:return ''


def _cmd(cmd):
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=3)
        return (r.stdout or r.stderr).strip()
    except Exception:return ''


def thermal_snapshot():
    zones=[]
    root=Path('/sys/class/thermal')
    if root.exists():
        for z in sorted(root.glob('thermal_zone*'))[:32]:
            try:
                raw=(z/'temp').read_text().strip(); value=float(raw)
                if abs(value)>1000:value/=1000.0
                typ=_read_first(z/'type') or z.name
                if -50 <= value <= 250: zones.append({'zone':z.name,'type':typ,'celsius':round(value,2)})
            except Exception:pass
    return zones


def memory_snapshot():
    info={}
    text=_read_first('/proc/meminfo')
    for line in text.splitlines():
        if ':' not in line:continue
        k,v=line.split(':',1);parts=v.strip().split()
        try:
            n=int(parts[0]);info[k]=n*1024 if len(parts)>1 and parts[1].lower()=='kb' else n
        except Exception:pass
    return {k:info.get(k,0) for k in ('MemTotal','MemAvailable','SwapTotal','SwapFree')}


def device_snapshot():
    uname=platform.uname()
    android_release=_cmd(['getprop','ro.build.version.release']) if os.environ.get('ANDROID_ROOT') else ''
    android_sdk=_cmd(['getprop','ro.build.version.sdk']) if os.environ.get('ANDROID_ROOT') else ''
    model=_cmd(['getprop','ro.product.model']) if os.environ.get('ANDROID_ROOT') else ''
    manufacturer=_cmd(['getprop','ro.product.manufacturer']) if os.environ.get('ANDROID_ROOT') else ''
    return {
        'platform':platform.platform(),'system':uname.system,'release':uname.release,'machine':uname.machine,
        'processor':platform.processor(),'cpu_count':os.cpu_count(),'python':platform.python_version(),
        'termux_prefix':os.environ.get('PREFIX',''),'termux_version':os.environ.get('TERMUX_VERSION',''),
        'android_root':os.environ.get('ANDROID_ROOT',''),'android_release':android_release,'android_sdk':android_sdk,
        'manufacturer':manufacturer,'model':model,'loadavg':list(os.getloadavg()) if hasattr(os,'getloadavg') else [],
        'memory':memory_snapshot(),'thermal':thermal_snapshot(),
    }


def session_id(mode, data=b'', salt=''):
    base=f'{mode}:{time.time_ns()}:{os.getpid()}:{salt}'.encode()+hashlib.sha256(data).digest()
    return hashlib.sha256(base).hexdigest()[:16]
