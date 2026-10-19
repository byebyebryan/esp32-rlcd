#!/usr/bin/env python3
"""Build new private wheels from Git objects and install without network access."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time
import zipfile

ROOT = Path(__file__).resolve().parent
OLD = Path('/home/bryan/.cache/agent-observer-working-set-20261018/installed-pair-b176ac06-bfa91a69')
BUILD_PY = '/home/bryan/code/agent-observer/.local/active-feed-20261016/installed311/bin/python'
BASES = {'311': BUILD_PY, '314': '/home/bryan/code/mesh-plus/.venv/bin/python'}
SPECS = {
    'observer': ('/home/bryan/code/agent-observer-rlcd-adoption-20261019', '1eec6c6d8681a3e58bab742d5c130656ab00433c', 'agent_observer', 'agent_observer'),
    'mesh': ('/home/bryan/code/mesh-plus-working-set', '2fb502da35c0ef9865762c4dc4b486dd30b7e316', 'src/mesh_plus', 'mesh_plus'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name, obj):
    with (ROOT / name).open('x') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write('\n')

def run(name, argv, **kwargs):
    start = time.monotonic()
    result = subprocess.run(argv, capture_output=True, timeout=300, **kwargs)
    for suffix, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (ROOT / (name + '.' + suffix)).write_bytes(content)
    record = {'argv': argv, 'returncode': result.returncode, 'seconds': time.monotonic() - start,
              'stdoutSha256': sha(result.stdout), 'stderrSha256': sha(result.stderr)}
    save(name + '.json', record)
    if result.returncode:
        print(result.stderr.decode(errors='replace')[-2000:], flush=True)
        raise RuntimeError(name + '_failed')
    return result.stdout

def main():
    wheels = ROOT / 'wheels'
    wheels.mkdir()
    report = {'sources': {}, 'wheels': {}, 'environments': {}, 'offline': True}
    for name, (repo, commit, package_source, package_name) in SPECS.items():
        assert not subprocess.check_output(['git', '-C', repo, 'status', '--porcelain'])
        export = ROOT / ('source-' + name)
        export.mkdir()
        archive = subprocess.check_output(['git', '-C', repo, 'archive', '--format=tar', commit])
        with tarfile.open(fileobj=io.BytesIO(archive)) as reader:
            reader.extractall(export, filter='data')
        manifest = []
        for raw in subprocess.check_output(['git', '-C', repo, 'ls-tree', '-r', '-z', commit]).split(b'\0'):
            if not raw:
                continue
            meta, path_raw = raw.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            path = path_raw.decode()
            assert kind == 'blob'
            data = (export / path).read_bytes()
            wanted = subprocess.check_output(['git', '-C', repo, 'cat-file', 'blob', oid])
            assert data == wanted, path
            manifest.append({'path': path, 'gitBlob': oid, 'sha256': sha(data), 'bytes': len(data)})
        save(name + '-source-manifest.json', manifest)
        report['sources'][name] = {'repo': repo, 'commit': commit, 'archiveSha256': sha(archive), 'files': len(manifest)}
        build = ROOT / ('build-' + name)
        build.mkdir()
        for file in ['pyproject.toml', 'README.md', 'LICENSE']:
            if (export / file).is_file():
                shutil.copy2(export / file, build / file)
        shutil.copytree(export / package_source, build / package_source)
        code = 'from setuptools.build_meta import build_wheel; build_wheel(' + repr(str(wheels)) + ')'
        run('build-' + name, [BUILD_PY, '-I', '-B', '-c', code], cwd=build, env={**os.environ, 'SOURCE_DATE_EPOCH': '1792432800'})
        wheel = next(wheels.glob(package_name + '-*.whl'))
        count = 0
        with zipfile.ZipFile(wheel) as z:
            wheel_package = {p: z.read(p) for p in z.namelist() if p.startswith(package_name + '/') and not p.endswith('/')}
        source_package = {package_name + '/' + p.relative_to(export / package_source).as_posix(): p.read_bytes()
                          for p in (export / package_source).rglob('*') if p.is_file()}
        assert wheel_package == source_package, name + '_wheel_source_parity'
        report['wheels'][name] = {'path': str(wheel), 'sha256': sha(wheel.read_bytes()), 'bytes': wheel.stat().st_size,
                                 'packageFiles': len(wheel_package)}
        print(name, report['wheels'][name], flush=True)
    prefix = Path.home() / '.local/share/agent-observer' / ('0.7.0a7-' + report['wheels']['observer']['sha256'][:8] + '-ws72-m' + report['wheels']['mesh']['sha256'][:8])
    for slot, base in BASES.items():
        env = prefix if slot == '314' else ROOT / ('venv-' + slot)
        assert not env.exists(), str(env)
        run('venv-' + slot, [base, '-I', '-m', 'venv', '--copies', str(env)])
        python = str(env / 'bin/python')
        run('dependencies-' + slot, [python, '-I', '-m', 'pip', 'install', '--no-index', '--disable-pip-version-check',
             '--no-cache-dir', '--find-links', str(OLD / ('dependency-wheels-' + slot)), '--require-hashes', '-r',
             str(OLD / ('dependency-requirements-' + slot + '.txt'))])
        run('applications-' + slot, [python, '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', '--disable-pip-version-check',
             report['wheels']['observer']['path'], report['wheels']['mesh']['path']])
        run('pip-check-' + slot, [python, '-I', '-m', 'pip', 'check'])
        report['environments'][slot] = {'prefix': str(env), 'python': python,
            'pythonSha256': sha((env / 'bin/python').read_bytes()),
            'version': subprocess.check_output([python, '-I', '-c', 'import platform;print(platform.python_version())'], text=True).strip()}
    save('pair.json', report)
    print(json.dumps(report, sort_keys=True), flush=True)

if __name__ == '__main__':
    main()
