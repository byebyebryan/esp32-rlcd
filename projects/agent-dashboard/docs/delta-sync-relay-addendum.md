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

The separate head-deadline refinement remained open on this runtime. The original
clock probe still attempts a prefix write at 2,101 ms after a two-second head
budget; the outer operation rejects and emits zero complete proof frames.
This establishes no Reader authority bypass. The original nonrenewable deadline
must also hold before writes.

Completion tests use a fixture source and codec. Actual Observer source/result
ownership, joined native IPC/Reader and fixed-SSH completion coverage remain
unqualified. Earlier actual-source baseline/head evidence stays bound to its
older runtime. The broad core gate was still running at the initial
`b57c2176` handoff;
this checkpoint records the independent focused source review only. No installed
pair, route, resource or performance acceptance follows.

Mesh follow-up `be6470edab0ae7d67063fd08b61a8019c2093e35` removes a
redundant `nativeBindingDigest` requirement from native completion controls;
their existing typed tag already carries that binding. RLCD reproduced six
full/active zero/one/four-transaction cases on each Python version with the
actual Agent structural codec and fixture batches: `b57c2176` rejects the valid
controls, while the correction accepts them and preserves the original bytes.
The 27 relay tests also pass on the corrected runtime. This is structural codec
composition, with fabricated fixture roots, rather than actual owned-source
completion or semantic Reader acceptance.

The finalized evidence commit is `171f21c60697d2671d1db602f991435379819306`:
`docs/evidence/2026-10-16-delta-sync/completion-g1-review.json`, SHA-256
`17b87a121c2c590a2b4c60e4b8f65f4bfdd54ba3b2a92a1a0a3216cc90dd4509`.
Its updated guide has SHA-256
`4685c4df82c353b05460b357c18cf01ecb94f78266881d59a085f0e97839e134`.
RLCD verified 187 Mesh and 211 Observer inputs against the immutable commits and
its existing private exports, eight protected paths and nine committed logs.
The producer's canonical run passes 342 tests with zero skips, plus its existing
design/delivery/lock/schema and lint gates. RLCD verified that log and retained
its prior independent focused runs rather than rerunning the unchanged suite.
Both native-codec composition and source-pin diagnostic outputs exactly match
the prior dual-version root replay. The latter remains an expected reproduction
of an open revocation gap, not passing source-lifetime qualification.

## Actual completion source and relay composition

Observer implements the agreed optional method at
`2f697d468eb3b0cb895276fd07cb746acbd23d37`. Its guide
`docs/delta-sync-completed-changes.md` has SHA-256
`59b671dd0ac8ec02df35c230afd1e51e912ecddf37aa043f146074f4fd313c51`;
`docs/evidence/2026-10-16-delta-sync-source/completed-changes.json` is 46,894 bytes,
SHA-256 `5b9a8b7f7385ba78a4cfd05af59cbf003802a902f46d0abc5f8890e308f71138`.
The source-minted `CompletedChanges` retains original transaction refs and its
original completion ticket, with a separate prepaid 4 KiB container lease.
Consuming data cannot retire container/header metadata. Legacy `changes()`
keeps its existing result shape.

RLCD verified 168 Observer inputs, 93 reported Mesh inputs, six protected inputs,
four artifacts, two agreement pins and four producer logs. It independently ran
all 15 new completion tests and 24 existing source tests on Python 3.14.8 and
3.11.17 against the reported Mesh `05ad6fc`, with GC disabled and zero skips.
The producer's separate full gate reports 914 passing tests.

RLCD also composed the actual owned source and Agent structural codec with
deadline-corrected Mesh `f32218b`, verifying 188 Mesh inputs. Twelve cases pass
on each Python version: full/active zero/one/four synthetic ServiceState changes,
plus bad-terminal rejection, scope close and repeated cancellation during a
blocked material drain in both views. Original material and whitespace-padded
completion bytes survive; complete follows material drains. Invalid terminals
emit no prefix, interrupted drains emit no completion, live input credit persists
through cleanup and siblings remain usable. All five final relay counters are
zero, and both version reports are byte-identical. Independently admitted
received material remains unconfirmed until a fresh synthetic proof; public
DTO exports then match the owner. That proof uses disclosed test-owned challenge
setup, rather than a selected Reader/controller route.

