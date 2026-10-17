# Compact normalization interface agreement

Status: **joint interface agreement complete; dependent G1 implementation
authorized**, 2026-10-17 UTC. Mesh, Observer and RLCD accept the exact R2
public-intent and raw-reference contract below under Bryan's existing
[execution authorization](delta-sync-plan.md). The complete Agent compact
schema/encoding freeze and runtime qualification remain open. Frozen G0 bytes
and the separate [A1 relay agreement](delta-sync-relay-addendum.md) remain unchanged.

## Accepted inputs

| Evidence | Accepted revision |
| --- | --- |
| Mesh standalone R2 and agreement | `b9dd8c610ea4575c1f4441d9331cfaef5ac1f58c`, `mesh-plus/docs/delta-sync-codec-contract-r2.md`, 27,992 bytes, SHA-256 `0920bf9ea7c2e76695c2cfe21016636a5ae3ebeac60f59be44f0fac914d8f44d` |
| Mesh review manifest | Same commit, `docs/evidence/2026-10-16-delta-sync/codec-review-r2.json`, SHA-256 `a3555b021414e45bac432190ebf9eff863763d8d4590f500df744beb887a0273` |
| Observer normalization decision accepted by Mesh | `ffa302fba16f90d00c39229ae810547aeb850908`, `agent-observer-active-feed/docs/delta-sync-normalization-decision.md`, SHA-256 `35b1911388e75f4bc2a87087f23f07f7ca95346719933d7b37a5365d528734d6` |
| Observer exact R2 signoff | `8a075bc78ef6f3710fa47ea57136260d5703dfee`, `docs/delta-sync-codec-r2-review.md`, SHA-256 `337c5ac11ab803f7121ee632e193b1d6c46e2a0b7ff0cda17b5c638bca9d9772` |
| Observer agreement evidence | Same commit, `docs/evidence/2026-10-16-delta-sync-source/codec-r2-agreement.json`, SHA-256 `52bbc0ecdba1ca7107cb507993bdc84525a84b5965c67c9fc376d60f32f254fd` |

RLCD verified these committed bytes and both owners' explicit agreement.
Observer reports no remaining public-intent, alias/birth, receipt-side or
normalization contract conflict. This is the coordinator reconciliation needed
before dependent shared implementation. Changed accepted semantics require an
identified amendment and joint review.

## Accepted decisions

- `native_codec=None` keeps strict expanded admission. A configured codec,
  descriptor/schema and explicit profile features are captured locally; a
  payload cannot select an implementation or fallback.
- Streaming plans validate each closed wire value before yielding, exhaust
  required spaces before commit and retain one value's scratch plus charged
  overlays. Public HeaderRef, alias and MembershipGroupIntent handles are
  metered and revocable; detached copies have independent prepaid ownership.
- Raw record/group references carry birth guards and resolve on the side fixed
  by their typed position. Before/after receipt dictionaries contain at most
  32 distinct full keys each. Removals and expected-old refs use before only;
  replacements use after only. A changed full cohort key or record identity/
  birth requires separate removal/insertion groups. Reordering cannot
  reinterpret an old reference.
- Compact `membership_expansion` is exactly `()`. The generic engine alone
  expands cells after independently validated field tokens/indexes; omitted
  masks still receive real token changes. Expanded behavior and all four
  semantic callbacks retain their contracts.

Every stage must independently reproduce the same eight logical tables,
cohort seals, body IDs, native root and source wrapper at the same complete
descriptor/generation. Mask assertions, receipt keys and token changes alone
cannot renew evidence. Failure rolls back all provisional aliases, cells,
indexes and owned allocations without publishing authority.

## Evidence and implementation ownership

Observer's stdlib checker SHA-256
`963493e4c49f9487ac3bc36a5e24bbef54a4cc29c354142e71a935521a309170`
imports neither producer nor Mesh's oracle. RLCD inspected and reran it on
Python 3.14.8 and 3.11.17 against the exact reference fixture SHA-256
`82f70805585aed2d7a70a2d10736de5650c9dad370b5cb811121fd47ad1761be`.
All six positive cases, 26 named rejections and two permutations pass, with
identical output. The earlier upstream replay remains separate evidence.
These checks cover toy sided-reference/mask syntax. They do not exercise native
schema, admitted old masks, receipt existence, roots, lifetime or resources.

