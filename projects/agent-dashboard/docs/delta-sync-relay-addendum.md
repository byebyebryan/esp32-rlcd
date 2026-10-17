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

## Implementation and qualification

Mesh may implement the agreed generic relay/controller and byte ownership;
Observer may implement its Mesh-free source/structural scanner and HeaderRef
facade through the accepted R4 public interfaces. Compact normalization/encoding
agreement, IDs/schema freeze, producer resource and performance acceptance, and
later consumer gates remain separate.

The Observer watch-close fix at `4254a97` is independently verified source
prerequisite evidence. Mesh's input-owner authority fix at `e9f07c3` also passes
the bounded authority regression, but reentrant callback material lifetime and
accounting remain an open implementation finding. A1 closure does not accept
those implementations or relax their physical-retirement requirements.

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
