# Prepared read application checkpoint

This independent client pass follows Observer's accepted immutable a5/Mesh a20
producer checkpoint. API 4/read 6/Service 4/Agent profile v3 remain unchanged.
The application uses public prepared read interface 1 and preparation interface
1; it retains wire 2, device expiry and its presentation policy.

## Source and controlled acceptance

Fleet consumes current owned rows and retained source metadata without rebuilding
the full saved roster per device request. Reconnect replaces the helper; gap,
clock failure, disconnect and original expiry revoke claims. Five installed
contract tests pass, including full projection parity with the legacy path,
partial/complete membership, exclusions beyond the USB prefix, independent
history/runtime expiry, heartbeat, mutation, gap/resync and reconnect cleanup.
The 47 existing projection/C admission/runtime/serial/bundle checks, packed-frame
checks, ASan/UBSan motion checks and documentation checks pass independently.
The stdlib suite explicitly skips the five optional installed-contract tests;
the accepted a5 Python runs all five without skips.

The [controlled comparison](controlled-cost.json) runs two hosts with 250 rows
each, one-second device requests, actual SDK IPC/proof/watch and the production
Fleet/projection/serial supervisor. Six fresh processes run D0,D1,D2,D2,D1,D0,
each excluding ten seconds of warm-up before a 30-second decision window.

| Application / dependency tuple | Mean CPU, percent of one core |
| --- | ---: |
| Old `9cc159d` / Observer a1, Mesh a17 | 21.64 |
| Old `9cc159d` / Observer a5, Mesh a20 | 18.43 |
| Prepared application / Observer a5, Mesh a20 | 13.21 |

The prepared application saves 28.30% relative to the old application with the
same new dependencies; the combined change saves 38.96% relative to the old
tuple. Every trial has the same semantic wire signature, six cached native reads,
matching device request/response counts, zero late replies and complete cleanup.
One trial has 30 requests rather than 31 at the measurement boundary.

These numbers include the fixture publishers, Reader and application in one
process. They exclude SSH crypto/server cost, real providers and physical serial.
Unchanged fictional native views retain their original ten-minute leases. They
establish controlled cost/output parity, not ordinary native freshness or the
installed dashboard's CPU. Source, artifact, deployment and device acceptance
remain distinct. Starship flash, live feed, rollback and warmed service cost are
the following delivery gate.
