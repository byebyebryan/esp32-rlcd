# G1 transport-only relay amendment

Status: **coordinator supports the design; joint producer agreement pending**,
2026-10-16, revision 2. This is amendment A1 to accepted acquisition roles. Exact Mesh/
Observer agreement is required before dependent relay transport implementation.
Other authorized G1 work continues. Frozen G0 bytes stay unchanged.

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
family. Mesh supplies its exact API and negotiation contract. There is no silent
bypass inside a material publisher, SDK 1 or Delivery 1, and no wire-supplied
imports, commands or source selection.

Relay checks bind expected UID/socket/service, host, descriptor, full/active
selector, native owner/context, configured source/profile, route and request/
channel/reader epochs. Transport structure checks do not claim full native or
domain admission. The relay exposes no ViewRef, AdmittedCommit, material-admission
reuse capability, semantic queries or authority-bearing profile hooks. Forwarded
material and tags remain unadmitted at the receiving boundary.

Opaque byte-ownership handles may reserve, seal and transfer exact unadmitted
input under the shared budgets. Such a handle cannot carry trusted material or
profile decisions, skip receiver admission, mint a semantic view or rebind a
retired request. If the public API uses the name `OwnedInputRef` for this handle,
its contract must explicitly mean byte ownership only and distinguish it from
any admission-reuse capability. Sealing bytes does not validate them. Exact
handle binding, transfer and cleanup remain part of the joint public API review.

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

## Agreement and qualification

Mesh returns the exact factory/role declaration, source-ticket interface, proof
envelope and check responsibilities. Observer confirms native acquisition/head/
identity/context compatibility. Both agree the same addendum/interfaces; RLCD
then records A1 acceptance. This draft grants no consumer adoption or rollout.

Revision 2 replaces the earlier name-based `OwnedInputRef` exclusion with the
capability boundary above. It reconciles the pending owned-input accounting API
without accepting that API or changing frozen G0 bytes, caps or proof rules.

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
