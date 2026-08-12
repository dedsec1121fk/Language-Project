from __future__ import annotations

from pathlib import Path
import datetime
import hashlib
import json
import os
import tarfile
import tempfile
import time
import zipfile

from .engine import active_languages, prewarm, load_state
from .registry import ROOT

FORMAT = "language-project-polyglot"
FORMAT_VERSION = 1
DEFAULT_CHUNK = 64 * 1024


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()


def _state_versions():
    return load_state().get('versions', {})


def _select_languages(order='registry', required_ids=None):
    langs = active_languages(order)
    if required_ids is None:
        if not langs:
            raise RuntimeError('No verified languages. Run: language-project setup --install')
        return langs
    by_id = {x['id']: x for x in active_languages('registry')}
    missing = [x for x in required_ids if x not in by_id]
    if missing:
        raise RuntimeError(
            'This polyglot artifact requires verified runtimes that are not active on this device: '
            + ', '.join(missing)
            + '. Run: language-project setup --install'
        )
    return [by_id[x] for x in required_ids]


def _start(order='registry', required_ids=None, warmups=1):
    langs = _select_languages(order, required_ids)
    workers, errors = prewarm(langs, warmups)
    if errors or len(workers) != len(langs):
        for w in workers:
            w.close()
        raise RuntimeError('Unable to prewarm every required language: ' + json.dumps(errors, ensure_ascii=False))
    return workers


def _close(workers):
    for w in workers:
        try:
            w.close()
        except Exception:
            pass


def _chain_encode(workers, data: bytes):
    cur = data.hex()
    stages = []
    for w in workers:
        cur, ns = w.request('E', cur)
        stages.append({'id': w.lang['id'], 'name': w.lang['name'], 'encode_ns': ns})
    return bytes.fromhex(cur), stages


def _chain_decode(workers, data: bytes):
    cur = data.hex()
    timings = {}
    for w in reversed(workers):
        cur, ns = w.request('D', cur)
        timings[w.lang['id']] = ns
    return bytes.fromhex(cur), timings


def _full_roundtrip(workers, data: bytes):
    encoded, stages = _chain_encode(workers, data)
    recovered, dec = _chain_decode(workers, encoded)
    for row in stages:
        row['decode_ns'] = dec[row['id']]
        row['combined_ns'] = row['encode_ns'] + row['decode_ns']
    return encoded, recovered, stages


def _language_metadata(workers):
    versions = _state_versions()
    return [
        {
            'id': w.lang['id'],
            'name': w.lang['name'],
            'kind': w.lang.get('kind'),
            'version': versions.get(w.lang['id'], 'verified'),
        }
        for w in workers
    ]


def status():
    langs = active_languages('registry')
    return {
        'project': 'Language Project',
        'mode': 'practical-polyglot',
        'verified_languages': len(langs),
        'language_ids': [x['id'] for x in langs],
        'language_names': [x['name'] for x in langs],
        'principle': 'Every polyglot operation uses every verified active language on this device.',
        'operations': {
            'seal': 'Distributed file integrity seal; every language contributes a deterministic transformed digest.',
            'fingerprint': 'Compact project-specific fingerprint derived from SHA-256 plus every verified language contribution.',
            'verify': 'Recreate and verify a polyglot seal with the exact language set recorded in it.',
            'pack': 'Create a recoverable .lpack archive; every chunk passes forward and backward through every language.',
            'unpack': 'Reverse the exact recorded language chain and safely restore the archive.',
            'copy': 'Atomic verified copy; every chunk passes through the complete language round-trip before writing.',
            'audit': 'Directory integrity audit; every file gets SHA-256 plus an all-language round-trip probe.',
            'audit-verify': 'Verify directory hashes and repeat all-language probes.',
            'protect': 'One-command protected backup set: optional directory audit + .lpack + package seal.',
            'restore': 'Verify an adjacent/explicit package seal, then safely restore the .lpack.',
            'compare': 'Compare files or directory trees while every verified language validates content-bound probes.',
            'mirror': 'Dry-run-first directory mirror; every copied chunk round-trips through every verified language.',
            'split': 'Split large files into transport-friendly encoded parts using the full language chain.',
            'join': 'Reconstruct split parts using the exact recorded reverse language chain.',
            'dedupe': 'Report exact duplicate groups and confirm each group through every verified language.',
            'scrub': 'Verify a directory audit and optionally repair trusted files from a verified mirror.',
            'backup-health': 'Scan protected backup receipts and re-verify package hashes plus polyglot seals.',
        },
        'warning': 'Polyglot transformations are reversible encodings, not encryption.',
    }


