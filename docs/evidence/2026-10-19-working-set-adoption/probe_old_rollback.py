from pathlib import Path
import json,re,subprocess
root=Path.home()/'.local/state/rlcd-working-set-adoption/20261019T183334Z';selection=json.loads((Path.home()/'.config/rlcd-agent-dashboard/selection.json').read_text());assert selection['deviceWire']==2
assert json.loads((root/'hardware/old.json').read_text())['allComponentsReadbackMatch']
unit=subprocess.check_output(['systemctl','--user','show','rlcd-agent-dashboard.service','--property=ActiveState,SubState,MainPID,NRestarts,InvocationID,ExecStart'],text=True);assert 'ActiveState=active' in unit and 'NRestarts=0' in unit
inv=subprocess.check_output(['systemctl','--user','show','rlcd-agent-dashboard.service','--property=InvocationID','--value'],text=True).strip();journal=subprocess.check_output(['journalctl','--user','_SYSTEMD_INVOCATION_ID='+inv,'-o','cat','--no-pager'],text=True);assert 'device_ack_recovered' in journal
(root/'old-service-unit.log').write_text(unit);(root/'old-service-journal.log').write_text(journal)
subprocess.run(['systemctl','--user','stop','rlcd-agent-dashboard.service'],check=True)
args=[str(Path.home()/selection['python']),'-I','-B',str(Path.home()/selection['bundle']/'scripts/live-dashboard.py'),'--port',selection['port'],'--seconds','12','--verbose']
r=subprocess.run(args,capture_output=True,text=True,timeout=45);(root/'old-client-verbose.log').write_text(r.stdout+r.stderr);assert r.returncode==0
sent={};checked=[];health=[]
for line in r.stdout.splitlines():
 if line.startswith('{'):
  value=json.loads(line);sent[value['sequence']]=value
 elif line.startswith('RLCD_ACK '):
  pairs=dict(v.split('=',1) for v in line.split()[1:]);original=sent.get(int(pairs['seq']))
  if original is None:continue
  assert pairs['crc']==original['crc'] and int(pairs['request'])==original['request']
  rows=int(pairs['rows']);assert rows==original['rows'] if all(h['status']<2 for h in original['hosts']) else original['rows']<=rows<=32
  checked.append({'request':original['request'],'crc':pairs['crc'],'rows':rows})
 elif line.startswith('RLCD_HEALTH '):health.append(dict(v.split('=',1) for v in line.split()[1:]))
assert len(checked)>=3
report={'wire':2,'selection':selection,'managedUnit':unit,'managedRecoveryEvent':True,'checkedAcknowledgements':checked,'health':health,'nativeCurrentnessAccepted':False,'scope':'exact old managed tuple/image restoration and repeated wire2 CRC/request/count ACK; native source health may remain partial','probeCorrection':'first helper incorrectly expected repeated recovery events; healthy per-frame ACKs refresh the recovery timer, so repeated ACKs are captured here using the unchanged installed verbose bridge'}
with (root/'old-service-rollback.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({'oldWire':2,'managedServiceRan':True,'checkedACKs':len(checked),'nativeCurrentnessAccepted':False}))
