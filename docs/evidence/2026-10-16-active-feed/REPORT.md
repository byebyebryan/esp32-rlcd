# Active feed integration and service CPU

2026-10-16 UTC. Observer a7 and Mesh a23 are selected with the RLCD host client
after independent producer acceptance, installed consumer checks and actual
paired rollback. The normal fleet uses a cached active projection before service
IPC; full inventory remains available. Physical device acceptance is deferred:
Starship had no `/dev/serial/by-id` before or after the switch, and the preceding
RLCD process already logged `serial_missing`.

## Exact selection

[Artifact bindings](artifacts.json) pin Observer runtime `7807160`, wheel
`5eafd4c1…`, and Mesh runtime `1978805`, wheel `73455186…`. Their owner acceptance
revisions are `b0cea487` and `b0d78604`. Installed readback on Starship and Snap
matches every one of 63 Observer and 67 Mesh runtime/schema files to the wheels;
all imported owner modules come from the selected prefix. Python is 3.14.8.

RLCD runtime is `7033725`; immutable bundle `519f202dff6d03c2`, manifest SHA-256
`519f202dff6d03c2c8b102c1fca01720683a2ac71a94364ddea96b43daa30545`.
Managed source checkpoint `c0d184b` selects the new collector and isolated active
publisher/source on both hosts and the client on Starship. Existing full reader,
full publisher, historical writer, Tmux and 349 selections remain independent.
No firmware changed; device wire 2 remains.

The prior operational tuple is retained: collector a3, full publisher/reader a5
with Mesh a20, and RLCD bundle `5bf9f44fa523123c` with a6/a22. Producer performance
baselines are separately scoped and must not be confused with this deployed tuple.

## Semantics and installed checks

The fixed selector admits current running Codex user/unknown-kind conversations,
including loaded waiting, blocked and errored sessions. Exact positive nonmembers
and fresh complete host/provider/namespace coverage reconcile the whole retained
roster before its 32-row device prefix. New namespaces do not clear prior scopes.
Partial omissions, expired facts, pruning, overflow and missed expired negatives
do not silently retire uncertain presentation context. No hide timeout or prior-ID
query was added.

Active read 1 masks independently expired fields and validates complete-empty
coverage independently of bodies. Raw owner context is informational. Activity age
uses each member's original current `runtime.observedAt`, `clock=sample`, when its
current activity is no later than that observation. The active DTO omits full
snapshot publication `collectedAt`; cached proof/emission cannot advance this
per-row source observation anchor. Full diagnostics retain their original route.

All 63 installed consumer tests pass without skips, including native C feed
admission/render checks under address/undefined-behavior sanitizers. Tests include
nominal full-view parity, diagnostics, complete-empty expiry, missed negatives,
independent field expiry, same-key support rejection, removal beyond row 32,
namespace/host isolation, control/clock revocation and owned reconnect/catalog
cleanup. Documentation/media provenance checks pass; generated media bytes are
unchanged. The complete dotfiles check and installed source-dispatch/bundle gates
pass. Source dispatch preserves effective last-value/equals syntax and switches
only `agent_active` serve/bridge calls before Mesh/Observer imports.

## Matched controlled cost

[Controlled results](controlled.json) compare exact installed old/client and new
active tuples in serial ABBA order at each scale. Each run performs twelve cached
native reads, six changing replacements and eighteen projection/wire reads. Full
uncapped presentation and wire signatures agree in all twelve runs; cleanup passes.
Both hosts use owned IPC with remote nonce evidence, rather than real SSH crypto.

| Total inventory identities, six selected | Full CPU | Active CPU | Reduction | Full received bytes | Active received bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100 | 979.03 ms | 245.46 ms | 74.93% | 1,683,753 | 267,946 |
| 500 | 4,815.59 ms | 241.72 ms | 94.98% | 8,031,653 | 267,946 |
| 2,000 | 17,350.30 ms | 241.44 ms | 98.61% | 31,841,153 | 267,946 |

