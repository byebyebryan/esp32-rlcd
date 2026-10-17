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

This is bounded synthetic source integration. Actual compact native serializer,
journal and source dispatch, schema/encoding freeze, inclusive memory/RSS,
dense/cold/recovery CPU/bytes, deliverable 2,000-row recovery and populated
IPC/fixed-SSH/immutable installed-pair acceptance remain open. The separate
source pin-tracking finding remains open; the later relay deadline correction
is [independently closed at source scope](delta-sync-relay-addendum.md#relay-deadline-and-failed-intake-correction).
This codec checkpoint changes neither path. Current a7/a23 and protected routes
stay selected.

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