This clears the method-implementation prerequisite and adds bounded actual-source
composition evidence. Disposable sockets, synthetic state and oracle-owned
sink/server storage do not establish populated native, aggregate resource/RSS,
CPU/bytes, dense/recovery or installed-pair acceptance. The consuming-ref pruning
helper is unchanged, so the separate finding below remains open. No schema/ID,
artifact, service, route or consumer selection changes.

Observer subsequently commits its two-IPC probe and historical failure at
`5397f66707a0d1d578da9761758220579da7a73c`. Its manifest
`completion-relay-join.json` is 72,901 bytes, SHA-256
`87551d631b99945e5c3cfa0de34804f0d24f54c06fc02f587143ff53d4c7df7b`;
the unchanged `verify_completion_relay_join.py` has SHA-256
`c6b1add15621294d8ce77aa229f06b6c3127d01410b27e174549b124bf9f19a4`.
The original pair uses older Mesh `b57c217`: six errors on each Python, at its
unsupported completion `nativeBindingDigest` lookup. Those failed logs remain
historical evidence. The existing `be6470ed` correction removes that lookup
while preserving typed base/target/tag binding checks.

RLCD verified 168 Observer inputs, 152 historical Mesh inputs, six protected
inputs, three artifacts and the failed reports/loaded-module pins. It then ran
the exact unchanged probe against both `be6470ed` and `f32218b`: all six full/
active zero/one/four cases pass on each Python version, with original native
fragments preserved over two disposable UNIX IPC paths and five final counters
zero. Every loaded producer module matches its immutable commit. This adds
passing controlled two-IPC completion evidence without modifying the source or
reattributing the old failures. The probe uses a trusted test controller and
does not exercise an independent Reader or fresh proof; the broader gates and
separate pin-tracking finding remain open.

### Independent receiver proof

Mesh evidence commit `75b8aae70fb560b8d9d2de53101b407a5d58940b` adds the
actual source/scanner/relay and independent receiver cache on the same
Observer `2f697d4` / Mesh `cdb8cd0` (`f32218b` runtime) pair. Its guide
`docs/delta-sync-completed-relay-g1.md` has SHA-256
`a53fc31581bbcb54d74ce9470d0469b4a064cec101f35b1b48e61240a5156063`;
`completed-relay-review.json` is 86,603 bytes, SHA-256
`e1d94203cacfda9adc6b6ea55f1978d37e9adb50241cdecbacd7704ab298c10f`.

RLCD verified 188 Mesh inputs, 215 Observer inputs, eight Mesh and six producer
protected inputs, 88 declared loaded modules, three producer packet files and
eight result/log artifacts. Mesh reports 194 passing tests per Python version;
RLCD independently reran only the eight new methods, preserving every assertion
and teardown. Both Python 3.14.8 and 3.11.17 pass with GC disabled; all 66 modules
loaded by that subset match their immutable commits. The unchanged 186 owning
tests retain their separate execution evidence.

Full/active zero/one/four chains preserve original native bytes across both
UNIX sockets. Completion leaves material unconfirmed; a fresh head obtained
through the actual source and relay passes normal cache confirmation, then
public DTOs equal the owner. Additional cases cover native control limits,
malformed terminal rejection, original recovery bytes, held drains, source close,
cancellation and failed material/control writes. Relay and receiver teardown
counters reach zero while sibling state survives. The trusted test controller
and private nonce setup do not qualify the ordinary acquisition dispatcher or
a selected Reader route. Batch cleanup passes independently of the still-open
detached-head tracking gap. Dense/eight-MiB relay delivery, aggregate resources,
performance, populated native/fixed SSH and installed-pair acceptance remain open.

