from __future__ import annotations

from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import tempfile
import time

from .polyglot_ops import (
    FORMAT,
    FORMAT_VERSION,
    DEFAULT_CHUNK,
    _close,
    _file_probe,
    _full_roundtrip,
    _chain_decode,
    _language_metadata,
    _sha256_file,
    _start,
    verify_directory_audit,
    verify_seal,
    verified_copy,
)


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _iter_files(root: Path, hidden=False):
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root)
        if not hidden and any(part.startswith('.') for part in rel.parts):
            continue
        yield p, rel


def _roundtrip_probe(workers, path: Path, sample_bytes=32768):
    probe, sha, size = _file_probe(path, sample_bytes)
    encoded, recovered, stages = _full_roundtrip(workers, probe)
    if recovered != probe:
        raise RuntimeError(f'All-language probe failed for {path}')
    return {
        'bytes': size,
        'sha256': sha,
        'probe_bytes': len(probe),
        'encoded_probe_sha256': hashlib.sha256(encoded).hexdigest(),
        'roundtrip_ns': sum(x['combined_ns'] for x in stages),
    }


def compare_paths(a, b, sample_bytes=32768, order='registry', warmups=1, hidden=False):
    """Compare files/directories while every active language validates content-bound probes."""
    a = Path(a).expanduser().resolve(); b = Path(b).expanduser().resolve()
    if not a.exists() or not b.exists():
        raise FileNotFoundError(a if not a.exists() else b)
    if a.is_file() != b.is_file():
        raise ValueError('Both paths must be the same kind: file/file or directory/directory')
    workers = _start(order, warmups=warmups)
    started = time.perf_counter_ns()
    try:
        if a.is_file():
            left = _roundtrip_probe(workers, a, sample_bytes)
            right = _roundtrip_probe(workers, b, sample_bytes)
            return {
                'ok': True,
                'type': 'file-compare',
                'left': str(a), 'right': str(b),
                'equal': left['bytes'] == right['bytes'] and left['sha256'] == right['sha256'],
                'left_info': left, 'right_info': right,
                'languages': len(workers), 'language_order': [w.lang['id'] for w in workers],
                'total_ns': time.perf_counter_ns() - started,
            }
        amap = {rel.as_posix(): p for p, rel in _iter_files(a, hidden)}
        bmap = {rel.as_posix(): p for p, rel in _iter_files(b, hidden)}
        rows = []
        for rel in sorted(set(amap) | set(bmap)):
            if rel not in amap:
                info = _roundtrip_probe(workers, bmap[rel], sample_bytes)
                rows.append({'path': rel, 'status': 'only-right', 'right': info})
            elif rel not in bmap:
                info = _roundtrip_probe(workers, amap[rel], sample_bytes)
                rows.append({'path': rel, 'status': 'only-left', 'left': info})
            else:
                li = _roundtrip_probe(workers, amap[rel], sample_bytes)
                ri = _roundtrip_probe(workers, bmap[rel], sample_bytes)
                same = li['bytes'] == ri['bytes'] and li['sha256'] == ri['sha256']
                rows.append({'path': rel, 'status': 'same' if same else 'changed', 'left': li, 'right': ri})
        counts = {k: sum(1 for r in rows if r['status'] == k) for k in ('same','changed','only-left','only-right')}
        return {
            'ok': True, 'type': 'directory-compare', 'left': str(a), 'right': str(b),
            'equal': counts['changed'] == 0 and counts['only-left'] == 0 and counts['only-right'] == 0,
            'counts': counts, 'files': rows,
            'languages': len(workers), 'language_order': [w.lang['id'] for w in workers],
            'total_ns': time.perf_counter_ns() - started,
        }
    finally:
        _close(workers)


def _copy_file_with_workers(source: Path, destination: Path, workers, chunk_size=DEFAULT_CHUNK):
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + '.language-project.part')
    if tmp.exists(): tmp.unlink()
    src_hash = hashlib.sha256(); dst_hash = hashlib.sha256(); chunks = 0; transforms = 0
    try:
        with source.open('rb') as src, tmp.open('wb') as dst:
            while True:
                chunk = src.read(chunk_size)
                if not chunk: break
                src_hash.update(chunk)
                _, recovered, _ = _full_roundtrip(workers, chunk)
                if recovered != chunk:
                    raise RuntimeError(f'All-language copy failed: {source} chunk {chunks}')
                dst.write(recovered); dst_hash.update(recovered)
                chunks += 1; transforms += len(workers) * 2
        if src_hash.digest() != dst_hash.digest():
            raise RuntimeError(f'Final SHA-256 mismatch copying {source}')
        os.replace(tmp, destination)
        try: shutil.copystat(source, destination, follow_symlinks=False)
        except OSError: pass
    except Exception:
        if tmp.exists(): tmp.unlink()
        raise
    return {'bytes': source.stat().st_size, 'chunks': chunks, 'sha256': src_hash.hexdigest(), 'transformations': transforms}


