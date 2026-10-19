#!/usr/bin/env python3
"""Apply only the reviewed producer targets after exact preimage checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import argparse

ROOT = Path.home() / '.local/state/rlcd-working-set-adoption/20261019T183334Z'
TARGETS = ['.local/bin/agent-observer-service', '.config/systemd/user/agent-observer.service',
    '.local/bin/mesh-plus', '.local/bin/mesh-plus-working-set', '.config/mesh-plus/sources.toml',
    '.config/systemd/user/mesh-plus-agent-working-set.service',
    '.config/systemd/user/default.target.wants/mesh-plus-agent-working-set.service']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['initial', 'reselect'], default='initial')
    phase = parser.parse_args().phase
    before = json.loads((ROOT / 'managed-before.json').read_text())
    source = Path.home() / '.local/share/chezmoi'
    for rel in TARGETS:
        old = before['targets'][rel]
        path = Path.home() / rel
        if old['kind'] == 'absent':
            assert not path.exists() and not path.is_symlink(), rel
        elif old['kind'] == 'symlink':
            assert path.is_symlink() and os.readlink(path) == old['target'], rel
        else:
            assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == old['sha256'], rel
    base = ['chezmoi', '--source', str(source), '--refresh-externals=never']
    targets = [str(Path.home() / p) for p in TARGETS]
    for name, args in [('producer-diff', [*base, 'diff', *targets]),
                       ('producer-dry-run', [*base, 'apply', '--dry-run', '--force', '--verbose', '--exclude', 'scripts', *targets]),
                       ('producer-apply', [*base, 'apply', '--force', '--verbose', '--exclude', 'scripts', *targets])]:
        result = subprocess.run(args, capture_output=True, timeout=60)
        log = ROOT / ((('reselect-final-' if phase == 'reselect' else '') + name) + '.log')
        assert not log.exists(), str(log)
        log.write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, name
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', '--user', 'restart', 'agent-observer.service'], check=True, timeout=30)
    subprocess.run(['systemctl', '--user', 'start', 'mesh-plus-agent-working-set.service'], check=True, timeout=30)
    result = subprocess.check_output(['systemctl', '--user', 'show', 'agent-observer.service',
        'mesh-plus-agent-working-set.service', '--property=Id,ActiveState,SubState,MainPID,NRestarts,InvocationID,ExecStart'], text=True)
    output = ROOT / ('producer-reselected-final.txt' if phase == 'reselect' else 'producer-selected.txt')
    assert not output.exists()
    output.write_text(result)
    print(result)

if __name__ == '__main__':
    main()
