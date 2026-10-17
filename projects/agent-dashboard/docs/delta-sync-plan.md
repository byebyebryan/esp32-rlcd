# Incremental state synchronization plan

Status: **G0 and A1 contracts closed, G1 implementation authorized**,
2026-10-17 UTC. Bryan authorized execution across the existing Mesh Plus,
Agent Observer and RLCD
owners. This thread has reviewed the final contract and records joint G0
closure below. Producer implementation and independent qualification may proceed
without another general go-ahead. Consumer adoption and normal service selection
remain behind their later acceptance gates.

## Producer-reported dark status and scoped handoff

On 2026-10-17, the Mesh owner closed its delta-sync write/qualification scope
and retained the feature dark and gated. Its local wrap commit is
`bea028964f5c1f89c6527fcd9f04e4d634c00d7b`, on `mesh-delta-sync-20261016`;
no upstream push is planned or performed by RLCD. Runtime remains
`03a681f95a609b20eaa20134f7241d3d14d441a6`, with prior evidence
`d483351d302bdc090f62bcaa18029788b7ec75be` byte-preserved. No packed-control
candidate was implemented. The previous G1 authorization is not an instruction
to restart an owning task that has closed its scope.

Mesh's `docs/delta-sync-dark-status.md` is 7,979 bytes, SHA-256
`0f237d975a9a3c300cd3688646d6c4a76317b81205bca8aa58771767fc0a7950`.
Its `docs/evidence/2026-10-17-delta-sync-wrap/receipt.json` has SHA-256
`a70159d37a7712a9050442404718f0efc0d89a4f0adec5e4c92a4e5d031734f1`.
RLCD verifies the docs/evidence-only diff, clean local readback, no pending Git
markers, 1,709 preserved tracked files, 18 refs, 229 ancestor commits, two
retained wheels and two external cache-only review pins. The saved 411-test
wrap gate is read/hash-checked, not rerun or promoted to qualification. Mesh
reports no future owned children, jobs or Git operations; its watcher audit
is cached and makes no fresh global scheduler guarantee.

Mesh releases only its own temporary attribution hold for cleanup coordination
in `/home/bryan/code/mesh-plus`. This grants no permission to rewrite/prune
pinned lineage, refs, artifacts, `dist/` or referenced `.cache/` contents.
`mesh-plus-idle-profile-20261014` at `c7b1d475` and
`mesh-plus-system-dashboard` at `fe7e700d` remain outside that clearance.
No cleanup is performed by this review.

Observer's own deferred/default-off wrap is
`79d07f40d177fe5f0c5a6d86a74511d02d2548b0`, descending from evidence
`51b0f27559b2b1553ffb60d04992ba90e639d873`. Source inspection verifies that
`Runtime.experimental_sync` defaults to the exact boolean `False` and rejects
full/active sync before owner/cache access. No ordinary CLI enablement is added;
disposable sync fixtures opt in explicitly. This guard is a new source change,
not a reassignment of earlier pipeline or performance acceptance. Its 6,320-byte
`docs/delta-sync-dark-feature.md` has SHA-256
`47d8a4795ddeab9d655bfffdca5ca4a50dc29ded1b51ec6c2d065a84207b811e`.
The owning 949-test/66-focused-per-Python wrap results are read/hash-checked,
not rerun or promoted to producer qualification.

Observer's external clearance is
`/home/bryan/.cache/agent-observer-delta-sync-wrap-20261017/git-clearance.json`,
SHA-256 `71e821454397fcd78434d4ca84a875412acf8426db21e2ac1eb446782218c27d`.
RLCD verifies its pinned sidecars, all 18 snapshot refs in the Git bundle,
bundle integrity and the exact `af2bc7bf`/`b6ce8428`/`51b0f275`/wrap ancestry.
The cache archive matches all 57,645 inventoried files, 681,480,296 uncompressed
bytes and four preserved symlink records, without extraction or modification.
Retain the entire external recovery directory and the cache or its verified
archive. Observer reports no pending children, Git operations or automatic
continuation and releases only its own existing cleanup scope. Other Observer
worktrees, published objects/artifacts and sibling owners remain excluded.

This records producer state and scoped handoff facts. It does not complete
G1/G2, grant acceptance, release RLCD's attribution HOLD or release another
owner's hold. Closed contracts and source findings remain closed; CPU,
2,000-row capacity/recovery and all other failed/open gates remain so.
Selected a7/a23, ordinary full/material/Tmux/349/writer/provider workflows,
concurrent work, rollback pins and deferred physical checks are preserved.

