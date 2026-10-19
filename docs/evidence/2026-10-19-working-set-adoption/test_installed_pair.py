#!/usr/bin/env python3
"""Selected installed SDK, policy, source and native-correction regressions."""
import gc
import hashlib
import io
import json
from pathlib import Path
import sys
import sysconfig
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent
TESTS = ROOT / 'source-observer/tests'
NAMES = [
    'test_mesh_working_set_profile', 'test_mesh_working_set_read',
    'test_working_set_registered_sdk', 'test_working_set_runtime_retirement',
    'test_working_set_clocks', 'test_working_set_worker_provenance',
    'test_working_set_encoding_refusal', 'test_working_set_source',
    'test_codex_snapshot', 'test_observation_evaluation', 'test_working_set_member_leases',
]

def main():
    sys.path.insert(0, str(TESTS))
    gc.disable()
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in NAMES)
    sink = io.StringIO()
    result = unittest.TextTestRunner(stream=sink, verbosity=2).run(suite)
    slot = str(sys.version_info.major) + str(sys.version_info.minor)
    (ROOT / ('installed-focused-' + slot + '.log')).write_text(sink.getvalue())
    site = Path(sysconfig.get_path('purelib')).resolve()
    loaded = []
    pair = json.loads((ROOT / 'pair.json').read_text())
    wheel_entries = {}
    for label in ['observer', 'mesh']:
        wheel = ROOT / 'wheels' / Path(pair['wheels'][label]['path']).name
        with zipfile.ZipFile(wheel) as z:
            wheel_entries.update({n: z.read(n) for n in z.namelist() if not n.endswith('/')})
    for name, module in tuple(sys.modules.items()):
        if not name.startswith(('agent_observer', 'mesh_plus')) or not getattr(module, '__file__', None):
            continue
        p = Path(module.__file__).resolve()
        assert p.is_relative_to(site), str(p)
        rel = p.relative_to(site).as_posix()
        assert p.read_bytes() == wheel_entries[rel], rel
        loaded.append({'module': name, 'path': rel, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    report = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'gcDisabled': not gc.isenabled(), 'modules': NAMES,
        'loadedModules': loaded, 'python': sys.executable,
        'scope': 'installed package tests with immutable source test/oracle helpers; synthetic fixtures do not establish native deployment'}
    (ROOT / ('installed-focused-' + slot + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['tests', 'failures', 'errors', 'skipped', 'gcDisabled', 'python']}), flush=True)
    return 0 if result.wasSuccessful() and not result.skipped else 1

if __name__ == '__main__':
    raise SystemExit(main())