Mesh may implement the agreed generic configured-codec, staged alias/group,
intent/ref, token-expansion and root/rollback APIs. Observer may implement its
pure Agent codec/profile facade, streaming restoration and owning native export
through those public interfaces. Each owner stays in its repository and
preserves concurrent work. No further general execution go-ahead is required.

Observer owns the complete Agent compact envelope, positions, schemas, encoding
identity and joined raw-restoration vectors. The candidate compatibility
checkpoint below permits dependent implementation; schema/API freeze and
immutable artifact qualification remain separate. This agreement allocates no
encoding, schema identifier or package version.

## Candidate wire compatibility

Observer's concrete candidate is commit
`c161090b0108e7102f77ed7936e6f41bcacb8f51`. Its exact inputs are:

| Input | SHA-256 |
| --- | --- |
| `docs/delta-sync-compact-wire-proposal.md` | `585d4172400d628737ad68064ab8ecdd768fe7ef29456197c2671722f817c5c2` |
| `agent_observer/contracts/sync-compact-frame.schema.json` | `cad76406eceab62bb5ba982f3472258b0f604d05dc890a865c7cd2acb43fb23e` |
| `docs/evidence/2026-10-16-delta-sync-source/compact-raw-vectors.json` | `a45ad79025dd8ae606db52735d9c63fa018c6d9640f5b2e81f31b01f43c387b5` |
| `docs/evidence/2026-10-16-delta-sync-source/verify_compact_raw_vectors.py` | `9d925a96aa661a2b5ef90a8e5529f15c8591e7949c204fdbe697b94ecc440850` |

Mesh's attributed G1 coordination receipt `e-0760ef9f` confirms same-byte
compatibility of the fixed raw positions and explicit single configured
encoding/journal with R2/R4. This receipt is distinct from an accepted runtime
commit or installed artifact. RLCD already independently reproduced the ten
candidate tests on each Python version and the exact fixtures/verifier: eight
baselines, ten transactions, 144 field tokens, seven lossless joined rows and
eight model rejections. Mesh reports identical dual-version verifier output.
The two alias-reuse cases are derived synthetic fixtures.

The design compatibility condition for dependent Agent/G1 implementation is
satisfied on these candidate bytes. The proposed `agent-observer.compact/1`
identifier remains unallocated and the schema remains unfrozen. Actual streaming
Agent admission, exporter/source dispatch and generic runtime qualification
still require their original correctness, ownership and performance gates.

## Generic source checkpoint

Mesh's opt-in implementation is now available for Observer's owning integration
at runtime `05ad6fc8db1725afd6aac19435af83e4c0eb46eb`, following the initial
implementation `030da1f0ac083fc51bf9ad10fc93e62678719cdc`. Its exact supported
API and source evidence are:

| Input | Revision and SHA-256 |
| --- | --- |
| `mesh-plus/docs/delta-sync-codec-g1.md` | Runtime `05ad6fc8`, 5,232 bytes, `1eede320e3667f81d909fe2fc3b783962f71c6acd70c4296790ffa1d6f92d26f` |
| `mesh-plus/docs/evidence/2026-10-16-delta-sync/compact-g1-iterator-review.json` | Evidence commit `51b8e8d6db6cd7a14dce2333f5b52a2f05d2abff`, 35,936 bytes, `10462a1c77cb1b8015db5dcdfdbb33491fc64c8529ea0659d4b0b300d392e50a` |

RLCD reviewed the public configured-codec, staged alias/group, provisional mask,
generic token expansion and root/rollback paths. It verified 187 Mesh input
pins, eight immutable Observer `c161090` packet inputs, six protected paths and
five producer logs. The API document also records the candidate wire
compatibility above in a durable Mesh source commit.

On independent immutable exports, RLCD reran all 25 focused tests on Python
3.14.8 and 3.11.17. With the final test file overlaid on the initial runtime,
both versions reproduce the held-iterator failure: 509 bytes and two pending
allocations survive close. The fixed runtime passes all 25 tests on both
versions, with cyclic GC disabled, public errors retained and all five final
allocation counters zero. The source inputs remain unchanged after execution.
Mesh separately reports its 330-test canonical gate; RLCD did not rerun that
broader suite for this bounded review.

