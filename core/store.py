from __future__ import annotations
from pathlib import Path
import sqlite3,json,datetime
from .registry import ROOT
from .paths import DATABASE_FILE, RESULTS_DIR
DB=DATABASE_FILE

SCHEMA='''
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS sessions(
 session_id TEXT PRIMARY KEY,
 timestamp TEXT NOT NULL,
 mode TEXT NOT NULL,
 bytes INTEGER NOT NULL DEFAULT 0,
 languages INTEGER NOT NULL DEFAULT 0,
 integrity INTEGER,
 duration_ns INTEGER,
 result_path TEXT,
 device TEXT,
 metadata TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_mode ON sessions(mode,timestamp DESC);
CREATE TABLE IF NOT EXISTS stages(
 session_id TEXT NOT NULL,
 language_id TEXT NOT NULL,
 language_name TEXT,
 rank INTEGER,
 median_ns INTEGER,
 p95_ns INTEGER,
 throughput_mib_s REAL,
 integrity INTEGER,
 PRIMARY KEY(session_id,language_id),
 FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_stages_lang ON stages(language_id,median_ns);
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 session_id TEXT,
 timestamp TEXT NOT NULL,
 event_type TEXT NOT NULL,
 payload TEXT NOT NULL
);
'''

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(DB,timeout=10)
    con.executescript(SCHEMA)
    return con

def _duration(r):
    if isinstance(r.get('total_ns'),(int,float)):return int(r['total_ns'])
    if isinstance(r.get('stats'),dict) and r['stats'].get('median_ns') is not None:return int(r['stats']['median_ns'])
    if r.get('rounds_detail'):
        return int(sum(x.get('total_ns',0) for x in r['rounds_detail']))
    return None

def _stage_rows(r):
    rows=r.get('ranking') or r.get('stages') or []
    out=[]
    for rank,x in enumerate(rows,1):
        med=x.get('combined_median_ns',x.get('median_ns'))
        p95=x.get('combined_p95_ns',x.get('p95_ns'))
        if med is None and isinstance(x.get('combined'),dict):med=x['combined'].get('median_ns')
        if p95 is None and isinstance(x.get('combined'),dict):p95=x['combined'].get('p95_ns')
        thr=x.get('throughput_mib_s')
        if thr is None and isinstance(x.get('combined'),dict):thr=x['combined'].get('throughput_mib_s')
        out.append((x.get('id',''),x.get('name',''),rank,int(med or 0),int(p95 or 0),float(thr or 0.0),None if x.get('integrity') is None else int(bool(x.get('integrity')))))
    return out

def record_result(r:dict,result_path:str|None=None):
    sid=r.get('session_id')
    if not sid:return
    with connect() as con:
        con.execute('''INSERT OR REPLACE INTO sessions(session_id,timestamp,mode,bytes,languages,integrity,duration_ns,result_path,device,metadata)
                       VALUES(?,?,?,?,?,?,?,?,?,?)''',(
            sid,r.get('timestamp') or datetime.datetime.now(datetime.timezone.utc).isoformat(),r.get('mode','unknown'),int(r.get('bytes',0) or 0),int(r.get('languages',0) or 0),
            None if r.get('integrity') is None else int(bool(r.get('integrity'))),_duration(r),result_path,json.dumps(r.get('device',{}),ensure_ascii=False),json.dumps(r,ensure_ascii=False)))
        con.execute('DELETE FROM stages WHERE session_id=?',(sid,))
        for lid,name,rank,med,p95,thr,ok in _stage_rows(r):
            con.execute('INSERT OR REPLACE INTO stages VALUES(?,?,?,?,?,?,?,?)',(sid,lid,name,rank,med,p95,thr,ok))

def record_event(session_id,event_type,payload):
    with connect() as con:
        con.execute('INSERT INTO events(session_id,timestamp,event_type,payload) VALUES(?,?,?,?)',(session_id,datetime.datetime.now(datetime.timezone.utc).isoformat(),event_type,json.dumps(payload,ensure_ascii=False)))

def rebuild():
    count=0
    for p in sorted(RESULTS_DIR.glob('*.json')):
        try:
            r=json.loads(p.read_text());record_result(r,str(p));count+=1
        except Exception:pass
    return count

def stats():
    with connect() as con:
        sessions=con.execute('SELECT COUNT(*),SUM(CASE WHEN integrity=1 THEN 1 ELSE 0 END),COALESCE(SUM(bytes),0),COUNT(DISTINCT mode) FROM sessions').fetchone()
        stages=con.execute('SELECT COUNT(*),COUNT(DISTINCT language_id) FROM stages').fetchone()
        modes=con.execute('SELECT mode,COUNT(*),COALESCE(AVG(duration_ns),0) FROM sessions GROUP BY mode ORDER BY COUNT(*) DESC').fetchall()
    return {'database':str(DB),'sessions':sessions[0],'successful_sessions':sessions[1] or 0,'total_payload_bytes':sessions[2],'modes':sessions[3],'stage_measurements':stages[0],'languages_measured':stages[1],'mode_summary':[{'mode':x[0],'runs':x[1],'avg_duration_ns':int(x[2] or 0)} for x in modes]}

def leaderboard(limit=50,min_samples=1,mode='chain'):
    with connect() as con:
        if mode and mode!='*':
            rows=con.execute('''SELECT st.language_id,MAX(st.language_name),COUNT(*),AVG(st.median_ns),MIN(st.median_ns),AVG(st.p95_ns),AVG(st.throughput_mib_s),AVG(COALESCE(st.integrity,1))
                                FROM stages st JOIN sessions se ON se.session_id=st.session_id WHERE se.mode=? GROUP BY st.language_id HAVING COUNT(*)>=? ORDER BY AVG(st.median_ns) ASC LIMIT ?''',(mode,int(min_samples),int(limit))).fetchall()
        else:
            rows=con.execute('''SELECT language_id,MAX(language_name),COUNT(*),AVG(median_ns),MIN(median_ns),AVG(p95_ns),AVG(throughput_mib_s),AVG(COALESCE(integrity,1))
                                FROM stages GROUP BY language_id HAVING COUNT(*)>=? ORDER BY AVG(median_ns) ASC LIMIT ?''',(int(min_samples),int(limit))).fetchall()
    return [{'id':r[0],'name':r[1] or r[0],'samples':r[2],'avg_median_ns':int(r[3] or 0),'best_median_ns':int(r[4] or 0),'avg_p95_ns':int(r[5] or 0),'avg_throughput_mib_s':float(r[6] or 0),'integrity_rate':float(r[7] or 0),'mode':mode or '*'} for r in rows]

def recent(limit=20,mode=None):
    with connect() as con:
        if mode:rows=con.execute('SELECT session_id,timestamp,mode,bytes,languages,integrity,duration_ns,result_path FROM sessions WHERE mode=? ORDER BY timestamp DESC LIMIT ?',(mode,int(limit))).fetchall()
        else:rows=con.execute('SELECT session_id,timestamp,mode,bytes,languages,integrity,duration_ns,result_path FROM sessions ORDER BY timestamp DESC LIMIT ?',(int(limit),)).fetchall()
    keys=['session_id','timestamp','mode','bytes','languages','integrity','duration_ns','result_path']
    return [dict(zip(keys,r)) for r in rows]
