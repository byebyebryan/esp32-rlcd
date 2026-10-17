# G1 transport-only relay amendment

Status: **A1 contract closed; dependent relay G1 implementation authorized**,
2026-10-17 UTC, revision 3. Mesh, Observer and RLCD accept the exact revision-4
interface recorded below. This closes amendment A1 to acquisition roles under
Bryan's existing execution authorization. Runtime and installed qualification,
consumer adoption and service selection retain their later gates. Frozen G0
bytes stay unchanged.

## Reason and scope

The accepted Mesh `ed771e5` proposal requires a publisher-owned admitted cache
and independent matching of a fresh head to that material. Omitting this
admission is an amendment, not an existing G0 implementation option.

Mesh reports roughly 2.19 seconds CPU for source cold admission at 500 rows.
Repeating that work in a fresh SSH publisher and Reader could threaten the
15-second acquisition budget at 2,000 rows. This is prototype evidence and
extrapolation, not measured full-pipeline capacity or acceptance.

A1 permits a separate transport-only relay: bounded unadmitted material
forwarding plus a fresh source-bound owner-head witness. The authority-receiving
Reader independently admits material and proof. Existing material publishers
retain their full admission contract.

## Role boundary

| Role | Responsibility |
| --- | --- |
| Native owner | Accepted generation, committed native tables/root/cursor, original evidence and fresh head after nonce |
| Transport-only relay | Authenticated source connection, bounded structural/envelope checks, exact bytes/chain forwarding, configured source wrapper and bounded fresh-head/lease checks |
| Reader | All body/schema/domain and cross-record checks, expected-old tokens, table/cohort/native/source roots, atomic indexes, nonce/liveness/clock/receipt/RTT proof checks and authority publication |
| Material publisher | G0 independent material admission whenever it exposes semantic/admitted views or capabilities |

The relay is an explicit trusted-factory/declared-role choice on the new sync
family. Mesh's accepted R4 specifies its API and negotiation contract. There is
no silent bypass inside a material publisher, SDK 1 or Delivery 1, and no
wire-supplied imports, commands or source selection.

Relay checks bind expected UID/socket/service, host, descriptor, full/active
selector, native owner/context, configured source/profile, route and request/
channel/reader epochs. Transport structure checks do not claim full native or
domain admission. The relay exposes no ViewRef, AdmittedCommit, material-admission
reuse capability, semantic queries or authority-bearing profile hooks. Forwarded
material and tags remain unadmitted at the receiving boundary.

Opaque byte-ownership handles may reserve, seal and transfer exact unadmitted
input under the shared budgets. Such a handle cannot carry trusted material or
profile decisions, skip receiver admission, mint a semantic view or rebind a
retired request. R4 uses separately minted `RelayInputOwner`,
`RelayInputReservation` and `RelayInputRef` types with the common structural
source protocol. Cache input and relay consumers reject each other's handles.
Sealing bytes does not validate them. Exact binding, transfer and cleanup are
part of the accepted interface.

The Reader independently checks all material and roots. A matching relay claim,
owner root or hash cannot substitute for admission. Original support, order,
uncertainty, removal, field expiry and presentation semantics remain unchanged.

## Proof, forwarding and bounds

Every nonce proof invokes the live native owner's bounded head operation after
nonce admission. Cached replies and pipe liveness are insufficient. The relay
wraps that exact target and configured source; the Reader matches the native/
source roots and complete original receipt/cohort heads to its admitted state.
Lease attenuation cannot renew original evidence. Keep original clock, UID/
incarnation, full RTT and margin checks.

A known moved head/source failure revokes affected Reader authority. No catch-up
occurs inside the two-second proof. Separate catch-up, one retry and recovery
remain inside the absolute 15-second acquisition budget. Never prove a retained
old target instead of the fresh head.

Forward exact bounded native baselines/transactions or signal gap/baseline-
required. The relay does not semantically compose, repair or relabel unadmitted
updates or silently drop required chain elements. Specify cursor/sequence,
duplicate, descriptor/scope and overflow handling. Late/cancelled work cannot
publish; source/watch/alias close retains the accepted bounded ownership rules.