def mirror_directory(source, destination, apply=False, delete=False, checksum=True, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1, hidden=False):
    """Plan or perform a verified directory mirror. Mutations require apply=True."""
    source = Path(source).expanduser().resolve(); destination = Path(destination).expanduser().resolve()
    if not source.is_dir(): raise ValueError('mirror source must be a directory')
    if source == destination or source in destination.parents:
        raise ValueError('destination must be outside source')
    if destination.exists() and not destination.is_dir():
        raise ValueError('mirror destination must be a directory or not exist')
    if apply:
        destination.mkdir(parents=True, exist_ok=True)
    smap = {rel.as_posix(): p for p, rel in _iter_files(source, hidden)}
    dmap = {rel.as_posix(): p for p, rel in _iter_files(destination, hidden)} if destination.is_dir() else {}
    to_copy=[]; unchanged=[]
    for rel,p in smap.items():
        q=dmap.get(rel)
        if q is None: to_copy.append((rel,'new'))
        elif p.stat().st_size != q.stat().st_size: to_copy.append((rel,'changed'))
        elif checksum and _sha256_file(p) != _sha256_file(q): to_copy.append((rel,'changed'))
        elif not checksum and int(p.stat().st_mtime) != int(q.stat().st_mtime): to_copy.append((rel,'changed'))
        else: unchanged.append(rel)
    extras=sorted(set(dmap)-set(smap))
    workers = _start(order, warmups=warmups)
    started=time.perf_counter_ns(); copied=[]; removed=[]
    try:
        # Even a pure dry run/no-change plan is authenticated by every language.
        plan_bytes=json.dumps({'copy':to_copy,'extras':extras,'delete':bool(delete)},sort_keys=True).encode()
        _, recovered, _=_full_roundtrip(workers, hashlib.sha256(plan_bytes).digest())
        if recovered != hashlib.sha256(plan_bytes).digest(): raise RuntimeError('Polyglot mirror plan verification failed')
        if apply:
            for rel,reason in to_copy:
                info=_copy_file_with_workers(smap[rel], destination/rel, workers, chunk_size)
                copied.append({'path':rel,'reason':reason,**info})
            if delete:
                for rel in extras:
                    p=destination/rel
                    if p.is_file() and not p.is_symlink():
                        p.unlink(); removed.append(rel)
                # Remove now-empty directories, deepest first, never the root.
                for d in sorted((p for p in destination.rglob('*') if p.is_dir()), key=lambda x: len(x.parts), reverse=True):
                    try: d.rmdir()
                    except OSError: pass
    finally:
        _close(workers)
    return {
        'ok': True, 'applied': bool(apply), 'source': str(source), 'destination': str(destination),
        'languages': len(workers), 'language_order': [w.lang['id'] for w in workers],
        'planned_copy': [{'path':r,'reason':why} for r,why in to_copy], 'unchanged': len(unchanged),
        'extra_destination_files': extras, 'delete_extras_requested': bool(delete),
        'copied': copied, 'removed': removed,
        'total_language_transformations': sum(x.get('transformations',0) for x in copied) + len(workers)*2,
        'total_ns': time.perf_counter_ns()-started,
    }