This clears a generic source prerequisite for Observer's already-authorized
integration. The test codec decodes a whole small fixture; actual Agent
streaming admission, source/export wiring, inclusive resources, performance,
native transport and immutable installed pairing remain unqualified. No
schema/encoding identity, package version or consumer selection is allocated
or changed by this checkpoint.

## Agent streaming source checkpoint

Observer's actual codec/profile integration is commit
`c1ae31f575921e58e23dbcd59585128a143585a9`. Its guide,
`docs/delta-sync-compact-codec.md`, has SHA-256
`00a9e968f97cc9777ed28c1e7535ec9afbda73797755e1e00e93266437397651`;
the source manifest `docs/evidence/2026-10-16-delta-sync-source/compact-codec.json`
has SHA-256 `538a6c0680883c95c0d7df605df5648485a53ab6d85e9176ae3d07ebdab76c0a`.

`AgentCompactSyncCodec` uses public configured specs, sided aliases, keyed
before/after-record state and `ctx.pack`. The Agent profile validates support
and mask intents, supplies nine derived tokens for changed bodies, returns an
empty compact membership expansion and leaves cell writing to Mesh. Head uses
the original bounded decoder without loading the material schema. The schema
graph has an explicit conservative 8 MiB reservation per plan in the same heap
ledger; this is included source ownership, not dense-capacity acceptance.

RLCD verified 167 Observer inputs, 93 reported Mesh inputs, 89 legacy Mesh inputs,
seven artifacts, eight producer logs and four unchanged candidate wire inputs.
It independently ran 76 selected codec/parser/profile/read tests on both Python
3.14.8 and 3.11.17 against each of Mesh `030da1f` and reviewed `be6470ed`.
All pass with cyclic GC disabled and no skips. The older `66b9c1e` expanded
profile/read/owned-source path also passes all 68 selected cases on each Python
version. Full/active warming fixtures pass on both compact pairs.

The source tests admit eight raw baselines and ten transaction cases to the
expected native roots, check independently recomputed source wrappers, reject
eight schema-valid invalid cases, preserve genuine equal/omitted-mask token
changes and losslessly export full/active native DTOs after synthetic fresh
confirmation. Dotted source names in the frozen arithmetic corpus remain
unchanged; runtime tests use explicit valid `agents_full`/`agents_active`
bindings and recompute their distinct wrapper roots. SDK name checks are intact.

Observer follow-up `b3a85bd77cd2cf76ac2f16c88f61f2dfd9398110` independently
pairs the unchanged `c1ae31f` runtime with Mesh `05ad6fc`. Its separate
`docs/evidence/2026-10-16-delta-sync-source/compact-codec-mesh05.json` is 64,702
bytes, SHA-256 `60699fa7f576d49b8f77ec480f9f6ec0d2d7162fa0e8b9d70562ef60875e1185`;
the updated guide has SHA-256
`f160b5fa9d1ed34d2731d0cb249496509b5ae4c0ee80ad1f273a4c764e6a7020`.
RLCD verified 167 unchanged Observer inputs, 93 Mesh runtime and 59 test inputs,
93 historical Mesh inputs and seven logs. Observer's 171 integration cases and
25 Mesh cases pass on each Python version with GC disabled; the old 509-byte/
two-allocation iterator failure reproduces before the fix. This corroborates
the prior root source/lifetime checks without reattributing earlier `030da1f`
results or claiming native, resource, performance or installed-pair acceptance.

Mesh follow-up `b65cb2cbe2ef2355a7392b6ce69acc7a2478dd06` runs the same 171
Observer cases on each Python version against deadline-corrected Mesh `f32218b`
(docs-only gate checkpoint `cdb8cd0`). Its
`docs/evidence/2026-10-16-delta-sync/observer-compact-review.json` is 81,308 bytes,
SHA-256 `3a149e63e3e2981e345d351aa6ad1c289c83ce1f14d1955b9d1a35cd52012a87`.
RLCD verified 188 Mesh inputs, 214 Observer inputs, 87 loaded modules, eight
protected paths, four raw packet inputs and six retained logs against immutable
commits. Both runs pass with GC disabled and no failures, errors or skips.
This adds independently executed owning tests on the newer source pair; it
does not add independent test design or populated native evidence. RLCD reused
its prior codec and relay runtime checks for this documentation-only handoff.