## Accepted G0 contract

| Evidence | Accepted revision |
| --- | --- |
| Mesh proposal and appendix | `ed771e5c8843dca718700c8b8b1d6804ae9134f0`, branch `mesh-delta-sync-20261016` |
| Exact appendix | `mesh-plus/docs/delta-sync-contract-appendix.md`, 28,802 bytes, SHA-256 `a376bc848a78027d4fd723e8a2959dbbc4e00114da132d3a5d2733a6ebce2eb6` |
| Observer domain/API acceptance | `agent-observer-active-feed/docs/delta-sync-proposal.md`, SHA-256 `2f61b17db957f6cc7166f115fafcc105ec41ee651c3747a17cb6d8ea42486f31`, explicitly accepts that appendix |
| Independent stdlib arithmetic script | SHA-256 `67a29dabb4abff4d945d257edf4d1be30e87b7b804817323a77da79041c47d54` |
| Arithmetic results | SHA-256 `2e3efc5fa5cafe4ff4064300f8bb0d34af46115fc55e8ce6fd572a296e495792`; 20 hash vectors, canonical Unicode/escape and rejection checks, 720 insertion permutations pass |

Mesh's committed contract and current owner confirmation identify the same
revision accepted explicitly by Observer. RLCD verified the commit/file binding,
clean Mesh checkout, evidence hashes and scoped results, and reviewed the
contract changes. All four review issues are resolved: stable logical cohort
keys, explicit cleanup ownership, original provider/namespace context binding
and the existing `hostScope`/`nativeIdKind` identity names.

Exact documents and review records are captured privately under
`.cache/delta-sync-integration/20261016T192225Z/`. Observer's arithmetic evidence
is under its `.cache/delta-sync-g0/<appendix-sha256>/`. This is design and
arithmetic acceptance, not schema, runtime, installed-package, native, performance
or deployment acceptance. Changed accepted semantics require an identified
amendment and joint review. G1 fills in negotiated schema/API allocation and
qualification details required by the accepted appendix.

## Goal and preserved baseline

Make repeated full-inventory reads cheap when almost all records are unchanged.
Retain the active projection as a separate scope choice. Both full and active
consumers should reuse admitted unchanged bodies without transferring, decoding
and validating them on every read.

The [active-feed receipt](../../../docs/evidence/2026-10-16-active-feed/REPORT.md)
establishes the current a7/a23 baseline and its limits. Published Mesh source is
`7c30fc9`, runtime `1978805`; Observer source is `412e6ff`, runtime `7807160`;
RLCD source is `2127745`, runtime `7033725`. Preserve this deployed tuple, full
diagnostic routes, Tmux, 349, writer and ordinary provider workflows until the
appropriate acceptance gate passes. Physical RLCD checks remain deferred.

Current protocols carry complete replacements and correlated full proofs.
The [active-feed plan](active-feed-plan.md) deferred deltas and digest-only proof.
Reserved syntax does not establish capability. The new sync family is explicit
and negotiated; frozen old schemas, lock inputs, SDK 1 and Delivery 1 routes
retain their contracts. An unsupported new route fails without a legacy retry.

The [transport-only relay amendment](delta-sync-relay-addendum.md) records joint
A1 closure on exact Mesh R4 `7d7b09c` and Observer signoff `ccf6577d`. Its agreed
dependent relay implementation may proceed under the existing G1 authorization.
G0 material publishers retain their admission contract. Reader authority checks,
bounds, deadlines and later acceptance gates remain unchanged.

## Ownership and execution gates

| Owner | Authorized work |
| --- | --- |
| Mesh Plus | Generic sync delivery, owned reconstruction/cache, commitments, proof, ordering/gap/resync, public staging/query APIs, bounded transport and reviewed new lock inputs |
| Agent Observer | Actual body/observation/support changes, coverage/removal/uncertainty, Mesh-free owner cache and incremental local IPC, pure source/profile/codec/read facade and factory integration |
| RLCD | Joint decisions and reference fixtures, matched baseline/acceptance preparation, later supported consumer integration, operational selection, fleet evidence and paired rollback |

Each producer edits only its repository on an isolated branch. Owners are not
alone in the codebase: preserve concurrent edits and existing artifacts and
accommodate other owners' agreed changes. Commit accepted planning documents in
the owning branch before runtime work. Reconcile fresh artifact allocations
before building; never overwrite a retained artifact or reuse its version.

