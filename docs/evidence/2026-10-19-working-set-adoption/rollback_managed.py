#!/usr/bin/env python3
"""Restore only this goal's exact managed preimages; firmware is paired separately."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path.home() / '.local/state/rlcd-working-set-adoption/20261019T183334Z'
PRODUCER = ['.local/bin/agent-observer-service', '.config/systemd/user/agent-observer.service',
    '.local/bin/mesh-plus', '.local/bin/mesh-plus-working-set', '.config/mesh-plus/sources.toml',
    '.config/systemd/user/mesh-plus-agent-working-set.service',
    '.config/systemd/user/default.target.wants/mesh-plus-agent-working-set.service']
CLIENT = ['.local/bin/rlcd-agent-dashboard', '.config/rlcd-agent-dashboard/selection.json',
    '.config/systemd/user/rlcd-agent-dashboard.service',
    '.config/systemd/user/default.target.wants/rlcd-agent-dashboard.service']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', action='store_true', help='Snap only; leave stopped for the paired firmware restore')
    args = parser.parse_args()
    old = json.loads((ROOT / 'managed-before.json').read_text())
    targets = PRODUCER + (CLIENT if args.client else [])
    # Compare every current target against the exact reviewed canonical render
    # before overwriting. Unknown concurrent drift is not ours to restore.
    source = Path.home() / '.local/share/chezmoi'
    for relative in targets:
        path = Path.home() / relative
        rendered = subprocess.check_output(['chezmoi', '--source', str(source), '--refresh-externals=never', 'cat', str(path)])
        if path.is_symlink():
            assert os.readlink(path) == rendered.decode().strip(), relative
        else:
            assert path.read_bytes() == rendered, relative
    if args.client:
        subprocess.run(['systemctl', '--user', 'stop', 'rlcd-agent-dashboard.service'], check=True, timeout=20)
    subprocess.run(['systemctl', '--user', 'stop', 'mesh-plus-agent-working-set.service'], check=True, timeout=20)
    for relative in targets:
        path = Path.home() / relative
        record = old['targets'][relative]
        if record['kind'] == 'absent':
            path.unlink()
        elif record['kind'] == 'symlink':
            temporary = path.with_name(path.name + '.rlcd-rollback')
            assert not temporary.exists() and not temporary.is_symlink()
            temporary.symlink_to(record['target'])
            temporary.replace(path)
        else:
            data = base64.b64decode(record['base64'])
            assert hashlib.sha256(data).hexdigest() == record['sha256']
            fd, name = tempfile.mkstemp(prefix='.rlcd-rollback-', dir=path.parent)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
            os.chmod(name, record['mode'])
            os.replace(name, path)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', '--user', 'restart', 'agent-observer.service'], check=True, timeout=30)
    report = {'restoredTargets': targets, 'allExact': True, 'clientLeftStoppedForFirmwarePair': args.client,
        'collector': subprocess.check_output(['systemctl', '--user', 'show', 'agent-observer.service',
            '--property=ActiveState,MainPID,ExecStart,InvocationID'], text=True)}
    for relative in targets:
        path = Path.home() / relative
        record = old['targets'][relative]
        if record['kind'] == 'absent':
            assert not path.exists() and not path.is_symlink()
        elif record['kind'] == 'symlink':
            assert path.is_symlink() and os.readlink(path) == record['target']
        else:
            assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
    with (ROOT / 'managed-rollback.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'restoredTargets': len(targets), 'allExact': True, 'clientLeftStoppedForFirmwarePair': args.client}))

if __name__ == '__main__':
    main()
