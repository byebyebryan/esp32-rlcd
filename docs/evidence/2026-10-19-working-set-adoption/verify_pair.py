#!/usr/bin/env python3
"""Verify wheel/source/installed parity, RECORD and private wheel identity."""
import base64
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import sysconfig
import zipfile

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    root = Path(__file__).resolve().parent
    pair = json.loads((root / 'pair.json').read_text())
    site = Path(sysconfig.get_path('purelib'))
    report = {'python': sys.executable, 'prefix': sys.prefix, 'packages': {}}
    for label, package, distname in [('observer', 'agent_observer', 'agent-observer'), ('mesh', 'mesh_plus', 'mesh-plus')]:
        wanted = pair['wheels'][label]
        wheel = root / 'wheels' / Path(wanted['path']).name
        assert sha(wheel.read_bytes()) == wanted['sha256']
        dist = importlib.metadata.distribution(distname)
        direct = json.loads(dist.read_text('direct_url.json'))
        assert direct['archive_info']['hashes']['sha256'] == wanted['sha256']
        assert not direct.get('dir_info', {}).get('editable')
        count = 0
        with zipfile.ZipFile(wheel) as z:
            for name in z.namelist():
                if name.startswith(package + '/') and not name.endswith('/'):
                    assert (site / name).read_bytes() == z.read(name), name
                    count += 1
        actual = {p.relative_to(site).as_posix() for p in (site / package).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        with zipfile.ZipFile(wheel) as z:
            expected = {name for name in z.namelist() if name.startswith(package + '/') and not name.endswith('/')}
        assert actual == expected
        checked = 0
        for path, digest, size in csv.reader(dist.read_text('RECORD').splitlines()):
            p = (site / path).resolve()
            assert p.is_relative_to(Path(sys.prefix).resolve())
            if not digest:
                assert path.endswith('/RECORD') or path.endswith('.pyc')
                continue
            data = p.read_bytes()
            expected_hash = 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')
            assert digest == expected_hash and len(data) == int(size)
            checked += 1
        report['packages'][label] = {'version': dist.version, 'wheelSha256': wanted['sha256'], 'packageFilesExact': count, 'installedRecordEntriesVerified': checked}
    from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
    descriptor = WorkingSetAgentProfile().descriptor
    assert descriptor.profile_id == 'agent-observer.mesh-working-set.v1'
    report['profile'] = descriptor.profile_id
    report['status'] = 'pass'
    print(json.dumps(report, sort_keys=True))

if __name__ == '__main__':
    main()