| Gate | Outcome |
| --- | --- |
| G0, complete | Exact contract and domain/API review, independent arithmetic, semantics, bounds and numerical requirements accepted as recorded above |
| G1, authorized | Freeze new negotiated schema/API identifiers and vectors; Mesh and Observer implement their owning layers and agree concrete interfaces before dependent changes |
| G2 | Independently qualify immutable artifacts, installed correctness/resources/performance, old-route compatibility and the exact paired producer tuple |
| G3 | RLCD adopts supported accepted APIs and proves same-scope full/active semantics and matched end-to-end performance |
| G4 | Scoped service selection, real configured fleet, resource windows and paired rollback; physical checks stay explicitly deferred |

Acknowledgement, source tests and prototypes do not establish readiness. Return
exact source/evidence revisions, immutable wheel hashes/dependencies,
descriptors, public APIs, installed gates, exclusions and cleanup evidence.
Publication follows review and exact acceptance. Producers do not select normal
roles, roll out sibling services or take provider/session/device actions.

The [G1 density review](delta-sync-density-review.md) permits private packed
storage work under the existing caps and public interfaces. It separates that
work from source/input resource qualification. The [compact normalization
agreement](delta-sync-codec-agreement.md) records joint Mesh R2 `b9dd8c6` and
Observer `8a075bc7` acceptance; dependent shared implementation may proceed.
A1 and the normalization interface are agreed. Actual compact schema/encoding
freeze, their implementations and the failed dense resource/CPU gates remain open.

The bounded ownership prerequisites are independently verified at source:
Observer watch-close revocation `4254a97`, Mesh input-owner authority revocation
`e9f07c3`, and Mesh callback material-credit retirement `66b9c1e`. The latter
keeps the revoked graph charged in its existing stage slot through confirmation
and owned-input unwind, then retires it during material work or owning cleanup.
The original probe and four targeted regressions pass on Python 3.14/3.11 with
cyclic GC disabled. Mesh evidence is `b230f98`,
`docs/evidence/2026-10-16-delta-sync/head-retirement.json`, SHA-256
`29093c01c6a9b19b3248b93a4b876878e1025b939debd014cb6b466150250172`.
These close the specific source findings; aggregate lifetime/resources, actual
compact execution and all producer acceptance gates remain open.

## Accepted architecture and authority

Cover the entire path:

`Observer engine/cache -> local service IPC -> publisher -> Mesh transport -> Reader/admitted cache -> Observer facade -> consumer`

The owner publishes a complete baseline followed by atomic typed keyed changes.
Generation/diff/cache work happens once per admitted owner generation and is
shared across subscribers. Native census/generation may retain O(N) work; count
it. Repeated reads and sparse updates must not hide full acquisition, decode,
admission, hashing, restoration or export at any boundary. Baselines, explicit
full exports and recovery may cost O(N).

The eight committed spaces separate records, stable bodies, exact observation
facets, memberships, original receipts, cohort heads, scope facts and metadata.
Observer's exact nine field-token extractions and moved-path table are accepted.
Preserve timestamps, optional/null shape, errors, reasons, coverage and committed
API 4/active age anchors. Do not infer a common sample time. Roster-sized scope
decisions are keyed facts, not arrays replaced on each sparse change.

The Mesh-free native root binds native contract/schema, `hostScope`/UID,
view/selector, owner incarnation, clock, complete original provider/namespace
contexts and projection continuity, including empty/unavailable scopes. The
O(1) Mesh wrapper binds its exact native root/cursor to the configured
authenticated host, source alias and profile/contract. Nonce, routes, catalog/
host order and channel/reader epochs remain bound separately. Aliases may share
a socket and immutable bytes; authority tokens remain distinct.

Use the appendix's exact canonical JSON, length framing and domain-separated
SHA-256 compressed binary Patricia commitments. Receivers independently compute
changed paths, roots and counts. No XOR, insertion-order root or full sort/rehash
implements sparse updates. Reject different original keys with equal key hashes.
Only owned, admitted bytes may be reused.

Membership keys use identity, current record birth, stable logical cohort ID
and field. Removing/reinserting an identity creates a new birth. A cohort seal
is an immutable `(generation, memberRoot, count)` version under its stable ID;
changing one binding does not rekey unchanged members. A renewed head asserts
actual reobservation of that exact validated set. A newer same-key receipt
cannot renew retained fields. Old refs stay informational. G1 must prove sparse
key/visit counts, including no hidden N-cell observation-ref rewrite.

