"""Descriptive selected-unit cgroup telemetry, not a producer budget test."""
from pathlib import Path
import argparse,json,subprocess,time
ap=argparse.ArgumentParser();ap.add_argument('--host',choices=['snap','starship'],required=True);ap.add_argument('--seconds',type=int,default=65);a=ap.parse_args();assert 60<=a.seconds<=120
units=['agent-observer.service','mesh-plus-agent-working-set.service','rlcd-agent-dashboard.service']
root=Path.home()/'.local/state/rlcd-working-set-adoption/20261019T183334Z'
def sample():
 raw=subprocess.check_output(['systemctl','--user','show',*units,'--property=Id,ActiveState,SubState,MainPID,InvocationID,NRestarts,CPUUsageNSec,MemoryCurrent,MemoryPeak'],text=True)
 result={}
 for block in raw.strip().split('\n\n'):
  d=dict(line.split('=',1) for line in block.splitlines() if '=' in line);result[d['Id']]=d
 return result
start=time.monotonic();first=sample();samples=[]
while True:
 now=time.monotonic();current=sample();samples.append({'elapsed':now-start,'units':current})
 for name in units:
  assert current[name]['InvocationID']==first[name]['InvocationID'] and current[name]['ActiveState']=='active' and current[name]['NRestarts']==first[name]['NRestarts']=='0',name
 if now-start>=a.seconds:break
 time.sleep(min(2,a.seconds-(now-start)))
elapsed=time.monotonic()-start;last=samples[-1]['units'];stats={}
for name in units:
 used=(int(last[name]['CPUUsageNSec'])-int(first[name]['CPUUsageNSec']))/1e9
 stats[name]={'cpuSeconds':used,'percentOneCore':used/elapsed*100,'memoryCurrentBytes':int(last[name]['MemoryCurrent']),'memoryPeakBytes':int(last[name]['MemoryPeak']),'sampledCurrentMinimumBytes':min(int(x['units'][name]['MemoryCurrent']) for x in samples),'sampledCurrentMaximumBytes':max(int(x['units'][name]['MemoryCurrent']) for x in samples),'restarts':int(last[name]['NRestarts']),'invocation':last[name]['InvocationID']}
report={'host':a.host,'seconds':elapsed,'units':stats,'samples':samples,'scope':'uncontrolled descriptive selected systemd cgroups; CPU includes each unit children, but remote SSH server/bridge processes and native daemon outside these units are excluded; shared pages/cgroup memory are not unique physical RAM or proof of inclusive32/64MiB producer caps; Starship RLCD remains old active profile'}
with (root/'working-set-final-resource.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({'host':a.host,'seconds':elapsed,'units':stats}))
