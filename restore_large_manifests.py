#!/usr/bin/env python3
"""Verify or restore the 162 large manifests downloaded from a GitHub release."""
import argparse,hashlib,json,os,tempfile,zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def blocks(record,parts_dir):
    decoder=zlib.decompressobj(31)
    for part in record['parts']:
        path=parts_dir/part['name']
        if not path.is_file() or path.stat().st_size!=part['size']:
            raise RuntimeError('Missing or incomplete release asset: '+str(path))
        h=hashlib.sha256()
        with path.open('rb') as f:
            while True:
                data=f.read(4*1024**2)
                if not data:break
                h.update(data)
                while data:
                    raw=decoder.decompress(data,8*1024**2);data=decoder.unconsumed_tail
                    if raw:yield raw
        if h.hexdigest()!=part['sha256']:raise RuntimeError('Release asset checksum mismatch: '+part['name'])
    tail=decoder.flush()
    if tail:yield tail
    if not decoder.eof:raise RuntimeError('Truncated gzip stream: '+record['path'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    default=ROOT/'backup_metadata/large_manifests.json'
    if not default.exists():default=ROOT/'large_manifests.json'
    p.add_argument('--manifest',type=Path,default=default)
    p.add_argument('--parts-dir',type=Path,default=ROOT/'large_manifest_parts')
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--verify-only',action='store_true');group.add_argument('--destination',type=Path)
    args=p.parse_args();manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    parts=args.parts_dir.resolve();dest=args.destination.resolve() if args.destination else None
    if dest:dest.mkdir(parents=True,exist_ok=True)
    total=0
    for n,r in enumerate(manifest['files'],1):
        target=dest/r['path'] if dest else None
        if target and dest not in target.resolve().parents:raise RuntimeError('Unsafe restore path')
        if target and target.exists():
            h=hashlib.sha256()
            with target.open('rb') as f:
                for data in iter(lambda:f.read(4*1024**2),b''):h.update(data)
            if target.stat().st_size!=r['size'] or h.hexdigest()!=r['sha256']:raise RuntimeError('Refusing to overwrite a different existing file: '+str(target))
            total+=r['size'];print('Already restored',n,'/',len(manifest['files']),r['path'],flush=True);continue
        tmp=None;output=None;h=hashlib.sha256();size=0
        if target:
            target.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(prefix=target.name+'.restore-',dir=target.parent);output=os.fdopen(fd,'wb')
        try:
            for data in blocks(r,parts):
                h.update(data);size+=len(data)
                if output:output.write(data)
            if output:output.close();output=None
            if size!=r['size'] or h.hexdigest()!=r['sha256']:raise RuntimeError('Original file checksum mismatch: '+r['path'])
            if target:
                if target.exists():raise RuntimeError('Restore target appeared while processing: '+str(target))
                os.replace(tmp,target);tmp=None;target.chmod(r['mode']&0o777);os.utime(target,ns=(r['mtime_ns'],r['mtime_ns']))
        finally:
            if output:output.close()
            if tmp and os.path.exists(tmp):os.unlink(tmp)
        total+=size;print('Verified',n,'/',len(manifest['files']),r['path'],flush=True)
    print('SUCCESS:',len(manifest['files']),'large manifests;',total,'original bytes verified.',flush=True)
if __name__=='__main__':main()
