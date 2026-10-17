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