Observer's separate recheck at `8f05305c699ac22960847c2bc757c2ef7c812d1c`
preserves its historical failed pair and confirms the existing correction on
Mesh `be6470ed`, separately using Observer `2f697d4` and `fc7579b`. Its guide
`docs/delta-sync-completion-join-recheck.md` has SHA-256
`107b0f80284d339649e86c35ef7f1cbd99405896c4209f4bf3e8e4de03015055`;
`completion-relay-recheck.json` has SHA-256
`8630d828cd65aa5f7662bc6da5f2d0e7a7ce25f9dba386cbb77a6986085f2491`.
RLCD verified 187 upstream Mesh inputs, eight protected inputs, the exact
152/207/209-file Mesh/old-Observer/current-Observer inventories, five artifacts,
eight retained logs and six saved reports with all loaded-module pins.

RLCD independently ran only the six new Reader cases on each Python version
against immutable Observer `fc7579b` / Mesh `be6470ed`, with GC disabled and all
66 loaded modules verified. Each full/active zero/one/four case admits a baseline,
confirms it with a fresh native nonce proof, stages actual source transactions
and confirms the final native tag/DTO with a distinct second proof. Both proofs
and catch-up share one acquisition capsule. All six Reader and five relay
counters finish at zero. The unchanged forwarding/source/relay suites retain
their existing logs rather than being rerun. This adds sequential synthetic
Reader evidence; it does not fix the consuming-ref defect, qualify network
controller dispatch, combine the separate ledgers into an aggregate budget,
or establish dense/recovery, CPU/RSS, native or installed acceptance.

## Open source pin-tracking finding

A distinct revocation gap is independently reproduced on Observer
`3a751916dd0492e3003a96179bc2121bb628668b` with Mesh `be6470ed`.
The committed diagnostic is
`mesh-plus/docs/evidence/2026-10-16-delta-sync/probe_source_inflight_prune.py`,
SHA-256 `4652a9215421bb92ff801f98db1896d75c9fb68e702b3548dd4baa0577a71fe2`.
It uses the actual source's head receive over a synthetic UNIX fixture and a
disclosed private Mesh `input_bytes` pin. Source lifecycle/count checks use
public `inspect()` and `aclose()`.

Without inspection during consumption, session close makes pin exit reject
`sync_input_retired`. With inspection, the session's `nbytes`-based pruning
drops the registry from one ref to zero, and pin exit succeeds after session
close. Both Python 3.14/3.11 reproduce the difference with cyclic GC disabled.
The 1,753-byte input remains charged through the pin and all five final counters
reach zero. This is a tracking/revocation failure; no late relay output,
material authority or cap overrun was measured.

The owning source/generic retirement seam must preserve session/scope revocation
of consuming refs while keeping history bounded, physical pin credit charged
and sibling/shared-owner lifetimes intact. Source receive also invokes this
pruning helper; the reproduced case uses inspection. Existing `nbytes`
semantics and the shared ownership API are not changed by this finding.
Its owning coordination and actual source-to-relay acceptance remain open;
the previously closed watch-close and cache material-credit findings stay closed.

Observer commits the current-source regression packet at
`90b4292bee4a441d00e6dd22fe566e75211b656f`. The proposal document
`docs/delta-sync-source-pin-revocation.md` has SHA-256
`c5307671c03099004dfa4e4e20b06471277b51af57326b4910d381a631322918`;
`source-pin-revocation.json` is 45,555 bytes, SHA-256
`278e095b3143bb55a6cf58cadc048128b0b52db0f23cbed1932aea9836428141`.
RLCD verifies 168 Observer inputs, 152 reported Mesh inputs, six protected inputs,
four artifacts and retained logs. The unchanged five-case regression overlay
also reproduces on current Mesh `f32218b` on both Python versions with GC
disabled: three expected failures and two passing controls. Inspection and
automatic receive still lose a consuming ref's revoker; terminal-history and
no-inspection controls pass. Ordinary and relay input source files are identical
between the reported `b57c217` and current Mesh pair.

