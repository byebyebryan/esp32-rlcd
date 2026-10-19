from pathlib import Path
import argparse,hashlib,json,os,socket,subprocess,time
root=Path.home()/'.local/state/rlcd-working-set-adoption/20261019T183334Z'
ap=argparse.ArgumentParser();ap.add_argument('--host',required=True,choices=['snap','starship']);ap.add_argument('--stage',choices=['final','rollback'],default='final');a=ap.parse_args()
before=json.loads((root/'managed-before.json').read_text())
producer={'.local/bin/agent-observer-service','.config/systemd/user/agent-observer.service','.local/bin/mesh-plus','.config/mesh-plus/sources.toml','.local/bin/mesh-plus-working-set','.config/systemd/user/mesh-plus-agent-working-set.service','.config/systemd/user/default.target.wants/mesh-plus-agent-working-set.service'}
client={'.local/bin/rlcd-agent-dashboard','.config/rlcd-agent-dashboard/selection.json','.config/systemd/user/rlcd-agent-dashboard.service','.config/systemd/user/default.target.wants/rlcd-agent-dashboard.service'}
changed=producer|(client if a.host=='snap' and a.stage=='final' else set());protected=[];rendered=[]
for name,old in before['targets'].items():
 path=Path.home()/name
 if name in changed:
  want=subprocess.check_output(['chezmoi','--refresh-externals=never','cat',str(path)])
  assert (os.readlink(path)==want.decode().strip()) if path.is_symlink() else path.read_bytes()==want,name
  rendered.append(name)
 else:
  if old['kind']=='absent':assert not path.exists() and not path.is_symlink(),name
  elif old['kind']=='symlink':assert path.is_symlink() and os.readlink(path)==old['target'],name
  else:assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==old['sha256'] and path.stat().st_mode&0o777==old['mode'],name
  protected.append(name)
def parse(raw):
 values={}
 for block in raw.strip().split('\n\n'):
  d=dict(line.split('=',1) for line in block.splitlines() if '=' in line)
  if 'Id' in d:values[d['Id']]=d
 return values
oldunits=parse(before['services']);keys=[k for k in oldunits if k!='agent-observer.service' and not(a.host=='snap' and k=='rlcd-agent-dashboard.service')]
raw=subprocess.check_output(['systemctl','--user','show',*keys,'--property=Id,ActiveState,SubState,MainPID,InvocationID,NRestarts'],text=True);units=parse(raw)
for name in keys:
 for field in ['ActiveState','SubState','MainPID','InvocationID','NRestarts']:assert units[name][field]==oldunits[name][field],(name,field)
if a.host=='snap':
 assert subprocess.check_output(['systemctl','--user','is-enabled','rlcd-agent-dashboard.service'],text=True).strip()=='enabled'
 assert subprocess.check_output(['loginctl','show-user','bryan','--property=Linger','--value'],text=True).strip()=='yes'
selection=json.loads((Path.home()/'.config/rlcd-agent-dashboard/selection.json').read_text());assert selection['deviceWire']==(3 if a.host=='snap' and a.stage=='final' else 2)
subprocess.run(['/home/bryan/.local/share/agent-observer/0.7.0a7-a3983afc-ws72-m4f598719/bin/python','-I','-B','/home/bryan/.local/share/agent-observer/0.7.0a7-a3983afc-ws72-m4f598719/artifact/verify_pair.py'],capture_output=True,check=True)
services=subprocess.check_output(['systemctl','--user','show','agent-observer.service','mesh-plus-agent-working-set.service','rlcd-agent-dashboard.service','--property=Id,ActiveState,SubState,MainPID,InvocationID,NRestarts,CPUUsageNSec,MemoryCurrent,MemoryPeak,ExecStart'],text=True)
report={'host':a.host,'stage':a.stage,'protectedManagedTargetsExact':protected,'selectedTargetsMatchCanonical':rendered,'protectedUnitIncarnationsExact':units,'selection':selection,'services':services,'packageInventoryRecordVerified':True,'scope':'scoped exact file/role/process preservation; physical/manual and whole producer gates separate'}
with (root/('final-audit.json' if a.stage=='final' else 'rollback-hold-audit.json')).open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({'host':a.host,'protectedTargets':len(protected),'selectedTargets':len(rendered),'protectedServices':len(units),'status':'pass'}))
