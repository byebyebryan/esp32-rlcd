"""Serial fresh-process A/B/C/C/B/A full application/dependency comparison."""
import json
import pathlib
import statistics
import subprocess

root = pathlib.Path(__file__).resolve().parent
old_python = '/home/bryan/.local/share/agent-observer/0.7.0a5-25cd5663560c973b-cpu/bin/python'
new_python = '/home/bryan/.local/share/rlcd-agent-dashboard-python/a6-a22-e01a7129-5ac484d7/bin/python'
old_app = '/home/bryan/.local/share/rlcd-agent-dashboard/807eab96b48825ae'
new_app = '/home/bryan/.cache/rlcd-integration-bundles/b24f7536e650f0d0'
script = '/home/bryan/code/esp32-rlcd/projects/agent-dashboard/scripts/measure-prepared-client.py'
variants = {'A': (old_python, old_app), 'B': (new_python, old_app), 'C': (new_python, new_app)}
trials = []
for index, label in enumerate(('A', 'B', 'C', 'C', 'B', 'A'), 1):
    python, app = variants[label]
    output = root/f'controlled-{index}-{label}.json'
    process = subprocess.run(['rtk', 'proxy', python, '-I', '-B', script,
        '--application', app, '--warmup', '5', '--seconds', '30', '--rows', '250',
        '--output', str(output)], capture_output=True, text=True, timeout=65)
    (root/f'controlled-{index}-{label}.log').write_text(process.stdout+process.stderr)
    process.check_returncode()
    trial = json.loads(output.read_text())
    assert trial['cleanup'] and trial['counts']['lateResponses'] == 0
    assert trial['counts']['deviceRequests'] == trial['counts']['responses']
    trials.append({'label': label, **trial})
    print(json.dumps({'trial': index, 'variant': label,
        'percentOneCore': trial['percentOneCore'], 'counts': trial['counts']}), flush=True)
signatures = {s for t in trials for s in t['semanticSignatures']}
membership = {s for t in trials for s in t['membershipSignatures']}
assert len(signatures) == len(membership) == 1
means = {label: statistics.mean(t['percentOneCore'] for t in trials if t['label']==label)
         for label in variants}
result = {'order': [t['label'] for t in trials], 'meanPercentOneCore': means,
    'combinedReductionPercent': (1-means['C']/means['A'])*100,
    'consumerReductionPercent': (1-means['C']/means['B'])*100,
    'dependenciesReductionPercent': (1-means['B']/means['A'])*100,
    'semanticSignatures': sorted(signatures), 'membershipSignatures': sorted(membership),
    'allCleanup': True, 'trials': trials,
    'limits': ['synthetic full pipeline including fixture publishers, Reader and application',
        'owned IPC/proof and fake serial; no providers, SSH crypto/server or physical USB',
        'fixed 500-row inputs, unchanged source cadence and original ten-minute fixture leases',
        'two trials per variant; uncontrolled host frequency/activity; no confidence interval or live saving claim']}
(root/'controlled-cost.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='trials'}), flush=True)