Observer's test-only refinement at `a10ed72b610a2edc2d551030471e153b171f1ff9`
closes the requested assertion hardening. Its overlay has SHA-256
`fa9fd6e95bc25c72cb328bb6ef01aa49e8bd78cf1f39721091550135184600bb`;
`source-pin-helper-hardening.json` has SHA-256
`b0b323cac3b7ddab2fd2a0f70a9bd553bfddeac8f836e31dbdb075a7c2918c6b`.
The helper now proves the shared-owner reserve, sibling access and raw cleanup
finished before accepting a pin-exit rejection. RLCD verified 210 Observer and
152 Mesh inputs and independently replayed the unchanged new harness on both
Python versions with GC disabled, verifying all 47 loaded modules. Injecting
`sync_input_retired` inside the pin body incorrectly passes the old helper but
fails the hardened end-of-body assertion. Both overlays still reproduce the
same three runtime failures and two passing controls; all five final counters
are zero. The original overlay, receipt and failed logs remain unchanged. This
closes the test prerequisite only; the source pin-tracking defect remains open.

Observer first proposed additive `revoked` status to distinguish logical
retirement from a healthy consume and physical storage reclamation. The
owner-bound query below supersedes that property proposal. No `nbytes` change,
private graph access, healthy-pin
revocation on inspection or early physical credit refund is accepted by this
proposal review. These expected failures confirm an open gate, not a source fix.

Mesh provides the concrete owner-bound alternative at
`d8d7a6233f625ba352c3451396770a61b28635c7`:
`docs/delta-sync-ref-retirement-proposal.md`, 6,067 bytes, SHA-256
`298efa4af40a23651702ac85862d817a045e9b7e781daf363bc43e1300aaf018`.
Its `ref-retirement-proposal.json` has SHA-256
`f498c415818e05829545c9abc8db382e1eb5a52d42c668c9d4dbe434a38350aa`.
RLCD verifies the exact packet, five input pins, three diagnostic pins, source
pin and retained design-check log; production sources remain unchanged.

Coordinator review is clear for `InputOwner.ref_is_retired(OwnedInputRef)` and
the corresponding relay-owner/ref method. Both return an exact bool using
constant-time lifetime metadata. Available or healthy consuming refs return
false; logical revocation, terminal consumption and a retired intake epoch return
true even if physical pins remain charged. Wrong type/role/owner or malformed
refs reject `sync_input_owner` without mutation. A closed minting owner can
still answer for its own refs. The query provides no bytes, currentness,
admission or proof capability and cannot refund credit or retire a graph.

The owned source requires a callable predicate before reserving session state
or starting I/O, checks exact bool results, prunes only true and drops the
captured query after its own children and I/O retire. Missing capability rejects
`sync_source_input_owner`; no ambiguous `nbytes` fallback is supported. Exact
Observer agreement is now recorded at
`5543fc79c7568b6d9e8da7d018e7703ac26e1a06`,
`docs/delta-sync-input-retirement-agreement.md`, SHA-256
`4e10173eb5cdf8b231e21f80ccf46cbfa9fce2f44d6a73f406020dcfcca008cf`.
Its `input-retirement-agreement.json` has SHA-256
`fc87b17654da3ae4d3fe348bb6eb47eb612ca21cdda24fca1bb6a66705e18ee0`.
RLCD verified all five agreement artifacts, its retained check log, the exact
Mesh proposal and unchanged defective source. Both owners now agree these
bytes. Existing G1 authorization covers Mesh's committed public method and the
dependent Observer source fix without another general or coordinator approval.
The query and source fix still require the stated
cache/relay, detached-head, sibling, cancellation, bounded-history and
GC-disabled accounting tests, including independent before/after replay of the
original failures. This closes the interface-agreement step only; the source
pin-tracking runtime finding remains open.