These include owned publisher, Reader, actual Fleet conversion, uncapped projector,
wire encoding and semantic hashing. Native collection, fixture/projection
construction, service hosting, catalog checks, SSH crypto and physical USB are
outside this timer. Original ten-minute fixture leases are synthetic, never live
freshness evidence. Two samples per mode/case on an uncontrolled host are not a
confidence interval; the full 500-row pair varies materially. Initial harness
setup without its required static catalog monitor callback was rejected before
measurement. Only the final runtime's twelve passing samples appear here.

Observer separately reports increased generation work (about 30–38%) and a7 full
workload cost (about 9–10%) versus its a6 baseline; its projected producer workload
recovers that cost through cheaper cached reads. Mesh separately qualifies the
library catalog adapter against the selected process authority. Those percentages
have different scopes and cannot be added to this table or presented as live
whole-system savings. The 5,000-row capacity case is a rejected capacity probe,
not throughput evidence; the producer's full-2,000 allocation timeout is excluded.

## Real configured feed and rollback

Same-generation cached views from the newly selected normal collectors match
400 full / eight selected identities on Starship and 104 / one on Snap. Both
scopes are complete; selected identities and every current runtime, phase,
activity, outcome and timing field match their full records. This is fresh bounded
populated-source evidence; ordinary native activity continues independently.

The actual configured Fleet observes local IPC and fixed SSH with nonce proof,
complete scopes and selected bodies, and closes its owned streams. Snap's normal
local active IPC route passes independently. A separate [live wire check](live-wire.json)
then exercises the ordinary serial worker at one-second cadence against an owned
simulated device running production native C admission/rendering: 31 requests and
31 accepted frames, admitted source-backed ACK, healthy eight-row final state and
complete cleanup. It is software evidence, not physical USB/panel acceptance.
The full v3 diagnostic route retains
504 current bodies and the same eight then-selected presentation rows. The
application performs no session start/resume/archive/hide/unload/repair actions.

The rollback drill stops only affected units, restores exact prior bytes/modes/
links on both hosts, removes active source/startup targets and restores the a3
collectors plus old RLCD client. The actual old a6/a22 client recovers populated
full IPC/SSH views. Reselect then restores the accepted tuple. Chezmoi's
last-applied state initially rejected that known archive restoration as conflict;
all thirteen saved paths were verified unchanged against backup before forced
application of only the reviewed role targets. No unrelated drift was overwritten.
Interrupted resource scheduling during that reselect was excluded.

Tmux owner/fleet/desktop and 349 service incarnations remain unchanged on both
hosts, as do full-publisher units and reader/writer links. Both captured Tmux
fleet status endpoints return without error. Retained rollback archives are under
`~/.local/state/esp32-rlcd/backups/20261016T-active-feed/` on both hosts. Private
integration receipts are in `.cache/active-feed-integration/20261016T052335Z/`.

## Selected service resources

[Passive resource windows](live-resources.json) cover two minutes before and after,
with sixty seconds of candidate warm-up, no added source reader and stable unit
incarnations/restart counts throughout each window.

| Starship service, percent of one core | Before | After |
| --- | ---: | ---: |
| RLCD including child processes | 8.73% | 0.71% |
| Observer collector | 2.74% | 2.04% |
| Original full publisher | 4.69% | 0.00% |
| New active publisher | absent | 0.29% |
| Monitored sum | 16.16% | 3.05% |

Snap's monitored collector/full/active units total 1.23% before and 0.99% after;
its unused local publisher units consume no measurable CPU in these windows.
Starship RLCD main-process PSS ranges from 43.5–44.5 MiB before to 23.1 MiB after;
FD counts are 11–14 before and 11 after.

These are descriptive observations with uncontrolled native activity, scheduling
and CPU frequency. Lower live collector CPU does not reverse the controlled
producer extra-work result. Snap's SSH stdio bridge/server crypto and native
provider CPU are outside its managed-unit sum. USB is absent in both windows;
this is feed-processing/service evidence rather than physical device cadence.
Physical ACK, readability, reconnect and reboot remain deferred. The service
continues its bounded missing-device retry policy.
