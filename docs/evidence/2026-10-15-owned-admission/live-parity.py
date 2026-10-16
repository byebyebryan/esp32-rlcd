"""Compare selected versus strict full current projection of one cached generation."""
import argparse
import asyncio
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('--application', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.application/'host'))
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector, selection_reason
from live_dashboard.runtime import Events
from agent_observer.mesh_read import PreparedAgentWatch
from mesh_plus import api
from mesh_plus.evidence import clock_domain
from mesh_plus.transport import boottime_ms

async def main():
    readers = []
    original = api.configured_reader
    async def capture(*a, **kw):
        reader = await original(*a, **kw)
        readers.append(reader)
        return reader
    fleet = Fleet(['starship', 'snap'], Events(io.StringIO()))
    full = None
    with patch.object(api, 'configured_reader', capture):
        task = asyncio.create_task(fleet.run())
        try:
            await asyncio.wait_for(fleet.ready.wait(), 20)
            deadline = asyncio.get_running_loop().time()+20
            while any(s.status != 'current' for s in fleet.sources()):
                if task.done() or asyncio.get_running_loop().time() > deadline:
                    raise ValueError('cached_hosts_not_current')
                await asyncio.sleep(.1)
            raw = fleet.guard.snapshot()
            raw['mesh']['reader'].update(sequence=1, revision=1)
            full = Fleet(fleet.hosts, full_roster=True)
            full.guard.disconnect()
            full.guard = PreparedAgentWatch(fleet.request_id, host_ids=fleet.hosts,
                                            profile=fleet.profile)
            full.guard.accept(raw)
            now, clock = boottime_ms(), clock_domain()
            with patch('mesh_plus.transport.boottime_ms', return_value=now), patch(
                    'mesh_plus.evidence.clock_domain', return_value=clock):
                selected, reference = fleet.sources(), full.sources()
            assert selected == [replace(s, rows=[r for r in s.rows
                if selection_reason(r)=='selected']) for s in reference]
            selected_projector, full_projector = Projector(fleet.hosts), Projector(fleet.hosts)
            view = selected_projector.project(selected)
            assert view == full_projector.project(reference)
            diagnostic = full_projector.explain(reference, view, include_all=True)
            membership = [(s.host, sorted(s.admitted_ids), sorted(s.excluded_ids)) for s in selected]
            result = {'application': str(args.application), 'hostRows': [
                {'host': s.host, 'status': s.status, 'currentFullRows': len(r.rows),
                 'selectedBodies': len(s.rows), 'currentIdentities': len(s.admitted_ids),
                 'positiveExclusions': len(s.excluded_ids)} for s,r in zip(selected,reference)],
                'wireRows': len(view['rows']), 'hosts': view['hosts'],
                'diagnosticRows': len(diagnostic['rows']),
                'selectionCounts': diagnostic['selection_counts'],
                'membershipSha256': hashlib.sha256(json.dumps(membership).encode()).hexdigest(),
                'selectedFullProjectionEqual': True,
                'scope': 'one real cached generation; strict reference resets only reader ordering for a fresh comparison guard, retains original proofs/leases and shared query time; no independent native completeness or physical USB claim'}
        finally:
            if full is not None:
                full.guard.disconnect()
            task.cancel()
            try:
                await asyncio.wait_for(task, 10)
            except asyncio.CancelledError:
                pass
    assert fleet.closed and all(r.inspect()['activeConnections']==0
        and r.inspect()['cleanupFailures']==0 for r in readers)
    result['cleanup'] = True
    return result

result = asyncio.run(main())
args.output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