Mesh implements the agreed public query at
`6fce5ed0e997d021e7532051fe985c3693962c3e`, with evidence commit
`2ec7bcf3a3422a68bd522502928a648954932e1d`. Its guide
`docs/delta-sync-ref-retirement-g1.md` has SHA-256
`1d9185992aa92bd46bf5baf9f79cebfecaaab3b314cb942a87f44c17c886334e`;
`ref-retirement-g1-review.json` is 96,732 bytes, SHA-256
`b7b007d80e85325e70173565852231d97a069a6ada25a6b88262d41a975aa7b9`.
RLCD verified 188 current and 188 parent inputs, eight protected inputs,
the exact agreement documents and retained logs/results. Code review confirms
metadata-only owner/role/ref checks, healthy consuming versus logical retirement
states, preserved physical pin credit and unchanged `nbytes`/consume behavior.

RLCD independently ran the seven new cases on Python 3.14.8 and 3.11.17 with GC
disabled, verifying all 31 loaded modules. Both fixed runs pass without errors
or skips. Exact parent plus only final test overlays yields seven missing-method
errors per version: evidence of absent capability, not an old source-contract
failure. The producer's 60 focused and 355 canonical passes retain their saved
execution scope; its earlier draft assertion failure is not hidden or relabeled.
This clears the committed public-method prerequisite for dependent Observer
adoption under existing G1. The source still needs callback adoption and final
paired inspection/receive/close/cancellation/sibling and held-pin replay before
the consuming-ref runtime finding can close. No broader producer or artifact
acceptance is inferred.

## Relay deadline and failed-intake correction

The head-deadline and source-error cleanup findings are now independently closed
at bounded source scope on Mesh `f32218bffab8860d374964721e35384f66a86269`.
The owning guide `docs/delta-sync-relay-deadline-g1.md` has SHA-256
`0be8dcb7b13e7a3c1a9cf12a6ff538402b2f51268ad8c056f0f66eb8a0c21df2`.
Evidence commit `028d90b63fed69bb1e095d8da44e2cce73a7e9a5` contains
`docs/evidence/2026-10-16-delta-sync/relay-deadline-review.json`, SHA-256
`bf0e529d9ad6b58cb22ebef3a7703254c2485390a04b45cf98638b3f941541e2`.

One absolute head deadline is captured at public entry and checked through
source/scanner/header handling, queued output locks and before each physical
write. Pre-write expiry retires only that acquisition and preserves an
independent watch's buffer/limits/credit. Failure after output starts closes the
affected channel while retaining pins through physical cleanup and repeated
cancellation. A source exception before returning any batch also initiates its
own channel/session cleanup; the worker unwinds before awaiting that cleanup.

RLCD verified 187 Mesh inputs against runtime and docs-only gate commit
`cdb8cd0e3c5f11e65728d2de7c157e89ca26d819`, 211 immutable Observer inputs,
eight protected paths and thirteen artifacts/logs. On Python 3.14.8 and 3.11.17,
six final regression methods overlaid onto prior `171f21c` reproduce seven
expected failing checks; the fixed runtime passes all 33 focused tests with
cyclic GC disabled, retained errors and five final counters zero. The unchanged
original probe moves from one write at 2,101 ms to no writes; neither run emits
a complete expired proof. Its malformed baseline chain fails inside the source
before returning a batch: five live tracked refs/open session before, zero
tracked refs/closed session after. Returned count/type rejection already passed
before and is not attributed to this correction.

Six actual-Agent structural-codec fixture composition cases also pass on each
Python version. The producer's docs-only gate passes 348 canonical tests with
zero skips; its initial future-evidence-link failure remains preserved alongside
the final passing log. These source checks do not close the separate consuming-
ref pruning gap or qualify actual owned-source completion, controller grammar,
aggregate resources/performance/native transport or an installed pair.

## Controller contract review

Mesh proposes the first explicit network control plane at
`5cee72e2d9fe2da8f27102774e09243b906e01ad`:
`docs/delta-sync-controller-proposal-r1.md`, 17,270 bytes, SHA-256
`18e8f7f97462613a72353e00e2ffa579b452fdf7855a91443198dca00d51900e`.
Its `controller-r1-review.json` has SHA-256
`4b123b9e2535f2a0f707cff58ae7edc27f1d09056b4ffa843eb290342597ca81`.
Versioned open/command/result records remain separate from unchanged R4 data
delivery and original native controls. Bounded sequence IDs, request digests,
drained delivery watermarks and restrictive-only head deadlines fit that direction.

