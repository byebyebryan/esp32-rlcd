"""Descriptive owned-service resource window; does not add a source reader."""
import argparse
import json
import pathlib
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--seconds', type=int, default=120)
parser.add_argument('--warmup', type=int, default=0)
parser.add_argument('--output', type=pathlib.Path, required=True)
args = parser.parse_args()
names = ['rlcd-agent-dashboard.service', 'agent-observer.service', 'mesh-plus-agent.service']

def sample():
    text = subprocess.check_output(['rtk', 'proxy', 'systemctl', '--user', 'show', *names,
        '-p', 'Id', '-p', 'MainPID', '-p', 'ExecMainStartTimestampMonotonic',
        '-p', 'NRestarts', '-p', 'ActiveState', '-p', 'ControlGroup'], text=True)
    result = {}
    for block in text.strip().split('\n\n'):
        fields = dict(line.split('=', 1) for line in block.splitlines())
        cgroup = pathlib.Path('/sys/fs/cgroup') / fields['ControlGroup'].lstrip('/')
        usage = dict(line.split() for line in (cgroup/'cpu.stat').read_text().splitlines())
        row = {'unit': fields, 'cpuUs': int(usage['usage_usec'])}
        if fields['Id'] == names[0]:
            processes = []
            for pid in (cgroup/'cgroup.procs').read_text().split():
                proc = pathlib.Path('/proc')/pid
                try:
                    memory = {k: int(v.strip().split()[0]) for k, v in
                              (line.split(':', 1) for line in (proc/'smaps_rollup').read_text().splitlines() if ':' in line)}
                    processes.append({'pid': int(pid), 'rssKiB': memory['Rss'],
                        'pssKiB': memory['Pss'], 'fds': len(list((proc/'fd').iterdir()))})
                except (FileNotFoundError, ProcessLookupError):
                    pass
            row['processes'] = processes
        result[fields['Id']] = row
    return result

remaining = args.warmup
while remaining > 0:
    delay = min(10, remaining)
    time.sleep(delay)
    remaining -= delay
start = time.monotonic()
samples = [{'seconds': 0, 'units': sample()}]
while time.monotonic() - start < args.seconds:
    time.sleep(min(10, args.seconds - (time.monotonic() - start)))
    samples.append({'seconds': time.monotonic()-start, 'units': sample()})
elapsed = samples[-1]['seconds']
before, after = samples[0]['units'], samples[-1]['units']
percent = {name: (after[name]['cpuUs']-before[name]['cpuUs']) / elapsed / 10000 for name in names}
stable = all(s['units'][name]['unit'] == before[name]['unit'] for s in samples for name in names)
result = {'seconds': elapsed, 'warmupSeconds': args.warmup, 'percentOneCore': percent, 'incarnationsStable': stable,
    'samples': samples, 'scope': 'ordinary selected service; no added reader; source/native activity and host frequency uncontrolled; descriptive only'}
args.output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='samples'}))
assert stable