def split_file(source, output_dir=None, part_size=4*1024*1024, order='registry', warmups=1, force=False):
    """Create transport-friendly encoded parts; every part passes through the complete language chain."""
    source=Path(source).expanduser().resolve()
    if not source.is_file(): raise ValueError('split requires a regular file')
    if part_size < 1: raise ValueError('part_size must be >= 1')
    out=Path(output_dir).expanduser().resolve() if output_dir else source.parent/(source.name+'.language-parts')
    if out.exists() and any(out.iterdir()) and not force: raise FileExistsError(f'{out} is not empty; use --force')
    out.mkdir(parents=True,exist_ok=True)
    if force:
        for p in out.iterdir():
            if p.is_file() and (p.name.startswith('part-') or p.name=='LANGUAGE-PARTS.json'): p.unlink()
    workers=_start(order,warmups=warmups); started=time.perf_counter_ns(); rows=[]; whole=hashlib.sha256(); total=0
    try:
        with source.open('rb') as f:
            idx=0
            while True:
                chunk=f.read(part_size)
                if not chunk: break
                whole.update(chunk); total+=len(chunk)
                encoded,recovered,stages=_full_roundtrip(workers,chunk)
                if recovered != chunk: raise RuntimeError(f'All-language split round-trip failed at part {idx}')
                name=f'part-{idx:06d}.lpart'; p=out/name; p.write_bytes(encoded)
                rows.append({'index':idx,'file':name,'bytes':len(chunk),'original_sha256':hashlib.sha256(chunk).hexdigest(),'encoded_sha256':hashlib.sha256(encoded).hexdigest(),'roundtrip_ns':sum(x['combined_ns'] for x in stages)})
                idx+=1
        if not rows:
            anchor=hashlib.sha256(b'').digest();_,recovered,_=_full_roundtrip(workers,anchor)
            if recovered != anchor: raise RuntimeError('All-language empty-file anchor failed')
        manifest={
            'format':FORMAT,'schema':FORMAT_VERSION,'type':'split-parts','project':'Language Project','created':_utc_now(),
            'source':{'name':source.name,'path':str(source)},'bytes':total,'sha256':whole.hexdigest(),'part_size':part_size,
            'parts':rows,'language_order':[w.lang['id'] for w in workers],'runtimes':_language_metadata(workers),'languages':len(workers),
            'encoding':'each part stored after full forward language chain; join requires exact recorded runtimes; not encryption',
            'total_ns':time.perf_counter_ns()-started,
        }
        mp=out/'LANGUAGE-PARTS.json';mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    finally:_close(workers)
    return {'ok':True,'source':str(source),'output_dir':str(out),'manifest':str(mp),'parts':len(rows),'bytes':total,'sha256':whole.hexdigest(),'languages':len(manifest['language_order'])}


def join_file(manifest, destination=None, warmups=1, force=False):
    mp=Path(manifest).expanduser().resolve(); obj=json.loads(mp.read_text())
    if obj.get('format')!=FORMAT or obj.get('type')!='split-parts': raise ValueError('Not a Language Project split-parts manifest')
    out=Path(destination).expanduser().resolve() if destination else mp.parent/(obj['source']['name']+'.joined')
    if out.exists() and not force: raise FileExistsError(f'{out} exists; use --force')
    out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.name+'.language-project.part')
    if tmp.exists():tmp.unlink()
    workers=_start(required_ids=obj['language_order'],warmups=warmups);whole=hashlib.sha256();total=0;started=time.perf_counter_ns()
    try:
        with tmp.open('wb') as dst:
            for row in obj['parts']:
                p=mp.parent/row['file'];enc=p.read_bytes()
                if len(enc)!=int(row['bytes']) or hashlib.sha256(enc).hexdigest()!=row['encoded_sha256']:
                    raise RuntimeError(f"Encoded part failed verification: {row['file']}")
                recovered,_=_chain_decode(workers,enc)
                if hashlib.sha256(recovered).hexdigest()!=row['original_sha256']:
                    raise RuntimeError(f"Decoded part failed verification: {row['file']}")
                dst.write(recovered);whole.update(recovered);total+=len(recovered)
        if total!=int(obj['bytes']) or whole.hexdigest()!=obj['sha256']: raise RuntimeError('Joined file hash/size mismatch')
        os.replace(tmp,out)
    except Exception:
        if tmp.exists():tmp.unlink()
        raise
    finally:_close(workers)
    return {'ok':True,'manifest':str(mp),'destination':str(out),'parts':len(obj['parts']),'bytes':total,'sha256':whole.hexdigest(),'languages':len(obj['language_order']),'total_ns':time.perf_counter_ns()-started}