Admission stages immutable generic state and a frozen domain-index patch and
publishes both atomically after all checks. Callbacks use supported metered
lookups/indexes, not private Mesh state or full SDK 1 restore adapters. Failed
validation, mutation, cancellation or callback replacement publishes no partial
candidate. Headers contain bounded roots/status; enumeration/export is explicit
and counted. A body lookup grants no currentness.

Atomicity is per host/source view. Aggregates bind ordered host selection,
catalog/routes and per-host confirmed tags/statuses. A staged host cannot appear
confirmed; other hosts retain only their own checked original leases. Full
exports keep `(runtime.value != "running", five-part identity)` order. Active
exports keep original scope order then identity within scope; other bounded
arrays keep original order. Use an index without renumbering N rows.

## Fresh proof, removal and cleanup

The two-second remote proof contains only a fresh owner head after nonce
admission and independent root/receipt/request checks, including original RTT
and margin rules. It does not call full frame/export/expire/publish/collection.
Material failure/health/context changes are committed; time only attenuates the
original leases. Head emission cannot fabricate a fresh legacy Service 4 frame.

A known moved head revokes that host's current authority. Catch up separately
with at most four transactions/8 MiB, then obtain a new nonce proof, all within
the original absolute 15-second acquisition budget. Allow one moved-head retry.
Further movement, eviction, quota or deadline exhaustion produces explicit sync
baseline recovery/failure inside that same budget. Never prove retained old
state instead, silently use a legacy route or retry without bound.

Keep positive facts, negative/completeness authority and external presentation
context separate. Per-field expiry remains independent. Transport removal,
expiry, pruning, missed negatives, overflow, disconnect and partial omission
do not assert parked or retire UI context. Complete-empty needs current scope
support. Preserve a7 full/active identity, kind, error and uncertainty semantics;
add no timeout, reconciliation query or event-replay guarantee.

Public source/watch/publisher/reader/stream close is bounded and idempotent.
Each closes its owned requests, tasks, subscriptions, reservations and sockets;
late work checks retirement. Repeated cancellation cannot detach cleanup.
Source close never stops the shared native service. Externally owned shared
source clients remain the external owner's obligation; closing one alias must
leave another alias usable. Disconnect revokes handles/stages immediately.

## Hard bounds

| Resource | Accepted bound |
| --- | --- |
| Records | Existing 4,096 native ceiling; active recent-member ledger 4,096 / 1 MiB |
| Serialized state / wire message / aggregate | Existing 8,404,992 / 8,470,528 bytes / 16 MiB; factorization overhead counts |
| Original receipt/cohort heads | At most 32 each; no historical current-receipt bank |
| Decoded retention | Current plus predecessor roots and one staged candidate; revocable handles cannot pin old graphs |
| Encoded journal | At most four generations and 8 MiB; first exhausted cap wins |
| Encoded ownership | 32 MiB unique sync bodies/stages/journal/pins across full/active/all peers inside unchanged 64 MiB service encoding budget |
| Decoded ownership | 64 MiB across owner full/active caches/indexes/stages/pins; independent publisher/Reader caps include Python allocations; Reader shares its cap across selected hosts |
| Head | Native <=49,152 bytes plus Mesh envelope <=16,384, complete sum <=65,536; entry/fixed limits include punctuation |
| Concurrency | Existing 16 local clients total across old/full/active/sync; channel eight subscriptions/eight outstanding requests; bounded slow-peer state |
| Existing timing | Setup/acquisition 15 s, remote proof 2 s, heartbeat <=5 s, blocked-credit end <=15 s; monitoring/catalog cadence and budgets unchanged |

Reserve/account allocations on creation and reclamation, not whole-cache size
walks. Share immutable allocations once; count independent processes in aggregate
memory. Bound detached exports separately. Slow peers get gap/resync before
forcing history retention. G1 freeze includes exact joined-row, field-token/
cohort-renewal, transaction and maximum-head vectors independently executed by
both owners. Preserve frozen old schema/lock bytes.

Retained canonical key/value buffers count toward the single 32 MiB encoded
cache/stage/journal/pin budget even when they are the logical map's only internal
representation. They also count toward the 64 MiB heap/allocation cap. These
overlapping caps do not imply extra copies: a physically shared buffer is charged
once within each cap; a separately copied output or stage is another allocation.
An output-only encoded ledger does not establish compliance. Report unique
internal canonical, output, stage and pin storage and their sharing at complete
full/active current/predecessor/staged peaks. This clarifies the accepted G0
encoded-cache ownership rule without changing frozen contract bytes or caps.

