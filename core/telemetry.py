from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os, threading, time, statistics


def _read_text(path):
    try:
        return Path(path).read_text(errors='ignore')
    except Exception:
        return ''


def _proc_rss_bytes():
    text=_read_text('/proc/self/status')
    for line in text.splitlines():
        if line.startswith('VmRSS:'):
            try:return int(line.split()[1])*1024
            except Exception:return 0
    return 0


def _mem_available_bytes():
    text=_read_text('/proc/meminfo')
    for line in text.splitlines():
        if line.startswith('MemAvailable:'):
            try:return int(line.split()[1])*1024
            except Exception:return 0
    return 0


def _thermal_max_c():
    vals=[]
    root=Path('/sys/class/thermal')
    if root.exists():
        for p in root.glob('thermal_zone*/temp'):
            try:
                v=float(p.read_text().strip())
                if abs(v)>1000:v/=1000.0
                if -50<=v<=250:vals.append(v)
            except Exception:pass
    return max(vals) if vals else None


def _cpu_ticks():
    try:
        parts=_read_text('/proc/stat').splitlines()[0].split()[1:]
        vals=[int(x) for x in parts]
        idle=vals[3]+(vals[4] if len(vals)>4 else 0)
        return sum(vals),idle
    except Exception:return None


@dataclass
class ResourceSampler:
    interval: float = 0.25
    samples: list[dict] = field(default_factory=list)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: threading.Thread|None = field(default=None, init=False)
    _started_ns: int = field(default=0, init=False)

    def start(self):
        if self._thread and self._thread.is_alive():return self
        self._stop.clear();self._started_ns=time.perf_counter_ns()
        self._thread=threading.Thread(target=self._loop,name='language-project-telemetry',daemon=True)
        self._thread.start();return self

    def _loop(self):
        last=_cpu_ticks()
        while not self._stop.is_set():
            now=time.perf_counter_ns();cur=_cpu_ticks();cpu=None
            if last and cur:
                dt=cur[0]-last[0];di=cur[1]-last[1]
                if dt>0:cpu=max(0.0,min(100.0,(dt-di)/dt*100.0))
            last=cur
            load=list(os.getloadavg()) if hasattr(os,'getloadavg') else []
            self.samples.append({
                't_ns':now-self._started_ns,'rss_bytes':_proc_rss_bytes(),'mem_available_bytes':_mem_available_bytes(),
                'cpu_percent':cpu,'load1':load[0] if load else None,'thermal_max_c':_thermal_max_c(),
            })
            self._stop.wait(max(0.05,float(self.interval)))

    def stop(self):
        self._stop.set()
        if self._thread:self._thread.join(timeout=max(1.0,self.interval*4))
        return self.summary()

    def summary(self):
        rows=self.samples
        def nums(k):return [float(x[k]) for x in rows if x.get(k) is not None]
        def stat(k,fn,default=None):
            v=nums(k);return fn(v) if v else default
        return {
            'samples':len(rows),'interval_ms':self.interval*1000.0,
            'duration_ms':((rows[-1]['t_ns']-rows[0]['t_ns'])/1e6) if len(rows)>1 else 0.0,
            'rss_peak_bytes':int(stat('rss_bytes',max,0) or 0),
            'rss_median_bytes':int(stat('rss_bytes',statistics.median,0) or 0),
            'mem_available_min_bytes':int(stat('mem_available_bytes',min,0) or 0),
            'cpu_mean_percent':round(stat('cpu_percent',statistics.fmean,0.0) or 0.0,3),
            'cpu_peak_percent':round(stat('cpu_percent',max,0.0) or 0.0,3),
            'load1_peak':round(stat('load1',max,0.0) or 0.0,3),
            'thermal_start_c':nums('thermal_max_c')[0] if nums('thermal_max_c') else None,
            'thermal_end_c':nums('thermal_max_c')[-1] if nums('thermal_max_c') else None,
            'thermal_peak_c':stat('thermal_max_c',max,None),
        }
