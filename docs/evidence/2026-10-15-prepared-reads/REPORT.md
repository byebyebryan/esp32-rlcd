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
remain distinct.

## Artifact and Starship delivery

Client source `1e20604` implements prepared reads. Source freeze `19323e6` also
corrects the stale boot diagnostic from wire 1 to the implemented wire 2. Both
hosts independently build and verify the same clean [bundle manifest](bundle.json):
`807eab96b48825ae94f1ce6bfe5a7f85f235e446ad3a8e3d1565542196f073c5`.
The selected Python is Observer a5/Mesh a20, with public preparation/read
interfaces 1. Five installed-contract tests pass on each host. Source is pushed
and synced to Starship; [hosted CI](ci.json) passes native, Debug and Release
presentation jobs for `19323e6`, separately from installed/device acceptance.

[ESP-IDF 5.5.3 builds](firmware-build.json) the selected dashboard application on Starship. Exclusive
serial preflight confirms the RLCD MAC `94:a9:90:f3:43:74`, 16 MiB flash and
the unchanged 2 MiB application layout. The [full backup](backup.json), old slot,
unit and selection remain private under the recorded backup directory. No serial
permission change is needed. The other connected device remains untouched.

The [application readback](firmware-readback.json) exactly matches the new
1,242,640-byte image, SHA-256
`0ecdc4cd7e3f87a664ad3554f865751106dc2e6601494494e21770319a1f4eca`.
Bootloader/partition prefix bytes remain equal to backup. The [boot capture](boot.json)
records one start, the expected source version, wire-2 requests and zero errors.

The installed bundle's [real cached-feed capture](live-capture.json) confirms
24 healthy CRC/request/row agreements before and after six seconds of silence.
Nine real rows come from both hosts. Silence clears all phase/age claims and
retains uncertain identities; recovery restores admitted state. Maximum sampled
frame time is 17,667 microseconds, with zero deadline misses, 292,171 bytes of
internal heap and a 4,776-byte stack watermark. Buffered old requests explain
extra rejected sends in the initial window; only matching positive ACKs count.

The physical device separately passes [failure/retry/expiry](failure-device.json)
and [single-host loss/recovery](partial-device.json) with fictional source data
through production projection and wire code. In the latter, one sibling stays
working while the lost host becomes uncertain, recovery restores both, and
silence clears both. These are controlled device proofs, not provider evidence.

[Rollback](firmware-rollback.json) restores and reads back the exact old 2 MiB
slot. The [actually running old managed bundle](old-managed.json), with its
retained a1/a17 Python, confirms nine admitted real rows. Candidate firmware is
then flashed/read back again and the [new managed bundle](new-managed.json)
receives healthy real ACKs with one serial owner. Scoped dotfiles commit
`447aa18` selects this pair; complete source checks and exact rendered/installed
artifact checks pass. Only the RLCD service changes during this client gate;
collector, Agent publisher, Tmux and 349 owners retain their incarnations.

[Protected-state comparison](protected.json) records unchanged unrelated targets,
non-Codex configuration and USB identities. Concurrent notification work advances
Codex configuration and foreign managed commits; this pass performs no provider
configuration writes and preserves the current bytes and unrelated commits.
Manual panel/readability and host reboot acceptance remain deferred.

## Fan-out and remaining cost

A separate [one/two-reader comparison](fanout-cost.json), at the same 500-row
shape and one-second requests, runs fresh processes in 1,2,2,1 order, excluding
five seconds of warm-up before 20-second windows. One prepared reader averages
13.11% of one core; two average 21.65%, an additional 8.54 points for the same
owned publisher pair. Outputs match with zero late replies and complete cleanup.
Cached native reads scale from four to seven/eight per window. This includes
the fixture pipeline and excludes real SSH/providers/hardware. It identifies a
remaining repeated acquisition/admission cost, not a shared-reader implementation
or permission to weaken proof/expiry.

The separate warmed installed-service windows each last 300 seconds with no
added reader. The [old application](old-live-cost.json), after Observer rollout,
uses 20.99% of one core; the [prepared application](new-live-cost.json), sampled
after at least 60 seconds of process warm-up, uses 12.76%. The
[summary](live-cost-summary.json) records a 39.20% relative reduction. Ordinary
native work is uncontrolled and native frame/request counts were not captured
in these service windows; this is descriptive, supported by the separate matched
controlled comparison rather than claimed as a causal service A/B test.
Both windows retain stable unit incarnations. Candidate mean/peak PSS are
47.41/47.44 MiB; mean/peak RSS are 68.51/68.51 MiB. Both have two processes and
19 file descriptors. Memory is essentially flat against the old 47.97 MiB mean
PSS. Application cgroup and process-tree CPU overlap and must not be added.
A separate [cold fixture probe](startup-cost.json) consumes 1.995 CPU seconds
over 5.148 seconds of remaining imports, owner/client startup and warm-up,
followed by 13.33% steady CPU. Timing starts after importing Python's `time`
module and excludes interpreter bootstrap. This combined controlled-pipeline
startup measurement is separate from the ordinary installed-service windows.

The separate 45-second endpoint samples include collector helpers in unit CPU:
[Starship](starship-unit-cost.json) uses 1.83% collector and 3.34% resident
publisher, while [Snap](snap-unit-cost.json) uses 1.53% collector, 0% unused
resident publisher and 1.58% for the SSH-hosted Agent source outside that unit.
These are ordinary-workload snapshots, not universal rates. Short-lived helpers
and SSH server/crypto are not fully observed by stable-process accounting.
The 300-second Starship window instead averages 2.88% collector and 4.84%
publisher, illustrating activity/cadence variation. Neither should be hidden
inside or added twice to the application tree total.

The [final managed gate](final-managed.json) retains the selected bundle, healthy
device diagnostics, one serial owner and unchanged protected service
incarnations. Remaining costs are Reader/native-body acquisition and admission,
proof/carrier composition and each client's independent projection/serial work.
Further Mesh or presentation optimization needs a separate measured checkpoint;
this pass changes no cadence, evidence lease, discovery scope or API contract.