Raw material, journal, output, staging and pins retain the same encoded/heap/
service caps and client/credit limits. Calling a buffer transport does not move
it outside accounting. This role grants no additional deadlines or capacity.

## Accepted A1 contract

| Evidence | Accepted revision |
| --- | --- |
| Mesh standalone interface and agreement | `7d7b09c97f7487662911968abb8a88ca7b7f9469`, `mesh-plus/docs/delta-sync-relay-api-r4.md`, 47,213 bytes, SHA-256 `5377d3a52c9e20bc839a1ecc135199b3103786f71b3e6e73a3e61a283dad7e5e` |
| Mesh review manifest | Same commit, `docs/evidence/2026-10-16-delta-sync/relay-api-r4-review.json`, SHA-256 `214d4e5a906c68e0060d5077f86d04eda1a10f92f8734edac46aef55987cb5fe` |
| Observer owning signoff | `ccf6577d81b45ce9e400ebf0881ad71383339f27`, `agent-observer-active-feed/docs/delta-sync-relay-r4-review.md`, SHA-256 `18569529522c5c65edcdffc4d5a448e4372d33255dcf13726b014257d3da155e` |
| Observer agreement evidence | Same commit, `docs/evidence/2026-10-16-delta-sync-source/relay-r4-agreement.json`, SHA-256 `7f9e2568d4a70fcdf866fcd0c3f8c5ba222895f8a787832df7de69a1a22acba7` |
| Original coordinator role boundary | Revision 2 at `665f6caaed99740a755de9467c7ae53322f7e720`, this document's SHA-256 `6eaa408376f91bb7c5e4276812927fd2bfce2445412fb02a211bea22a5e52aef` |

RLCD verified those committed bytes, the producer agreement and prior input
pins. Observer explicitly accepts the source/ref/scanner, native identity and
complete context, head/clock, lifecycle and ownership contract with no remaining
owning conflict. This record is the coordinator's joint A1 closure. The original
role decision and immutable R2/R3 packets remain provenance; R4 is the single
accepted interface for dependent implementation. Changed accepted semantics need
an identified amendment and joint review.

R4 completes public `HeaderRef.materialization_bytes` and `materialize()` with
retirement checks and independently prepaid detached copies. It also fixes the
nine-field request binding, authenticated factory-minted bridge identity and
nonrenewable acquisition capsules separate from long-lived watches. Scope close
revokes use before awaited cleanup; live input/output pins, ticket metadata and
surviving copies stay charged until physical retirement. Shared 32 MiB encoded
and 64 MiB heap caps and original Reader deadlines remain binding.

The retained arithmetic oracle and fixtures are unchanged: prior independent
12 positive/four rejection checks on Python 3.14/3.11 remain arithmetic evidence.
Their toy JSON-fragment preservation does not qualify native line framing.
No runtime tests or implementation are implied by this contract closure.

## Completion transfer agreement

The additive source completion seam is agreed within the existing G1 scope.
Observer's owning review at `132c0f109784ac849fa1d03d254118669224485a`,
`docs/delta-sync-completion-transfer-r1-review.md`, SHA-256
`bdd6e13402c44a6c5c58051ecf12a92658230138adec40a25f317f6166733d93`,
accepts the method, result name and lifetime contract. Mesh's reconciliation at
`332e33ff27ee1dfa6c53faf970429c34fe08d46d`,
`docs/delta-sync-completion-transfer-r2.md`, 4,699 bytes, SHA-256
`c1aa8a8ad8e449b5b6d68fadc839e57377237d26ba9bb5a035f0571945484706`,
adopts its sole native-versus-outer control-bound clarification. The Mesh
evidence manifest is `completion-transfer-review-r2.json`, SHA-256
`d9ce6d34a708c81287b1a448dc06ac20e2fff26cef8a01e9ee39450704aedd49`.
The original R1 packet stays unchanged; this agreement reopens neither A1 nor
compact R2 and needs no additional general execution permission.

Optional `changes_with_completion(...)` returns a source-owned
`CompletedChanges` with transactions and completion, or an explicit control. Legacy
`changes()` keeps its transaction-only tuple/control surface. Completion carries
the exact original native bytes and correlates status, base/target, terminal tag,
cursor and chain epoch. Generic relay preflight checks the entire result before
output and drains material before completion; EOF, watch liveness or a
synthesized control cannot substitute for native completion.