def duplicate_report(root, min_size=1, sample_bytes=8192, order='registry', warmups=1, hidden=False):
    root=Path(root).expanduser().resolve()
    if not root.is_dir(): raise ValueError('dedupe requires a directory')
    groups_by_size={}
    for p,rel in _iter_files(root,hidden):
        if p.stat().st_size>=min_size: groups_by_size.setdefault(p.stat().st_size,[]).append((p,rel))
    candidates=[]
    for size,items in groups_by_size.items():
        if len(items)>1:candidates.extend(items)
    by_hash={}
    for p,rel in candidates: by_hash.setdefault(_sha256_file(p),[]).append((p,rel))
    dup_groups=[(h,items) for h,items in by_hash.items() if len(items)>1]
    workers=_start(order,warmups=warmups);rows=[];started=time.perf_counter_ns()
    try:
        for sha,items in dup_groups:
            probe,_,_=_file_probe(items[0][0],sample_bytes)
            _,recovered,_=_full_roundtrip(workers,probe)
            if recovered!=probe:raise RuntimeError(f'All-language duplicate confirmation failed: {items[0][1]}')
            rows.append({'sha256':sha,'bytes_each':items[0][0].stat().st_size,'files':[rel.as_posix() for _,rel in items],'copies':len(items),'reclaimable_bytes':items[0][0].stat().st_size*(len(items)-1)})
    finally:_close(workers)
    return {'ok':True,'root':str(root),'groups':rows,'duplicate_groups':len(rows),'duplicate_files':sum(x['copies'] for x in rows),'reclaimable_bytes':sum(x['reclaimable_bytes'] for x in rows),'languages':len(workers),'language_order':[w.lang['id'] for w in workers],'note':'Report only; no files are deleted.','total_ns':time.perf_counter_ns()-started}


def scrub_from_audit(manifest, root=None, mirror=None, repair=False, warmups=1):
    """Verify an audit; optionally repair missing/changed files from a trusted mirror using all-language copies."""
    mp=Path(manifest).expanduser().resolve();obj=json.loads(mp.read_text())
    base=Path(root).expanduser().resolve() if root else Path(obj.get('root','')).expanduser().resolve()
    before=verify_directory_audit(mp,base,warmups=warmups)
    result={'ok':before['ok'],'before':before,'repair_requested':bool(repair),'repaired':[],'unrepaired':[]}
    if before['ok'] or not repair:return result
    if not mirror: raise ValueError('--mirror is required with --repair')
    trusted=Path(mirror).expanduser().resolve()
    if not trusted.is_dir(): raise ValueError('mirror must be a directory')
    expected={x['path']:x for x in obj['files']}
    for failure in before['failures']:
        rel=failure['path'];src=trusted/rel;dst=base/rel
        if not src.is_file(): result['unrepaired'].append({'path':rel,'reason':'missing-from-mirror'});continue
        exp=expected.get(rel)
        if not exp or src.stat().st_size!=exp['bytes'] or _sha256_file(src)!=exp['sha256']:
            result['unrepaired'].append({'path':rel,'reason':'mirror-does-not-match-audit'});continue
        info=verified_copy(src,dst,chunk_size=DEFAULT_CHUNK,order='registry',warmups=warmups,force=True)
        result['repaired'].append({'path':rel,'sha256':info['sha256']})
    after=verify_directory_audit(mp,base,warmups=warmups)
    result['after']=after;result['ok']=after['ok'];return result


def backup_health(root, warmups=1, limit=None):
    """Verify protected-backup receipts and package seals in a backup directory."""
    root=Path(root).expanduser().resolve()
    if not root.is_dir(): raise ValueError('backup-health requires a directory')
    receipts=sorted(root.glob('*.receipt.json'),reverse=True)
    if limit is not None: receipts=receipts[:max(0,int(limit))]
    rows=[]
    for rp in receipts:
        try:
            obj=json.loads(rp.read_text());pkg=Path(obj['package'])
            if not pkg.is_absolute():pkg=root/pkg
            if not pkg.is_file():
                # portability: try receipt directory + basename
                pkg=root/Path(obj['package']).name
            seal_path=Path(obj.get('package_seal') or (str(pkg)+'.language-seal.json'))
            if not seal_path.is_absolute():seal_path=root/seal_path
            if not seal_path.is_file():seal_path=root/Path(str(pkg)+'.language-seal.json').name
            sha_ok=pkg.is_file() and _sha256_file(pkg)==obj.get('package_sha256')
            seal_result=verify_seal(seal_path,pkg,warmups=warmups) if pkg.is_file() and seal_path.is_file() else {'ok':False,'reason':'package-or-seal-missing'}
            rows.append({'receipt':str(rp),'package':str(pkg),'package_exists':pkg.is_file(),'package_sha256_ok':sha_ok,'seal':str(seal_path),'seal_ok':bool(seal_result.get('ok')),'ok':bool(sha_ok and seal_result.get('ok'))})
        except Exception as e:
            rows.append({'receipt':str(rp),'ok':False,'error':str(e)})
    return {'ok':all(x.get('ok') for x in rows) if rows else True,'root':str(root),'receipts':len(rows),'healthy':sum(1 for x in rows if x.get('ok')),'unhealthy':sum(1 for x in rows if not x.get('ok')),'results':rows}
