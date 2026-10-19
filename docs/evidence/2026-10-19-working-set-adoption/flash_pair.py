#!/usr/bin/env python3
"""Exact Snap board, verified backup and paired component writes only."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path.home()/'.local/state/rlcd-working-set-adoption/20261019T183334Z'
PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:DE:D0:04-if00'
PYTHON=str(Path.home()/'.espressif/tools/python/v5.5.3/venv/bin/python')
OLD=Path.home()/'code/esp32-rlcd/projects/agent-dashboard/build-snap-live-20261019T164832Z'
KNOWN={'bootloader/bootloader.bin':'e5249398e4c1a9aa41297d988f45a0d0244a88d9266ce977a6fd02ff4bca0c4f','partition_table/partition-table.bin':'5e71c3c890e04714daa03b21a0d23953a2dadf9fdf15eec02b886f7b6e9f8c81','rlcd-dashboard.bin':'243ca45f8a18f43d72e9ecb4357ec34f6340c759a0db305b2ab807e65261d4d2'}
OFF={'bootloader/bootloader.bin':0,'partition_table/partition-table.bin':0x8000,'rlcd-dashboard.bin':0x10000}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(log,args,timeout=400):
 r=subprocess.run(args,capture_output=True,timeout=timeout)
 log.write_bytes(r.stdout+r.stderr)
 assert r.returncode==0,(args[0],r.returncode,str(log))
 return r.stdout+r.stderr
def main():
 ap=argparse.ArgumentParser();ap.add_argument('operation',choices=['backup','new','old','new-final']);a=ap.parse_args()
 root=ROOT/'hardware';root.mkdir(exist_ok=True,mode=0o700)
 assert os.path.realpath(PORT).startswith('/dev/ttyACM')
 props=subprocess.check_output(['udevadm','info','--query=property','--name',PORT],text=True)
 assert 'ID_SERIAL_SHORT=94:A9:90:DE:D0:04' in props
 for f,h in KNOWN.items():assert sha(OLD/f)==h
 subprocess.run(['systemctl','--user','stop','rlcd-agent-dashboard.service'],check=True)
 assert subprocess.run(['fuser',PORT],capture_output=True).returncode==1,'usb_owner_present'
 base=[PYTHON,'-m','esptool','--chip','esp32s3','--port',PORT,'--baud','460800']
 assert not (root/(a.operation+'.json')).exists()
 mac=run(root/(a.operation+'-mac.log'),base+['read_mac'])
 assert b'94:a9:90:de:d0:04' in mac.lower()
 report={'operation':a.operation,'port':PORT,'mac':'94:a9:90:de:d0:04','349Touched':False}
 if a.operation=='backup':
  backup=root/'flash-wire2-before.bin';assert not backup.exists()
  run(root/'backup.log',base+['read_flash','0','0x1000000',str(backup)],600)
  data=backup.read_bytes();assert len(data)==16777216
  for f,offset in OFF.items():assert data[offset:offset+(OLD/f).stat().st_size]==(OLD/f).read_bytes(),f
  report.update(bytes=len(data),sha256=sha(backup),allOldComponentsMatch=True)
 else:
  backup=root/'flash-wire2-before.bin';saved=json.loads((root/'backup.json').read_text())
  assert sha(backup)==saved['sha256']
  if a.operation=='old':build=OLD;expected=KNOWN
  else:
   built=json.loads((ROOT/'firmware/build.json').read_text());build=Path(built['build'])
   expected={f:v['sha256'] for f,v in built['files'].items()}
  for f,h in expected.items():assert sha(build/f)==h
  args=base+['write_flash','--flash_mode','dio','--flash_freq','80m','--flash_size','16MB']
  for f,offset in sorted(OFF.items(),key=lambda x:x[1]):args.extend([hex(offset),str(build/f)])
  run(root/(a.operation+'-write.log'),args,300)
  readback=root/(a.operation+'-readback.bin');end=0x10000+(build/'rlcd-dashboard.bin').stat().st_size
  run(root/(a.operation+'-readback.log'),base+['read_flash','0',hex(end),str(readback)],300)
  data=readback.read_bytes()
  for f,offset in OFF.items():assert data[offset:offset+(build/f).stat().st_size]==(build/f).read_bytes(),f
  report.update(build=str(build),files=expected,allComponentsReadbackMatch=True,readbackSha256=sha(readback))
 (root/(a.operation+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