Both existing bounds apply: Agent native control is at most 16,384 bytes;
the complete nested Mesh control, including its envelope and LF, is at most
65,536 bytes. Batch/control/header metadata, copies, live pins and late results
remain prepaid until physical retirement under the shared caps and original
deadline. Closing a result affects its own resources and preserves siblings.

RLCD verified the exact agreement inputs, all 200 captured Observer files against
the declared immutable commit, and unchanged original packet/probe bytes. Both
producer output files exactly match RLCD's prior twelve-case Python 3.14/3.11
replay: native 16,384 accepted, 16,385 and 65,536 rejected, final fixture credit
zero. This is synthetic lexical-bound evidence. Actual source method, relay
consumption, controller grammar, cancellation/close execution and aggregate
qualification remain implementation work.

## Generic completion consumer checkpoint

Mesh implements the generic consumer at
`b57c2176d60a8593fa2f85d7322655384a3227b6`. Its guide,
`docs/delta-sync-completion-g1.md`, is 3,837 bytes, SHA-256
`c4549565ff89efc031ed29f82db4a133b0c57a965d5e880c2d46a4c3026d59eb`.
Setup requires the optional completion-bearing source method and rejects a
legacy-only source. The consumer preflights all material, terminal metadata and
outer envelopes before output, retains pins and separately owned metadata, and
drains material before forwarding the exact original completion bytes.

RLCD verified 187 immutable Mesh input pins and six protected paths, then ran
all 27 focused relay fixture tests on Python 3.14.8 and 3.11.17 with cyclic GC
disabled. All pass with five final allocation counters zero. Additional probes
confirm that an oversized completed result and a malformed five-ref tuple emit
no delivery prefix, retire their own session/refs, preserve a sibling channel
and retain 1,024 bytes of unsealed receive credit until physical cleanup. This
closes the bounded malformed-batch cleanup finding at source.

The separate head-deadline refinement remains open on this runtime. The original
clock probe still attempts a prefix write at 2,101 ms after a two-second head
budget; the outer operation rejects and emits zero complete proof frames.
This establishes no Reader authority bypass. The original nonrenewable deadline
must also hold before writes.

Completion tests use a fixture source and codec. Actual Observer source/result
ownership, joined native IPC/Reader and fixed-SSH completion coverage remain
unqualified. Earlier actual-source baseline/head evidence stays bound to its
older runtime. The broad core gate was still running at the producer handoff;
this checkpoint records the independent focused source review only. No installed
pair, route, resource or performance acceptance follows.

## Implementation and qualification

Mesh may implement the agreed generic relay/controller and byte ownership;
Observer may implement its Mesh-free source/structural scanner and HeaderRef
facade through the accepted R4 public interfaces. Compact normalization/encoding
agreement, IDs/schema freeze, producer resource and performance acceptance, and
later consumer gates remain separate.

The Observer watch-close fix at `4254a97` is independently verified source
prerequisite evidence. Mesh's input-owner authority fix at `e9f07c3` and
callback material-credit fix at `66b9c1e` also pass their bounded regressions.
The revoked graph stays charged through callback/confirmation unwind and
retires outside the nonce operation. These source prerequisites do not grant
aggregate resource, runtime or producer acceptance under A1.

Tests must show Reader rejection of corrupt and self-consistent-but-domain-
invalid material, wrong roots/receipts/bindings, replay and owner/clock changes;
moved heads during cold admission; gaps/overflow/duplicate conflicts and
cancellation; and absence of relay semantic/admission capabilities. Keep full
material-publisher and old-route tests.

Measure real 100/500/2,000-row cold/recovery and steady full/active acquisition,
including startup, native IPC, fixed SSH, Reader admission and proof. The
15-second absolute/two-second proof budgets and cold/regression, end-to-end
CPU/byte/memory gates remain unchanged. Reader admission alone may still need
optimization. Exact installed paired artifacts and independent native/transport/
resource/performance and scoped rollback acceptance remain required by the
[execution plan](delta-sync-plan.md).
