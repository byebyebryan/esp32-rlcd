#!/usr/bin/env python3
"""Public configured two-host working-set route; bounded metadata only."""
import argparse
import asyncio
from collections import Counter
import json
import os
from pathlib import Path
import resource
import secrets
import time

from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
from agent_observer.mesh_working_set_read import PreparedWorkingSetAgentWatch
from mesh_plus.api import configured_reader
from mesh_plus.evidence import clock_domain
from mesh_plus.library_authority import LibraryMeshAuthority
from mesh_plus.transport import boottime_ms


async def run(args):
    profile = WorkingSetAgentProfile()
    request_id = secrets.token_hex(16)
    facade = PreparedWorkingSetAgentWatch(request_id, host_ids=['starship', 'snap'], profile=profile)
    authority = LibraryMeshAuthority()
    stream = None
    consumer = None
    proofs = {'starship': set(), 'snap': set()}
    snapshots = []
    count = 0
    started = time.monotonic()
    failure = None
    try:
        reader = await configured_reader('agent', source='agent_working_set',
            socket='/run/user/' + str(os.getuid()) + '/mesh-plus-agent-working-set/read.sock',
            scope='hosts', hosts=['starship', 'snap'], authority=authority, report_routes=False, profile=profile)
        request = {'meshProtocol': 1, 'requestId': request_id, 'operation': 'watch',
            'profile': profile.descriptor.profile_id, 'access': 'cached',
            'selection': {'mode': 'hosts', 'hostIds': ['starship', 'snap']}, 'extensions': {}}
        stream = reader.execute_admitted(request)

        async def receive():
            nonlocal count
            async for frame in stream:
                facade.accept(frame)
                count += 1
                if isinstance(frame, dict) and ('mesh' not in frame or frame['mesh']['kind'] == 'error'):
                    raise RuntimeError('route_terminal')
            raise RuntimeError('route_ended')

        consumer = asyncio.create_task(receive())
        while time.monotonic() - started < args.seconds:
            await asyncio.sleep(1)
            if consumer.done():
                await consumer
            now = boottime_ms()
            read = facade.read(now, clock_domain())
            if read.context is None:
                continue
            by_host = {host: {'members': 0, 'active': 0, 'recentOnly': 0, 'parked': 0, 'uncertain': 0,
                'completeScopes': 0, 'totalScopes': 0} for host in ['starship', 'snap']}
            rows = {tuple(row['identity'].values()): row for row in read.members}
            assert len(read.member_leases) == len(read.members)
            for lease, row in zip(read.member_leases, read.members, strict=True):
                assert lease['identity'] == row['identity']
                assert lease['membershipExpiresAtMs'] > now
                counts = by_host[row['identity']['hostScope']]
                counts['members'] += 1
                counts['active'] += lease['activeExpiresAtMs'] is not None
                counts['recentOnly'] += lease['activeExpiresAtMs'] is None and lease['recentExpiresAtMs'] is not None
                counts['parked'] += row['runtime']['health'] == 'current' and row['runtime']['value'] == 'parked'
            for item in read.uncertain:
                by_host[item['identity']['hostScope']]['uncertain'] += 1
            for scope in read.scopes:
                item = by_host[scope['hostScope']]
                item['totalScopes'] += 1
                item['completeScopes'] += scope['coverage']['status'] == 'complete'
            for host in read.context['hosts']:
                state = by_host[host['hostId']]
                state['delivery'] = host['delivery']['status']
                state['viewState'] = host['viewState']
                proof = host['delivery'].get('proof')
                if proof is not None:
                    proofs[host['hostId']].add(proof['nonce'])
            snapshots.append({'elapsed': round(time.monotonic() - started, 3), 'hosts': by_host})
        assert snapshots, 'route_no_admission'
        last = snapshots[-1]['hosts']
        assert all(x['delivery'] == 'ready' and x['viewState'] == 'current'
                   and x['totalScopes'] > 0 and x['completeScopes'] == x['totalScopes']
                   and x['uncertain'] == 0 for x in last.values()), 'route_incomplete'
        remote = 'starship' if args.local_host == 'snap' else 'snap'
        assert len(proofs[remote]) >= 2, 'route_fresh_proofs_missing'
    except Exception as error:
        # Exceptions can contain upstream details; preserve only a finite type.
        failure = type(error).__name__
    finally:
        if consumer is not None:
            consumer.cancel()
            try:
                await consumer
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        facade.disconnect()
        cleared = facade.read(boottime_ms(), clock_domain())
        assert cleared.context is None and not cleared.members and not cleared.member_leases
        if stream is not None:
            await asyncio.wait_for(stream.aclose(), 5)
        await asyncio.to_thread(authority.close)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {'status': 'pass' if failure is None else 'failed', 'failureType': failure,
        'frames': count, 'seconds': time.monotonic() - started,
        'proofNonces': {k: len(v) for k, v in proofs.items()}, 'samples': snapshots,
        'disconnectedClaimsCleared': True,
        'clientCpuSeconds': usage.ru_utime + usage.ru_stime,
        'completedChildrenCpuSeconds': children.ru_utime + children.ru_stime,
        'clientMaxRssKiB': usage.ru_maxrss,
        'scope': 'actual configured IPC and fixed SSH; descriptive local-client/owned-completed-child resource sample, not whole native pipeline/cost or process memory cap'}
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: report[k] for k in ['status', 'failureType', 'frames', 'seconds', 'proofNonces',
          'clientCpuSeconds', 'completedChildrenCpuSeconds', 'clientMaxRssKiB']}), flush=True)
    if snapshots:
        print(json.dumps(snapshots[-1]), flush=True)
    return 0 if failure is None else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-host', choices=['snap', 'starship'], required=True)
    parser.add_argument('--seconds', type=int, default=25)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert 15 <= args.seconds <= 120
    raise SystemExit(asyncio.run(run(args)))