## Matched performance and correctness acceptance

Compare a7/a23 replacements with the same full scope, then the same active scope.
Earlier full-versus-active savings are not the delta baseline. Use 100/500/2,000
rows, at least six generations, unchanged/cohort-only renewal, one/1% stable-body
updates, real N-row timestamp refresh, all-body change, cold/recovery/gap and
slow-reader cases. Count real N changed observations as K=N. The primary value
case is one subscriber/four reads per generation; report one-read amortization
separately and 4/16-subscriber sharing/capacity cases.

| Acceptance dimension | Required result |
| --- | --- |
| Full four-read CPU, 500/2,000 | >=50% lower total generation-through-consumer CPU for unchanged/cohort-only, one/1% body updates and real N-row timestamp refresh |
| Native timestamp-refresh bytes | >=50% fewer total application bytes at each local-service and Mesh boundary, including cold baseline over >=6 generations |
| Steady bytes | >=90% fewer cohort-only and >=75% fewer sparse-body application bytes at each boundary |
| Incremental sync CPU | Producer target >=70% lower publisher/Reader/facade/owned-descendant CPU for full unchanged/sparse cases |
| Generation/diff overhead | Target <=10% above matched a7; hard promotion ceiling <=25%, included in total CPU gate |
| Cold, all stable bodies changed, forced recovery | CPU and bytes regress <=25% within unchanged deadlines; allowance excludes the timestamp-refresh value case |
| Small active scopes | Total CPU regression <=max(10% baseline, 5 ms/generation) |
| Compact unchanged head | <=2 ms median service/source CPU and <=8 KiB for native <=4 receipts; 2,000-row cost <=2x 100-row cost at equal receipt count |
| Sparse latency | Visibility p95 <=matched baseline +10 ms |
| Memory | Aggregate peak RSS at 2,000 <=1.5x matched baseline +16 MiB, hard internal caps, stable reclamation and no leaks |
| Repeated unchanged bodies | No decode/schema/hash/materialization after baseline except explicit counted exports/oracle |
| Semantics | Equal complete facts, ordered identities, support, coverage, original leases and uncertainty; no silent fallback or partial publication |

Producer overhead compares matched old and new total owner-generation CPU;
the new total includes retained common work and all additional sync publication
work. Report those components and the combined total separately. Comparing one
new stage against the whole old generation cannot establish the overhead gate.

Use serial installed-artifact ABBA under the shared advisory lock, real local
IPC and disposable fixed SSH. Qualify WSS independently if exposed. Include
generation/diff/hash/cache, local IPC, publisher, both measured SSH endpoints,
admission/facade/application and owned descendants. Include semantic-oracle
hashing in totals with its separate cost. Report absolute CPU, all baseline/
delta/proof/control bytes, latency, memory/indexes and FD/task cleanup. Do not
add unrelated percentages, exclude expensive boundaries, slow native collection
or relax deadlines. Capacity failure is a disclosed limit, not equal-work savings.

Correctness cases include complete/partial/complete-empty, changes beyond USB32,
independent runtime/history expiry, retained old same-key support, wrong base/
result/count, duplicate/conflicting keys, reordered/gapped updates, malformed
facets/refs, clock/owner/context/selector changes, mutation, cancellation, failed
callbacks, oversize/recovery and cleanup/shared-alias isolation. Existing full
and Tmux routes retain compatibility. Failed gates return to review; source or
prototype results cannot substitute for exact installed acceptance.

## RLCD fixture preparation

The read-only baseline fingerprint is retained under
`.cache/delta-sync-integration/20261016T192225Z/baseline.json`. Reproducible
reference seeds and their manifest are now prepared in that directory's
`reference-fixtures/`, using the selected a7/a23 interpreter and existing client
fixtures. Full inputs contain 100/500/2,000 records; each paired active input has
three selected bodies derived from the same exact original receipts. Full order,
identity uniqueness, subset membership and old-profile admission were checked.

These are synthetic committed input seeds and a workload matrix, not native,
currentness, transport, capacity or performance evidence. Stored monotonic
receipts grant no live authority. Workload transitions and the new sync adapter
await supported qualified producer APIs; matched timing must still include
generation and every transport/validation boundary.
