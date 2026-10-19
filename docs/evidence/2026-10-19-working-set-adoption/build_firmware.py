#!/usr/bin/env python3
"""Fresh Snap wire-3 build from the exact clean adopted source checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

REPO = Path.home() / 'code/esp32-rlcd'
ROOT = Path.home() / '.local/state/rlcd-working-set-adoption/20261019T183334Z'
BUILD = REPO / 'projects/agent-dashboard/build-snap-working-set-20261019T183334Z'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    assert subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip() == args.source
    assert not subprocess.check_output(['git', '-C', str(REPO), 'status', '--porcelain'])
    root = ROOT / 'firmware'
    root.mkdir(mode=0o700)
    original = REPO / 'projects/agent-dashboard/sdkconfig'
    assert sha(original) == '21195fd64798f857638982d8b68e61b3aed72d118ddfd1964cf53363ae0ed7d8'
    shutil.copy2(original, root / 'sdkconfig-before')
    config = root / 'sdkconfig-live'
    shutil.copy2(original, config)
    assert 'CONFIG_RLCD_DASHBOARD_LIVE=y' in config.read_text()
    assert 'CONFIG_RLCD_DASHBOARD_STATIC_STUDY=y' not in config.read_text()
    assert not BUILD.exists()
    exclude = Path(subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', '--git-path', 'info/exclude'], text=True).strip())
    if not exclude.is_absolute():
        exclude = REPO / exclude
    entry = '/' + BUILD.relative_to(REPO).as_posix() + '/'
    assert entry not in exclude.read_text().splitlines()
    with exclude.open('a') as stream:
        stream.write('\n' + entry + '\n')
    argv = [str(REPO / 'scripts/idf.sh'), '-C', str(REPO / 'projects/agent-dashboard'),
            '-B', str(BUILD), '-D', 'SDKCONFIG=' + str(config), 'build']
    with (root / 'build.log').open('xb') as log:
        result = subprocess.run(argv, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, timeout=600)
    assert result.returncode == 0, 'firmware_build_failed'
    assert subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip() == args.source
    assert not subprocess.check_output(['git', '-C', str(REPO), 'status', '--porcelain'])
    args_json = json.loads((BUILD / 'flasher_args.json').read_text())
    assert args_json['extra_esptool_args']['chip'] == 'esp32s3'
    assert args_json['flash_settings'] == {'flash_mode': 'dio', 'flash_size': '16MB', 'flash_freq': '80m'}
    assert set(args_json['flash_files']) == {'0x0', '0x10000', '0x8000'}
    files = {}
    for offset, relative in args_json['flash_files'].items():
        path = BUILD / relative
        files[relative] = {'offset': offset, 'bytes': path.stat().st_size, 'sha256': sha(path)}
    assert files['rlcd-dashboard.bin']['bytes'] < 2 * 1024 * 1024
    report = {'source': args.source, 'build': str(BUILD), 'idfVersion': '5.5.3', 'deviceWire': 3,
              'sdkconfigSha256': sha(config), 'defaultConfigUnchanged': sha(original) == sha(root / 'sdkconfig-before'),
              'files': files}
    (root / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    main()
