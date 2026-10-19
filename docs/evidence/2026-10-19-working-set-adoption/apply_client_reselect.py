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
TARGETS = ['.local/bin/rlcd-agent-dashboard', '.config/rlcd-agent-dashboard/selection.json',
    '.config/systemd/user/rlcd-agent-dashboard.service',
    '.config/systemd/user/default.target.wants/rlcd-agent-dashboard.service']

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
    for name, args in [('client-diff', [*base, 'diff', *targets]),
                       ('client-dry-run', [*base, 'apply', '--dry-run', '--force', '--verbose', '--exclude', 'scripts', *targets]),
                       ('client-apply', [*base, 'apply', '--force', '--verbose', '--exclude', 'scripts', *targets])]:
        result = subprocess.run(args, capture_output=True, timeout=60)
        log = ROOT / ((('reselect-final-' if phase == 'reselect' else '') + name) + '.log')
        assert not log.exists(), str(log)
        log.write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, name
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    assert not subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'rlcd-agent-dashboard.service']).returncode == 0
    subprocess.run(['systemctl', '--user', 'start', 'rlcd-agent-dashboard.service'], check=True, timeout=30)
    result = subprocess.check_output(['systemctl', '--user', 'show', 'rlcd-agent-dashboard.service', '--property=Id,ActiveState,SubState,MainPID,NRestarts,InvocationID,ExecStart'], text=True)
    output = ROOT / ('client-reselected-final.txt' if phase == 'reselect' else 'client-selected.txt')
    assert not output.exists()
    output.write_text(result)
    print(result)

if __name__ == '__main__':
    main()
