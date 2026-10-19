#!/usr/bin/env python3
"""One private installed/native proof; only the service created here is stopped."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import time

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', choices=['snap', 'starship'], required=True)
    parser.add_argument('--prefix', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    pair = json.loads((root / 'pair.json').read_text())
    assert not args.output.exists()
    python = args.prefix / 'bin/python'
    assert Path(sys.executable).absolute() == python
    home = Path.home() / '.codex'
    control = home / 'app-server-control/app-server-control.sock'
    assert control.is_symlink()
    endpoint = control.resolve(strict=True)
    assert endpoint.parent == Path('/tmp/codex-daemon-' + str(os.getuid()))
    qualifier = root / 'qualify-working-set-native'
    oracle = root / 'evaluate-observation'
    assert qualifier.is_file() and oracle.is_file()
    run_dir = Path(tempfile.mkdtemp(prefix='rlcd-ws-', dir='/run/user/' + str(os.getuid())))
    run_dir.chmod(0o700)
    service_socket = run_dir / 's'
    observer_cli = args.prefix / 'bin/agent-observer-service'
    mesh_cli = args.prefix / 'bin/mesh-plus'
    argv = [str(python), '-I', '-B', str(qualifier), '--codex-home', str(home), '--native-endpoint', str(endpoint),
        '--host-scope', args.host, '--window-hours', '72', '--service-socket', str(service_socket),
        '--candidate-python', str(python), '--candidate-python-sha256', sha(python),
        '--observer-service-cli', str(observer_cli), '--observer-service-cli-sha256', sha(observer_cli),
        '--mesh-cli', str(mesh_cli), '--mesh-cli-sha256', sha(mesh_cli),
        '--observer-wheel-sha256', pair['wheels']['observer']['sha256'],
        '--mesh-wheel-sha256', pair['wheels']['mesh']['sha256'], '--deadline-seconds', '240', '--service-wait-seconds', '90']
    environment = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME', 'CODEX_HOME', 'CLAUDE_CONFIG_DIR'}}
    environment['PYTHONNOUSERSITE'] = '1'
    qualifier_proc = service = None
    records, raw_lines = [], []
    started = time.monotonic()
    service_log = args.output.with_suffix('.service.log')
    selector = selectors.DefaultSelector()
    cleanup = {}
    with open(Path.home() / '.cache/agent-active-feed-cpu.lock', 'a+') as lock, service_log.open('xb') as stderr:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            qualifier_proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, start_new_session=True)
            selector.register(qualifier_proc.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(qualifier_proc.stderr, selectors.EVENT_READ, 'stderr')
            buffers = {'stdout': b'', 'stderr': b''}
            deadline = time.monotonic() + 250
            while selector.get_map():
                if time.monotonic() > deadline:
                    raise TimeoutError('qualification_deadline')
                for key, mask in selector.select(0.25):
                    chunk = os.read(key.fd, 32768)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    kind = key.data
                    buffers[kind] += chunk
                    assert len(buffers[kind]) < 131072, 'qualification_output_limit'
                    if kind == 'stdout':
                        while b'\n' in buffers[kind]:
                            line, buffers[kind] = buffers[kind].split(b'\n', 1)
                            raw_lines.append(line)
                            assert sum(map(len, raw_lines)) < 131072
                            # The qualifier pretty-prints its final receipt; parse
                            # only the compact progress record to start the owner.
                            if b'"event":"native_before_complete"' in line:
                                progress = json.loads(line)
                                records.append(progress)
                                assert service is None
                                service_argv = [str(python), str(observer_cli), 'serve', '--host-scope', args.host,
                                    '--socket', str(service_socket), '--provider', 'codex', '--codex-home', str(home),
                                    '--working-set-window-hours', '72']
                                service = subprocess.Popen(service_argv, stdout=subprocess.DEVNULL, stderr=stderr,
                                    env=environment, start_new_session=True)
                                print(json.dumps({'event': 'private_candidate_started', 'host': args.host, 'pid': service.pid}), flush=True)
            qualifier_proc.wait(timeout=2)
            data = b'\n'.join(raw_lines) + b'\n' + buffers['stdout']
            text = data.decode()
            if records:
                text = text[text.index('\n') + 1:]
            result = json.loads(text)
            result['qualifierReturncode'] = qualifier_proc.returncode
            result['hostScope'] = args.host
            result['qualifierSha256'] = sha(qualifier)
            result['oracleSha256'] = sha(oracle)
        finally:
            for name, proc in [('service', service), ('qualifier', qualifier_proc)]:
                if proc is not None:
                    if proc.poll() is None:
                        proc.terminate()
                    try:
                        proc.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=3)
                    cleanup[name] = {'pid': proc.pid, 'returncode': proc.returncode, 'joined': True}
            selector.close()
            # The native daemon is never signalled. Only private filesystem
            # objects created in this run's directory may be removed.
            remaining = [p.name for p in run_dir.iterdir()]
            for child in run_dir.iterdir():
                assert not child.is_dir()
                child.unlink()
            run_dir.rmdir()
    result['ownedCleanup'] = cleanup
    result['privatePathRetired'] = not run_dir.exists()
    result['seconds'] = time.monotonic() - started
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({k: result.get(k) for k in ['status', 'projectionStatus', 'reasonCode', 'membershipStatus', 'fieldStatus', 'counts', 'qualifierReturncode', 'ownedCleanup', 'seconds']}, sort_keys=True), flush=True)
    return 0 if result.get('projectionStatus') == 'match' or result.get('status') == 'pass' else 3

if __name__ == '__main__':
    raise SystemExit(main())