This was bounded synthetic source integration. Actual compact native serializer,
journal and source dispatch, schema/encoding freeze, inclusive memory/RSS,
dense/cold/recovery CPU/bytes, deliverable 2,000-row recovery and populated
IPC/fixed-SSH/immutable installed-pair acceptance remained open at that checkpoint.
The following sections record later serializer and source progress. The separate
source pin-tracking finding was still open at that checkpoint; the later relay deadline correction
is [independently closed at source scope](delta-sync-relay-addendum.md#relay-deadline-and-failed-intake-correction).
This codec checkpoint changes neither path. Current a7/a23 and protected routes
stay selected.

## Native compact owner output

Observer implements the native serializer at
`fc7579bd2e3e6b020b4e66958e8e425e60889b93`. Its guide
`docs/delta-sync-compact-export.md` has SHA-256
`5fc10018f3ed7050eaa0a923c9ab876f7ec444448e31e25d22bc34c7f743e46b`;
`docs/evidence/2026-10-16-delta-sync-source/compact-export.json` has SHA-256
`ae25cbacfb0b4de3291e68fbfe0b562230172bbf8b071f08b7c4e87c1aae1e58`.
Explicit startup selection `sync_serialization="compact"` chooses one serializer
and bounded journal on the encoded owner. Expanded remains the default; the
compact path has no expanded fallback. Head, control, logical descriptor and
roots remain unchanged. No encoding identity, route or schema is allocated.

The exporter walks committed encoded values one at a time under prepaid scratch
and output construction credit. Sparse mask changes come from changed observation
keys; unchanged masks, including token-only body edits, stay omitted. Mesh retains
sole responsibility for cell expansion after independent domain admission.
Serializer-only scan bounds do not establish sparse total owner publication work.

RLCD verifies 170 Observer inputs, 146 reported Mesh inputs, six protected inputs,
seven artifacts, seven logs and three cold-screen reports. It independently runs
all ten new export tests on Python 3.14.8 and 3.11.17 against both reported Mesh
`05ad6fc` and current `f32218b`; all pass with GC disabled and no skips, and loaded
producer modules match their immutable commits. Tests cover exact expanded/compact
reconstruction, roots, warming, sparse journals, unchanged head/control bytes,
fresh direct receiver confirmation, expected-old/root rollback and bounded frame/
quota refusal. The producer's separate 196-focused/924-canonical gates retain
their original execution provenance.

The verified producer cold screen emits full compact frames of 142,313 / 687,515 /
2,739,021 bytes at 100/500/2,000 identities, versus 168,077 / 826,477 / 3,297,477
legacy bytes in the same fixtures. The ten-selected active frame is 19,545 bytes.
These full fixtures have 710 / 3,510 / 14,010 membership cells, rather than nine
fields per row. Only current cold full/active owner state is present: no predecessor,
overlapping stage, slow peer, intake, relay, Reader or RSS measurement. This is
source-frame size evidence, not accepted dense capacity, recovery or whole CPU
improvement. Earlier CPU failures remain failed. Actual compact source/IPC dispatch
was still pending at that owner-output checkpoint; the source work follows.
Inclusive pipeline qualification and immutable installed pairing remain open,
and the selected a7/a23 tuple stays unchanged.

## Explicit compact source and native dispatcher

Observer implements the opt-in source at
`7213084557ed4dd63361567bb75bd262b2e517bc`. Its guide
`docs/delta-sync-compact-source.md` has SHA-256
`72f9aa63c74ff86141bb03c9e877d724bd20eb542d721c4edcf41974858e02e7`;
`compact-source.json` has SHA-256
`069f9e181c2beb2b5dc7817d575e2a021c116c9538577975ab8279b0b5107b7e`.
Pure `agent_observer.sync_compact_source.CachedCompactAgentSyncSource` retains
the existing constructor and owned session/batch/head/watch surface. Explicit
parser selection uses the compact structural scanner for material and the
original parser for heads. It captures a static callable without a bound-parent
cycle. Unowned compact byte operations reject before I/O; the expanded source
remains strict and default. There is no sniffing or format fallback.

RLCD verified 212 Observer inputs, 152 reported Mesh inputs, five artifacts,
four unchanged raw-convention pins and retained logs/diagnostics. It independently
ran only the seven new methods on Python 3.14.8 and 3.11.17 against both reported
Mesh `f32218b` and query-enabled `6fce5ed0`: all 28 method executions pass with
GC disabled, no skips and all 79 loaded modules verified per run. The producer's
203-focused/931-canonical results keep their saved execution provenance.

Synthetic state uses the actual disposable native Runtime dispatcher with
collection disabled. Full/active zero/one/four chains preserve the exact frames
returned by that dispatcher. Independent compact Reader admission/staging,
fresh original source heads and final lossless DTO export pass. Other cases
cover wrong-route rejection, a large opaque invalid body forwarded then rejected
by the Reader, original head parsing without compact/schema work, import purity
and watch-close revocation that preserves a prior baseline ticket.

This clears a component prerequisite for ongoing G1 integration. Private test
nonce/native-byte pin and a test-assembled proof carrier remain disclosed; the
tests do not exercise generic relay/controller forwarding or authenticate an
installed route. Native fixture, oracle and Reader allocations are separate.
That source's pruning AST is unchanged, so its consuming-ref fix through the
agreed query remained separate and open at that checkpoint. Aggregate resources/RSS, total CPU,
dense 2,000-row/cold recovery, populated providers/fixed SSH and immutable
installed paired acceptance remain open. No ID/schema allocation, service,
provider, selection, sibling or rollout action occurs.

## Compact source through relay and Reader

Mesh adds test-only composition evidence at
`6be8fc9f149596e85e8cfc90e3904e54ee3b4269`, pairing unchanged Observer
`7213084` with Mesh runtime `6fce5ed0`. Its guide
`docs/delta-sync-compact-relay-g1.md` has SHA-256
`7fac4fe763baceecd5211b2808948bbe4e79e53bc6ad296e5c4bfa7314567079`;
`compact-relay-review.json` has SHA-256
`9f1366841c31f66c60853968ead59b008c710072e4636d18a3d05e9af7348dba`.
The exact `verify_compact_relay.py` has SHA-256
`bbeb88cf0ca8619f6a750bc018dd15279e6bc09797aba5cd58278b8c2dc087c2`.

RLCD verified 188 Mesh inputs, 212 Observer inputs, eight protected inputs,
the prior source-review receipt and preserved harness diagnostics. It then ran
the unchanged three new methods on Python 3.14.8 and 3.11.17: nine scenarios
per run pass with GC disabled, retained errors, no skips and all 73 loaded
project modules verified. The earlier 203 component tests were not rerun or
combined into these counts. Two earlier framing/extraction mistakes remain
explicit test-harness diagnostics, with no production change or failed-before
claim.

The actual disposable compact Runtime dispatcher, compact source and structural
transport codec feed Mesh's byte relay over two UNIX sockets into an independent
compact Reader. Full/active zero/one/four chains preserve exact baseline,
transaction, whitespace-padded completion and head fragments extracted from
received Mesh bytes. Baseline and target use fresh original relay-head proofs;
an original valid completion presented as a proof rejects `sync_proof_shape`,
and changed material cannot be acquired before confirmation. Final public DTOs
equal the native owner. Wrong source/transport selections reject before a
material prefix. A large opaque invalid body crosses unchanged, then independent
Reader admission rejects `sync_compact_value_shape`.

Reader's six and relay's five counters return to zero, source sessions/sockets
close, and the synthetic native fixture retires its scratch and Runtime threads.
The controller is trusted direct test code with private nonce setup. Separate
owner, capture/oracle, relay and Reader allocations do not establish aggregate
caps or RSS. Ordinary carrier/controller/authentication bootstrap, compact
watch/held-drain/cancellation/expired-head composition, dense capacity/recovery,
CPU, populated providers/fixed SSH and immutable installed-pair acceptance
remain open. That composition used the earlier source with its open pin-pruning finding.
This adds bounded pipeline evidence without selecting a route or promoting
artifacts.

The subsequent source retirement fix at Observer `e3441d0` / Mesh `6fce5ed0`
passes these same three compact methods and all nine scenarios on both Python
versions in RLCD's independent final-pair replay, with 73 loaded project modules
verified per run. Its [tracking defect is independently closed at bounded source scope](delta-sync-relay-addendum.md#independent-source-fix-closure).
That closure does not qualify controller execution, aggregate resources,
performance, native providers or the immutable installed pair.

## Compact owner CPU diagnostic

Observer source `f3e350772d2c3045849e3c48b60fb158943a3451` removes a redundant
freeze/thaw round trip when encoding admitted compact row values. Its shallow
adapter handles committed immutable objects; canonical sorting/Unicode/NaN
settings and the existing row/encoded reservations stay unchanged. The guide
`docs/delta-sync-compact-owner-cpu.md` has SHA-256
`93fb9ef8d4bab7020f42c644bea482bba843f57e4ca966a09386b5430c4c8f36`;
`compact-owner-cpu.json` has SHA-256
`9caa9011cb6810280ffa1f030afdd457ff5e58295e8f80b45ac462ac7b3292ca`.

RLCD verified 212 producer inputs, artifacts/logs and the saved serial ABBA
samples, then independently recomputed their statistics, component sums,
signature equality and source hashes. Compact modules are lazily imported
during measured sync work; initially loaded hashes remain stable and all final
module files match their respective before/after Git bytes. Exact 100-row cold
full/active bytes, tags, hashes and membership counts match the prior export.
No CPU benchmark was rerun. Under the shared CPU advisory lock, RLCD ran the
unchanged 17 exporter/source methods and three compact relay methods on each
Python version against immutable Mesh `6fce5ed0`: all 20 pass with GC disabled,
no errors/skips and 81/73 loaded project modules verified respectively. The
producer's 62 focused and 940 canonical results keep their saved provenance.

The compact all-body median, including the semantic oracle, falls from
742.87 to 625.34 ms at 500 rows and from 2,554.12 to 2,238.85 ms at 2,000 rows,
with separate serial old/new ABBA controls for each before/after screen.
The strict producer ceiling remains **FAIL**. Across twelve after generations,
excluding each side's separately retained oracle, old/new combined-owner CPU
totals are 2,214.209 / 7,318.117 ms at 500 rows (**+230.51%**) and
9,090.413 / 26,391.901 ms at 2,000 rows (**+190.33%**), above the +25% ceiling.
These compact screens retain their own workload/provenance and do not replace
the earlier expanded-source CPU evidence.

Fixtures contain 3,510 / 14,010 full membership cells, not nine fields on every
row. The 2,000-row runs each record five baseline fallbacks and deliver no
baseline, so they prove no recovery saving. Cold construction and instrumented
profiling are separate; profile timings are excluded from ABBA. This is partial
source progress only: delivered cold/recovery, actual IPC/publisher/Reader/SSH,
aggregate 32/64 MiB, RSS, dense capacity, installed candidate and producer
acceptance remain open. The source retirement fix is unchanged and closed;
selected a7/a23, normal workflows, schemas/IDs and rollout remain unchanged.

### Streamed transaction hashing

Observer `f7f7a55e1bbc019d2b866f7e48da85c815c2e031` combines unsigned
transaction hashing with final output construction, reducing three row walks to
two. The final unsigned closing brace is hashed before output substitutes the
canonical ID field and LF. Constructor, staged encoded and per-row reservations,
size/fragment guards and deterministic iterator retirement remain in force.
Baseline, original head/control and source APIs are unchanged. The guide
`docs/delta-sync-compact-transaction-pass.md` has SHA-256
`7d8f88ed396ff2b8c1496635bb7c6cf2064163d8af93503349963e7a61842d60`;
the 199,533-byte `compact-owner-streamed-id.json` has SHA-256
`edfa76ba4f9d3c851f6629a9de0197d2415acbcd737f7f2d92021dd2ca5dff13`.

RLCD verifies 212 producer inputs, the sole production-file change, 76 saved
comparison artifacts and all saved ABBA samples, source hashes, component sums
and semantic signatures. Under the shared CPU advisory lock, the unchanged
17 exporter/source methods and three compact relay methods pass on each Python
3.14.8/3.11.17 with GC disabled and 81/73 loaded modules verified. Four fresh
before/after captures reproduce the same 18 full/active baseline, transaction
and completion frames across both versions, with 68 imported modules verified
per capture. Exact raw bytes match both the prior source and saved producer
captures; a separate canonical raw-ID computation passes every transaction.
The producer's saved 62-case and 940-test/zero-skip checks retain their own
provenance. No CPU benchmark was rerun.

The new compact all-body medians, including the oracle, are 536.08 ms at 500
rows and 1,938.75 ms at 2,000 rows; matched a7 controls are 194.79 and 795.79 ms.
Across twelve generations per side, oracle-excluded old/new combined-owner CPU
totals are 2,205.188 / 6,259.876 ms (**+183.87%**) and
9,068.550 / 22,878.023 ms (**+152.28%**). The strict +25% ceiling remains
**FAIL**. The earlier samples remain separate. The fixture still has
3,510 / 14,010 full membership cells rather than nine fields on every row;
each 2,000-row run has five baseline fallbacks with no ensuing baseline delivery.
Cold/recovery delivery, inclusive resources/RSS, ordinary controller/native
transport and immutable installed-pair gates remain open. Joint controller
contract closure and the source retirement closure stay closed. Git attribution
cleanup remains on HOLD; no artifact/ID, selection, service/provider, sibling or
rollout action accompanies this source review.

### Bounded row-local reuse

Observer `84d284dab04b68ae0e9070335d017e85564f2ba9` adds one record memo
matched by exact side and full identity within a row, then clears it at the next
row and before scratch release. Its container prepays another 256 heap bytes.
Membership after masks use the exact committed edit bytes; removals have no
after value and edits without retained bytes keep the original lookup path.
This adds no roster cache, cross-generation reuse, API or format change.
The guide `docs/delta-sync-compact-row-reuse.md` has SHA-256
`0701b8fc4072d4c626288e37eaf21e2bf0fdeec0c8aff99cd4c06e8e8ae3b304`;
its 251,162-byte `receipt.json` has SHA-256
`346180d6bcd05960eb9140c5c63d7f4d2b50d9b5d6144b9a5c7f3b6330cfa958`.

RLCD verifies 212 before/after Observer inputs, 225 selected Mesh inputs,
128 artifacts, final ABBA samples, semantic signatures and stable source hashes.
On immutable Mesh `a482abb`, all 64 focused methods pass independently on each
Python 3.14.8/3.11.17 with GC disabled, zero failures/errors/skips and 86 loaded
project pins verified. Four fresh before-`f7f7a55`/after captures preserve all
18 full/active frames byte-for-byte on both versions, with 71 loaded pins each;
an independent raw-ID computation passes every transaction. The saved 942-test,
zero-skip and 198-Markdown gate retains its provenance. An initial root replay's
four subprocess import failures came from its empty import path; that failed
harness run is retained separately from the corrected immutable-path replay.

The fresh twelve-generation, oracle-excluded old/new owner totals are
2,310.133 / 6,134.985 ms at 500 rows (**+165.57%**) and
9,230.158 / 22,475.622 ms at 2,000 rows (**+143.50%**). Both hard +25% ceilings
remain **FAIL**. The 2,000-row runs each retain five baseline fallbacks and
deliver no recovery baseline; the workload still has 3,510/14,010 full member
cells rather than nine fields on every row. Instrumented map-entry reads fall
from 30,696 to 18,456; profiler timing is excluded from ABBA. Draft 500-row
samples and the source-edited, hash-guard-rejected 2,000-row draft remain
separate from the final frozen screens. RLCD reruns no CPU benchmark.

This clears the bounded source review only. The Mesh stamped-header copy
lifetime finding remains open, with its owning correction acknowledged;
controller/source-ref contracts stay closed. Aggregate resources/RSS, dense
delivery/recovery, populated native/fixed SSH, immutable installed-pair and
whole-producer gates remain open. Attribution cleanup stays on HOLD; selected
a7/a23, schemas/IDs, normal workflows and rollout are unchanged.

## Remaining qualification

Run the actual expanded and compact paths through strict streaming schema and
domain admission, all independent roots, expected-old masks, token-only updates,
nonempty compact-patch rejection, late malformed values, iterator/header/codec
retirement and atomic callback/root/capacity failure. Verify GC-disabled held
errors, cancellation, live input/output pins and all copied scratch under the
same shared 32 MiB encoded/64 MiB heap caps and original deadlines.

The Mesh callback material-credit fix at `66b9c1e` is independently verified
bounded source evidence. The failed dense CPU gate, deliverable 2,000-row packed
recovery, inclusive resource/RSS/plateau and matched cold/recovery CPU/bytes
remain open. Actual populated IPC/fixed SSH, immutable
installed full/active/old-route pairing and later RLCD acceptance retain the
[original gates](delta-sync-plan.md#ownership-and-execution-gates). Preserve
a7/a23, full diagnostics, Tmux, 349, writer, ordinary providers and deferred
physical checks until the appropriate gate passes.