def _seal_core(path: Path, workers, chunk_size=DEFAULT_CHUNK):
    if chunk_size < 1:
        raise ValueError('chunk_size must be >= 1')
    size = path.stat().st_size
    source_hash = hashlib.sha256()
    per = {
        w.lang['id']: {
            'id': w.lang['id'],
            'name': w.lang['name'],
            'chunks': 0,
            'bytes': 0,
            'encode_ns': 0,
            'decode_ns': 0,
            '_digest': hashlib.sha256((w.lang['id'] + '\0').encode()),
        }
        for w in workers
    }
    chunk_index = 0
    with path.open('rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            source_hash.update(chunk)
            w = workers[chunk_index % len(workers)]
            encoded, en = w.request('E', chunk.hex())
            recovered, dn = w.request('D', encoded)
            recovered_b = bytes.fromhex(recovered)
            if recovered_b != chunk:
                raise RuntimeError(f"{w.lang['name']}: round-trip failure while sealing chunk {chunk_index}")
            row = per[w.lang['id']]
            row['chunks'] += 1
            row['bytes'] += len(chunk)
            row['encode_ns'] += en
            row['decode_ns'] += dn
            eb = bytes.fromhex(encoded)
            row['_digest'].update(chunk_index.to_bytes(8, 'big'))
            row['_digest'].update(len(chunk).to_bytes(8, 'big'))
            row['_digest'].update(eb)
            chunk_index += 1

    source_sha = source_hash.hexdigest()
    # If a small file had fewer chunks than workers, unused languages still take part
    # by processing a deterministic anchor derived from the complete file hash.
    for idx, w in enumerate(workers):
        row = per[w.lang['id']]
        if row['chunks']:
            continue
        anchor = hashlib.sha256(bytes.fromhex(source_sha) + w.lang['id'].encode() + idx.to_bytes(4, 'big')).digest()
        encoded, en = w.request('E', anchor.hex())
        recovered, dn = w.request('D', encoded)
        if bytes.fromhex(recovered) != anchor:
            raise RuntimeError(f"{w.lang['name']}: anchor round-trip failure")
        row['anchor'] = True
        row['encode_ns'] += en
        row['decode_ns'] += dn
        row['_digest'].update(b'ANCHOR\0')
        row['_digest'].update(bytes.fromhex(encoded))

    rows = []
    combined = hashlib.sha256(bytes.fromhex(source_sha))
    for w in workers:
        row = per[w.lang['id']]
        digest = row.pop('_digest').hexdigest()
        row.setdefault('anchor', False)
        row['transformed_sha256'] = digest
        row['combined_ns'] = row['encode_ns'] + row['decode_ns']
        combined.update(w.lang['id'].encode() + b'\0' + bytes.fromhex(digest))
        rows.append(row)
    return {
        'bytes': size,
        'sha256': source_sha,
        'chunk_size': chunk_size,
        'chunks': chunk_index,
        'languages': len(workers),
        'language_order': [w.lang['id'] for w in workers],
        'language_seals': rows,
        'polyglot_fingerprint': combined.hexdigest(),
        'integrity': True,
    }


def seal(path, output=None, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ValueError('seal requires a regular file')
    workers = _start(order, warmups=warmups)
    started = time.perf_counter_ns()
    try:
        core = _seal_core(path, workers, chunk_size)
        result = {
            'format': FORMAT,
            'schema': FORMAT_VERSION,
            'type': 'seal',
            'project': 'Language Project',
            'created': _utc_now(),
            'source': {'name': path.name, 'path': str(path)},
            'runtimes': _language_metadata(workers),
            **core,
            'total_ns': time.perf_counter_ns() - started,
        }
    finally:
        _close(workers)
    out = Path(output).expanduser() if output else path.with_name(path.name + '.language-seal.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    result['output'] = str(out)
    return result


def verify_seal(manifest, file=None, warmups=1):
    mp = Path(manifest).expanduser().resolve()
    obj = json.loads(mp.read_text())
    if obj.get('format') != FORMAT or obj.get('type') != 'seal':
        raise ValueError('Not a Language Project polyglot seal')
    path = Path(file).expanduser().resolve() if file else Path(obj['source']['path']).expanduser().resolve()
    if not path.is_file():
        alt = mp.parent / obj['source']['name']
        if alt.is_file():
            path = alt
        else:
            raise FileNotFoundError(path)
    ids = obj['language_order']
    workers = _start(required_ids=ids, warmups=warmups)
    try:
        current = _seal_core(path, workers, int(obj['chunk_size']))
    finally:
        _close(workers)
    expected_by_id = {x['id']: x for x in obj.get('language_seals', [])}
    mismatches = []
    for row in current['language_seals']:
        exp = expected_by_id.get(row['id'])
        if not exp or exp.get('transformed_sha256') != row['transformed_sha256']:
            mismatches.append(row['id'])
    ok = (
        current['sha256'] == obj.get('sha256')
        and current['bytes'] == obj.get('bytes')
        and current['polyglot_fingerprint'] == obj.get('polyglot_fingerprint')
        and not mismatches
    )
    return {
        'ok': ok,
        'file': str(path),
        'manifest': str(mp),
        'bytes': current['bytes'],
        'languages': current['languages'],
        'sha256_expected': obj.get('sha256'),
        'sha256_actual': current['sha256'],
        'fingerprint_expected': obj.get('polyglot_fingerprint'),
        'fingerprint_actual': current['polyglot_fingerprint'],
        'language_mismatches': mismatches,
    }


def fingerprint(path, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ValueError('fingerprint requires a regular file')
    workers = _start(order, warmups=warmups)
    try:
        core = _seal_core(path, workers, chunk_size)
    finally:
        _close(workers)
    return {
        'file': str(path),
        'bytes': core['bytes'],
        'sha256': core['sha256'],
        'languages': core['languages'],
        'language_order': core['language_order'],
        'polyglot_fingerprint': core['polyglot_fingerprint'],
    }


def _tar_source(source: Path, target: Path):
    with tarfile.open(target, 'w:gz') as tf:
        tf.add(source, arcname=source.name, recursive=True)


def _safe_extract_tar(archive: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    base = destination.resolve()
    with tarfile.open(archive) as tf:
        for member in tf.getmembers():
            target = (base / member.name).resolve()
            if target != base and base not in target.parents:
                raise ValueError(f'Unsafe archive member: {member.name}')
            if member.issym() or member.islnk():
                # Symlinks can escape the extraction root after extraction; skip them.
                raise ValueError(f'Symlink/hardlink members are not accepted: {member.name}')
        if hasattr(tarfile, 'data_filter'):
            tf.extractall(destination, filter='data')
        else:
            tf.extractall(destination)


def pack(source, output=None, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1, force=False):
    source = Path(source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    if chunk_size < 1:
        raise ValueError('chunk_size must be >= 1')
    out = Path(output).expanduser().resolve() if output else source.parent / (source.name + '.lpack')
    if out.exists() and not force:
        raise FileExistsError(f'{out} already exists; use --force to replace it')
    if source.is_dir() and (out == source or source in out.parents):
        raise ValueError('Output .lpack must be outside the source directory')

    workers = _start(order, warmups=warmups)
    started = time.perf_counter_ns()
    try:
        with tempfile.TemporaryDirectory(prefix='language-project-pack-') as td:
            td = Path(td)
            archive = td / 'source.tar.gz'
            payload = td / 'payload.bin'
            _tar_source(source, archive)
            archive_sha = _sha256_file(archive)
            payload_hash = hashlib.sha256()
            chunks = []
            total_original = 0
            total_encoded = 0
            with archive.open('rb') as src, payload.open('wb') as dst:
                index = 0
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    encoded, recovered, stages = _full_roundtrip(workers, chunk)
                    if recovered != chunk:
                        raise RuntimeError(f'Polyglot pack integrity failure in chunk {index}')
                    dst.write(encoded)
                    payload_hash.update(encoded)
                    chunks.append({
                        'index': index,
                        'bytes': len(chunk),
                        'original_sha256': hashlib.sha256(chunk).hexdigest(),
                        'encoded_sha256': hashlib.sha256(encoded).hexdigest(),
                        'roundtrip_ns': sum(x['combined_ns'] for x in stages),
                    })
                    total_original += len(chunk)
                    total_encoded += len(encoded)
                    index += 1
            manifest = {
                'format': FORMAT,
                'schema': FORMAT_VERSION,
                'type': 'lpack',
                'project': 'Language Project',
                'created': _utc_now(),
                'source': {'name': source.name, 'kind': 'directory' if source.is_dir() else 'file'},
                'compression': 'tar.gz',
                'encoding': 'full verified language chain; reversible; not encryption',
                'language_order': [w.lang['id'] for w in workers],
                'runtimes': _language_metadata(workers),
                'languages': len(workers),
                'chunk_size': chunk_size,
                'chunks': chunks,
                'archive_bytes': total_original,
                'payload_bytes': total_encoded,
                'archive_sha256': archive_sha,
                'payload_sha256': payload_hash.hexdigest(),
                'total_ns': time.perf_counter_ns() - started,
            }
            tmp_out = out.with_name(out.name + '.part')
            if tmp_out.exists():
                tmp_out.unlink()
            tmp_out.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(tmp_out, 'w', compression=zipfile.ZIP_STORED) as zf:
                zf.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
                zf.write(payload, 'payload.bin')
            os.replace(tmp_out, out)
    finally:
        _close(workers)
    return {
        'ok': True,
        'output': str(out),
        'source': str(source),
        'languages': len(manifest['language_order']),
        'chunks': len(manifest['chunks']),
        'archive_sha256': manifest['archive_sha256'],
        'payload_sha256': manifest['payload_sha256'],
        'bytes': out.stat().st_size,
        'warning': 'The .lpack format is reversible encoding, not encryption.',
    }


def unpack(package, destination=None, warmups=1, force=False):
    package = Path(package).expanduser().resolve()
    if not package.is_file():
        raise FileNotFoundError(package)
    dest = Path(destination).expanduser().resolve() if destination else package.parent / (package.stem + '-restored')
    if dest.exists() and any(dest.iterdir()) and not force:
        raise FileExistsError(f'{dest} is not empty; use --force to extract there')
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
        if names != {'manifest.json', 'payload.bin'}:
            raise ValueError('Invalid .lpack container contents')
        manifest = json.loads(zf.read('manifest.json'))
        if manifest.get('format') != FORMAT or manifest.get('type') != 'lpack':
            raise ValueError('Not a Language Project .lpack archive')
        payload_sha = hashlib.sha256()
        with zf.open('payload.bin') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                payload_sha.update(chunk)
        if payload_sha.hexdigest() != manifest.get('payload_sha256'):
            raise RuntimeError('Package payload SHA-256 does not match its manifest')

    workers = _start(required_ids=manifest['language_order'], warmups=warmups)
    started = time.perf_counter_ns()
    try:
        with tempfile.TemporaryDirectory(prefix='language-project-unpack-') as td:
            td = Path(td)
            archive = td / 'source.tar.gz'
            with zipfile.ZipFile(package) as zf, zf.open('payload.bin') as src, archive.open('wb') as dst:
                for row in manifest['chunks']:
                    size = int(row['bytes'])
                    encoded = src.read(size)
                    if len(encoded) != size:
                        raise RuntimeError(f"Unexpected end of payload at chunk {row['index']}")
                    if hashlib.sha256(encoded).hexdigest() != row['encoded_sha256']:
                        raise RuntimeError(f"Encoded chunk {row['index']} failed SHA-256 verification")
                    recovered, _ = _chain_decode(workers, encoded)
                    if hashlib.sha256(recovered).hexdigest() != row['original_sha256']:
                        raise RuntimeError(f"Decoded chunk {row['index']} failed SHA-256 verification")
                    dst.write(recovered)
                if src.read(1):
                    raise RuntimeError('Package payload contains unexpected trailing bytes')
            archive_sha = _sha256_file(archive)
            if archive_sha != manifest['archive_sha256']:
                raise RuntimeError('Recovered archive SHA-256 mismatch')
            _safe_extract_tar(archive, dest)
    finally:
        _close(workers)
    return {
        'ok': True,
        'package': str(package),
        'destination': str(dest),
        'source_name': manifest['source']['name'],
        'languages': len(manifest['language_order']),
        'chunks': len(manifest['chunks']),
        'archive_sha256': manifest['archive_sha256'],
        'total_ns': time.perf_counter_ns() - started,
    }


def verified_copy(source, destination, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1, force=False):
    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    if not source.is_file():
        raise ValueError('polyglot copy requires a regular file')
    if destination.exists() and not force:
        raise FileExistsError(f'{destination} already exists; use --force to replace it')
    if source == destination:
        raise ValueError('source and destination must be different')
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + '.language-project.part')
    if tmp.exists():
        tmp.unlink()
    workers = _start(order, warmups=warmups)
    src_hash = hashlib.sha256()
    dst_hash = hashlib.sha256()
    chunks = 0
    bytes_total = 0
    started = time.perf_counter_ns()
    try:
        with source.open('rb') as src, tmp.open('wb') as dst:
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                src_hash.update(chunk)
                encoded, recovered, _ = _full_roundtrip(workers, chunk)
                if recovered != chunk:
                    raise RuntimeError(f'Full-language round-trip failed at chunk {chunks}')
                dst.write(recovered)
                dst_hash.update(recovered)
                bytes_total += len(chunk)
                chunks += 1
        if src_hash.digest() != dst_hash.digest():
            raise RuntimeError('Final copy SHA-256 mismatch')
        os.replace(tmp, destination)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    finally:
        _close(workers)
    return {
        'ok': True,
        'source': str(source),
        'destination': str(destination),
        'bytes': bytes_total,
        'chunks': chunks,
        'languages_per_chunk': len(workers),
        'total_language_transformations': chunks * len(workers) * 2,
        'sha256': src_hash.hexdigest(),
        'total_ns': time.perf_counter_ns() - started,
    }


def _file_probe(path: Path, sample_bytes: int):
    size = path.stat().st_size
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    digest = h.digest()
    if size <= sample_bytes:
        data = path.read_bytes()
    else:
        half = max(1, sample_bytes // 2)
        with path.open('rb') as f:
            head = f.read(half)
            f.seek(max(0, size - half))
            tail = f.read(half)
        data = head + tail
    # Include the full-file hash in the probe, so every worker's probe is bound to all bytes.
    return data + digest, h.hexdigest(), size


def directory_audit(root, output=None, sample_bytes=32 * 1024, order='registry', warmups=1, hidden=False, verbose=True):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('audit requires a directory')
    if sample_bytes < 0:
        raise ValueError('sample_bytes must be >= 0')
    workers = _start(order, warmups=warmups)
    rows = []
    started = time.perf_counter_ns()
    try:
        files = []
        for p in sorted(root.rglob('*')):
            if not p.is_file() or p.is_symlink():
                continue
            rel = p.relative_to(root)
            if not hidden and any(part.startswith('.') for part in rel.parts):
                continue
            if output and p.resolve() == Path(output).expanduser().resolve():
                continue
            files.append(p)
        for idx, p in enumerate(files, 1):
            probe, sha, size = _file_probe(p, sample_bytes)
            encoded, recovered, stages = _full_roundtrip(workers, probe)
            ok = recovered == probe
            if not ok:
                raise RuntimeError(f'All-language probe failed for {p}')
            rows.append({
                'path': p.relative_to(root).as_posix(),
                'bytes': size,
                'sha256': sha,
                'probe_bytes': len(probe),
                'probe_encoded_sha256': hashlib.sha256(encoded).hexdigest(),
                'roundtrip_ns': sum(x['combined_ns'] for x in stages),
                'integrity': ok,
            })
            if verbose:
                print(f"[{idx:>4}/{len(files):<4}] {p.relative_to(root)}  {size:>10} B  OK")
    finally:
        _close(workers)
    tree_hash = hashlib.sha256()
    for row in rows:
        tree_hash.update(row['path'].encode() + b'\0' + bytes.fromhex(row['sha256']))
    result = {
        'format': FORMAT,
        'schema': FORMAT_VERSION,
        'type': 'directory-audit',
        'project': 'Language Project',
        'created': _utc_now(),
        'root': str(root),
        'languages': len(workers),
        'language_order': [w.lang['id'] for w in workers],
        'runtimes': _language_metadata(workers),
        'sample_bytes': sample_bytes,
        'files': rows,
        'file_count': len(rows),
        'total_bytes': sum(x['bytes'] for x in rows),
        'tree_fingerprint': tree_hash.hexdigest(),
        'integrity': all(x['integrity'] for x in rows),
        'total_ns': time.perf_counter_ns() - started,
    }
    out = Path(output).expanduser() if output else root / 'LANGUAGE-PROJECT-POLYGLOT-AUDIT.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    result['output'] = str(out)
    return result


def verify_directory_audit(manifest, root=None, warmups=1):
    mp = Path(manifest).expanduser().resolve()
    obj = json.loads(mp.read_text())
    if obj.get('format') != FORMAT or obj.get('type') != 'directory-audit':
        raise ValueError('Not a Language Project directory audit')
    base = Path(root).expanduser().resolve() if root else Path(obj['root']).expanduser().resolve()
    if not base.is_dir():
        raise FileNotFoundError(base)
    workers = _start(required_ids=obj['language_order'], warmups=warmups)
    failures = []
    checked = 0
    tree_hash = hashlib.sha256()
    try:
        for row in obj['files']:
            p = base / row['path']
            if not p.is_file():
                failures.append({'path': row['path'], 'reason': 'missing'})
                continue
            probe, sha, size = _file_probe(p, int(obj['sample_bytes']))
            if sha != row['sha256'] or size != row['bytes']:
                failures.append({'path': row['path'], 'reason': 'content-changed'})
                continue
            encoded, recovered, _ = _full_roundtrip(workers, probe)
            if recovered != probe or hashlib.sha256(encoded).hexdigest() != row['probe_encoded_sha256']:
                failures.append({'path': row['path'], 'reason': 'polyglot-probe-mismatch'})
                continue
            tree_hash.update(row['path'].encode() + b'\0' + bytes.fromhex(sha))
            checked += 1
    finally:
        _close(workers)
    expected_paths = {x['path'] for x in obj['files']}
    current_paths = set()
    for p in base.rglob('*'):
        if p.is_file() and not p.is_symlink():
            rel = p.relative_to(base).as_posix()
            if rel != mp.name:
                current_paths.add(rel)
    extras = sorted(current_paths - expected_paths - {Path(manifest).name})
    ok = not failures and not extras and checked == len(obj['files']) and tree_hash.hexdigest() == obj['tree_fingerprint']
    return {
        'ok': ok,
        'manifest': str(mp),
        'root': str(base),
        'languages': len(obj['language_order']),
        'expected_files': len(obj['files']),
        'checked_files': checked,
        'failures': failures,
        'extra_files': extras,
        'tree_fingerprint_expected': obj['tree_fingerprint'],
        'tree_fingerprint_actual': tree_hash.hexdigest(),
    }


def protect(source, destination=None, label=None, chunk_size=DEFAULT_CHUNK, order='registry', warmups=1, force=False, audit_directory_first=True):
    """Create a practical backup set: optional directory audit + .lpack + seal of the package."""
    source = Path(source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    dest = Path(destination).expanduser().resolve() if destination else source.parent / 'Language-Project-Backups'
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    safe_label = ''.join(c if c.isalnum() or c in '-_.' else '-' for c in (label or source.name)).strip('-') or 'backup'
    package = dest / f'{safe_label}-{stamp}.lpack'
    audit_result = None
    if source.is_dir() and audit_directory_first:
        audit_path = dest / f'{safe_label}-{stamp}.audit.json'
        audit_result = directory_audit(source, audit_path, sample_bytes=32 * 1024, order=order, warmups=warmups, verbose=False)
    pack_result = pack(source, package, chunk_size=chunk_size, order=order, warmups=warmups, force=force)
    seal_result = seal(package, str(package) + '.language-seal.json', chunk_size=chunk_size, order=order, warmups=warmups)
    receipt = {
        'format': FORMAT,
        'schema': FORMAT_VERSION,
        'type': 'protected-backup-receipt',
        'project': 'Language Project',
        'created': _utc_now(),
        'source': str(source),
        'package': str(package),
        'package_seal': seal_result['output'],
        'directory_audit': audit_result.get('output') if audit_result else None,
        'languages': pack_result['languages'],
        'language_order': seal_result['language_order'],
        'package_sha256': _sha256_file(package),
        'polyglot_fingerprint': seal_result['polyglot_fingerprint'],
        'warning': '.lpack is reversible encoding, not encryption.',
    }
    receipt_path = dest / f'{safe_label}-{stamp}.receipt.json'
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    receipt['receipt'] = str(receipt_path)
    return receipt


def restore_protected(package, destination=None, seal_manifest=None, warmups=1, force=False):
    """Verify an adjacent/explicit polyglot seal first, then restore the .lpack."""
    package = Path(package).expanduser().resolve()
    seal_path = Path(seal_manifest).expanduser().resolve() if seal_manifest else Path(str(package) + '.language-seal.json')
    verification = None
    if seal_path.is_file():
        verification = verify_seal(seal_path, package, warmups=warmups)
        if not verification['ok']:
            raise RuntimeError('Protected backup seal verification failed; restore aborted')
    result = unpack(package, destination=destination, warmups=warmups, force=force)
    result['seal_checked'] = bool(verification)
    result['seal_manifest'] = str(seal_path) if verification else None
    return result