RLCD verifies 188 Mesh inputs and eight protected inputs, unchanged production
sources and exact packet/vector bytes. The toy model reproduces 14 positive and
34 rejection cases identically on Python 3.14.8 and 3.11.17. It does not model
the new results, carrier ingress, busy scheduling or cancellation concurrency.
The R1 review required two contract clarifications before dependent dispatcher
edits:

1. Cancel revokes its capsule, then requires a cancelled receipt for the original
   command and an OK receipt for cancel. End similarly requires OK after closing
   its capsule. The blanket ban on results after capsule revocation forbids those
   receipts. Define bounded cleanup-receipt ownership under the original immutable
   deadline, distinct from revoked material/proof authority, and make terminal,
   busy and expiry-result rules consistent. No new time grant or revived work.
2. Specify how the first-byte timestamp reaches the dispatcher from the prepaid
   userspace carrier, including coalesced tails and paused reads behind blocked
   output. Sampling at later dequeue/parse would renew time already spent buffered.
   For example, bytes admitted at 1,000 ms with 2,000 ms remaining are expired at
   a 3,500 ms dequeue; they must not gain a new 5,500 ms deadline. Define a supported
   timestamp handoff or an equally conservative bound, rather than assuming an
   existing buffered `LineChannel` exposes that provenance.

These were control-plane contract findings, not new runtime failures or changes to
the accepted data/role/completion contracts. Their original R1 evidence remains
unchanged; the R2 reconciliation follows.

### Controller R2 reconciliation

RLCD's coordinator contract review is clear for standalone Mesh
`33cb57c98ca3062f139ea1fd0c68b15bd5abd8d6`,
`docs/delta-sync-controller-proposal-r2.md`, 31,399 bytes, SHA-256
`89b24a9f3191bcded303d33c8b2ed973335b703811185abf1186848fbd562f48`.
Its `controller-r2-review.json` has SHA-256
`40092583a0e5732f62512d6026eb96b28fce5623e5e0d4a64e11af291a09ba3c`.
Both R1 findings are resolved at contract scope:

- Bounded, single-use receipt records carry exact immutable command/request/
  channel identities and their original deadlines separately from retired work.
  Specified end/cancel/failure/busy receipts cannot revive material or proof
  authority. Request/channel retirement invalidates all receipts. An expired head
  receipt is suppressed even if a still-live cancel receipt confirms cleanup.
  The drained `through` watermark is captured once under the output lock.
- A minted, prepaid carrier for unread IPC sockets or fixed stdio descriptors
  stamps immediately before each nonblocking userspace admission. Immutable byte
  ranges retain conservative first-byte floors through coalescing, fragmentation
  and paused reads. Missing provenance rejects; dequeue time cannot renew the
  bound. Its ring, range metadata, frame/header copies and output ownership remain
  subject to the original aggregate caps.

RLCD verified the exact proposal/manifest/vector bytes, all unchanged R1 pins,
188 Mesh inputs, eight protected inputs and an empty runtime diff. The unchanged
toy reproducer passes identically on Python 3.14.8 and 3.11.17: R1's 14 positive/
34 rejection cases plus R2's 15 positive/32 rejection cases. These are metadata,
state and arithmetic checks; they do not qualify minted provenance, actual
carrier storage, strict dispatcher/result parsing, concurrency, I/O, physical
cleanup or resource accounting.

Exact Observer agreement on these R2 bytes remains to be recorded. Once both
owners agree, the existing G1 authorization covers dependent controller/carrier
implementation without another general or coordinator approval. The separate
source retirement-query implementation and all original correctness/lifetime,
32/64 MiB, two-second/fifteen-second, dense CPU, deliverable 2,000-row recovery,
RSS, populated native IPC/fixed SSH, immutable installed pair and end-to-end
gates remain open. This review grants no API freeze, runtime or producer
acceptance, selection change or rollout.

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
