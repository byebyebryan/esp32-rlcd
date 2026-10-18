# Working-set P1 client review

2026-10-18. **Exact R1+R2+R3 client contract accepted; WS-P1-1 and WS-P1-2
closed at wording/pure-helper scope.** R2 completes branch/coverage lifetimes;
R3 clarifies coverage and fixes computed-cutoff bounds. This is not integrated
producer/runtime acceptance. No view is selected here, no identifier is allocated,
and dark delta-sync remains deferred.

## Exact reviewed packet

Observer commit `995401e0a902c2f69571a731d7cd433f5bf40739`, in the isolated
`agent-observer-working-set` worktree:

| Artifact | Exact bytes |
| --- | --- |
| `docs/working-set-contract-r1.md` | 16,800 bytes; SHA-256 `4b4f55dff8308daee6aec442848a6c841c8e18b128ef4b91c01959e87aa33ec8` |
| `docs/evidence/2026-10-18-working-set/p1-review.json` | SHA-256 `84546ecfc2ee67dfde9b53202b7f8cfb5a065873bd5b7537150576c40c5a7755` |

All 17 packet artifacts and 15 declared source inputs match the immutable Git
objects. The saved 961-test canonical result was verified, not rerun. Candidate
native/profile identifiers remain unallocated and unfrozen.

The announced R2 supplement is Observer
`58b04ac478edcfb47ab1695199f7db728d5a1238`:

| Artifact | Exact bytes |
| --- | --- |
| `docs/working-set-contract-r2.md` | 6,604 bytes; SHA-256 `937d442402064a4e43258412d12e906fd5ca98b7fe0244c45f9ac1699884ccea` |
| `docs/evidence/2026-10-18-working-set/p1-r2-review.json` | SHA-256 `eed4a58e1b9a3ed25012d0a0ba54ad512ea4b6867a6a50b74629de1522a76224` |

All ten R2 manifest artifacts match immutable Git objects. Source, tests and
`pyproject.toml` are byte-unchanged from R1. Original R1 bytes and the initial
review at RLCD `26c0c48749e5f6f7658dc2177d5c1ae6cbed5c2f` remain provenance.

The owning correction is Observer
`645688f80eec90fb1a1e8df8ac127c5f458b88c8`:

| Artifact | Exact bytes |
| --- | --- |
| `docs/working-set-contract-r3.md` | 3,981 bytes; SHA-256 `65815ad9997d00d8fc6c34fa56c9e920df9f13a13a25ff9b1a3e303ce8d7c797` |
| `agent_observer/working_set_policy.py` | SHA-256 `1af48f051e4bbddc19ca24b7b4cb891431571c63ff8584b283b0b8b8b2b66519` |
| `docs/evidence/2026-10-18-working-set/client-correction/receipt.json` | 8,004 bytes; SHA-256 `bc344073ad8c81339f534189cff4e1f9e1ec50adc9c0a9a1455da902628195b0` |

All 29 correction artifacts match immutable Git objects. R1/R2, the original
client diagnostic, and both preceding root reviews are byte-preserved. Only
`working_set_policy.py` changes within the producer source package.

## R2 completion and exact client signoff

The service-level scalar `K=max(W-L+1)` is a conservative replacement for
per-identity positive-cutoff history: `T+Q-K` equals the minimum of all accepted
candidate lower cutoffs for fixed T/Q. K is nondecreasing within its clock
incarnation and survives roster, capacity, namespace and provider-context
changes. Only a new service/boot/time-domain baseline resets it. Dhi remains
the exact current bracket's upper cutoff and is never inferred from K.

The bounded last-T guard and explicit `recent_tracking_capacity` latch prevent
same-scope eviction from silently re-arming recency. Existing independent active
membership may continue under its own limits. Missing guards or clock evidence
cannot manufacture a negative. These are accepted requirements, not evidence of
an implemented cache, capacity recovery or timer.

For current eligible rows, use the maximum of each available branch's minimum
support horizon, capped by eligibility. Flattening both alternatives into one
minimum incorrectly expires the union with its shorter branch. These horizons
govern current positive claims and establish no presentation timeout.

R2 explicitly requires complete coverage to become partial/unresolved when a
member's sole positive branch expires without a separately admitted current
negative. Checking the census alone and filtering the row from a still-complete
scope would create false absence authority. A live active alternative can still
select a row after recent expiry. Conservative earlier loss of complete scope
is also permitted; it does not erase that independent active claim. All required
negative and census supports remain currentness dependencies, including for
complete-empty. Delayed quiet replacements cannot bypass the facade's checks.

These explicit union/coverage rules resolved the semantic concern in WS-P1-1
at the R2 review. R3 now replaces the original blanket unknown-age sentence
explicitly. No remaining client contract conflict is identified in the exact
R1+R2+R3 tuple. Mesh's public SDK/profile review and source implementation gates
remain their existing owning assignments.

## R3 correction closure

R3 adopts decision-dependent membership coverage: unknown recent age does not
make an independently proved active row unresolved. The age field itself stays
unknown. Exhaustive census, all other required selection supports and R2's
sole-positive expiry downgrade remain required. WS-P1-1 is closed.

The helper checks both computed deadlines against the inclusive signed-safe
range before returning a time decision. If either is out of range, the result
is unknown with reason `cutoff_out_of_range` and both bounds absent. It neither
clamps nor preserves a usable sibling bound. Zero-window and valid signed
negative cutoffs remain unchanged; independent active membership still wins.
WS-P1-2 is closed at preparatory-helper scope.

Independent execution of the unchanged owning runners on Python 3.14.8 and
3.11.17 reproduces exactly two overflow failures and 13 passes on immutable
58b04ac with only the final test file overlaid. Exact 645688f passes all 15
tests per version, with GC disabled and zero errors/skips. The named original
counterexample separately changes from true/out-of-range to unknown/no bounds
on each version; its independent active result remains selected. Every loaded
source/test/runner entry matches its exact Git object. Before policy/range
runs contain four/three entries; after runs contain five/four, including their
owning runner inside the final export.

Private correction evidence is repository-root
`.cache/observer-working-set-20261018/client-correction-645688f/review.json`,
SHA-256 `7a1a98537c0c61799b3163bf597363b62c1293ace297abf9028a5c0ab3b19d0d`.
The saved 964-test canonical result was verified, not rerun. Unchanged R1/R2
arithmetic, actual clock/cache/timer/native/profile behavior and producer gates
were not replayed or qualified by this correction review.

## Compatible client semantics

- Selection is independently supported `E AND (A OR R)`: current running,
  including waiting/blocked, survives unknown recent activity; proved recent
  activity can select a parked or runtime-unknown row. Recent membership grants
  no runtime or action authority. Default recency is 72 hours; zero disables it.
- The `L/W/U` source bracket and one-millisecond flooring allowances preserve a
  conservative unknown interval. Same-event positive cutoffs cannot renew on
  heartbeat, proof, reconnect or repeated observation. Older events and detected
  clock discontinuity supply no new recent or outside-window authority.
- Positive expiry yields unresolved retained context. Removal requires a current
  proved negative or a current exhaustive accepted replacement whose coverage
  establishes the selection decision. There is no added context timeout.
- Quiet `Dlo`/`Dhi` transitions publish replacements and advance projection
  revision while observation revision remains unchanged. No-op reads and proofs
  renew neither supports nor revisions. Partial reconnect omission cannot retire
  prior presentation context.
- Complete scope requires the exhaustive current saved-plus-loaded identity
  union and the supports needed to decide every identity. Loaded-only census,
  aggregate activity flags and skipped/failed activity reads cannot establish
  recent-history absence. The proposed `no_native_turn` exception must join the
  exact same accepted row/sample and current latest-turn support.
- Full history remains an explicit rare read. There is no full fallback, top-N
  truncation or implicit consumer migration. Keep the proposed 4,096-identity,
  1 MiB combined-ledger and 32-receipt bounds, frame limits, and inclusive costs
  for simultaneous caches, generations, clocks, pins and copies. P0 body counts
  are a sizing screen; proposed CPU/byte gates still require measurement.

Mesh's existing same-byte review owns confirmation that positive attenuation
`H - max(0, E - Dlo)` uses the exact original receipt expiry and its current
translated receipt under matching context/accepted bindings. This formula can
only shorten positive authority. It cannot translate `Dhi` into an early negative
time proof. No additional Mesh review request is created here.

The existing displayed-age contract remains source-sampled
`runtime.observedAt - activity.at` under its current/sample support. A new
membership clock does not implicitly change that UI field or its authority.

## Initial R1 corrections and current disposition

**WS-P1-1 — closed by R2 semantics and R3 explicit wording.** R1 lines 173–180
require a proved decision for every identity, then say
“Unknown age is partial.” The initial review flagged the missing distinction
between selected membership and coverage availability. Eligible active rows with
unknown age remain selected. A current exhaustive scope may prove all membership
decisions even when one selected row's age remains unavailable; R2 also permits
conservative partial coverage without dropping that member. Excluded-kind rows
and a disabled recent branch need no activity proof.

R3's accepted replacement: “Unknown activity makes affected membership coverage
partial when the selection decision cannot otherwise be proved. Independently
proved active membership remains selected; unavailable activity and age fields
remain unknown.” Preserve exhaustive census and all required current supports.

**WS-P1-2 — closed on 645688f at preparatory-helper scope.** R1 lines 94–98
require out-of-range cutoff arithmetic to make recent unknown. Before the fix,
exact 58b04ac `recent_activity()` returned `True`/`recent` with cutoffs beyond
the signed safe-integer envelope. Both Python versions reproduce this input:

| Input/result | Value |
| --- | ---: |
| Maximum allowed cutoff | 9,007,199,254,740,991 |
| L / U / now | 9,007,199,254,730,991 / 9,007,199,254,731,001 / 9,007,199,254,731,091 |
| Current original receipt expiry | 9,007,199,254,740,990 |
| W / activity T / Q | 1,700,000,000,000 / 1,699,999,999,000 / 259,200,000 |
| Before Dlo / Dhi | 9,007,199,513,929,990 / 9,007,199,513,930,002 |

All input integers are within the safe-integer bound; sample, support, service,
boot and context joins match. Expected outcome is unknown with no usable
out-of-range cutoff. This is preparatory-model conformance, not an integrated
runtime failure or producer qualification result.

The R2 review kept the helper correction open; R3 now closes that existing
request without a new assignment or general permission gate. Original R1 and
failed-vector evidence remain preserved. The separate contract, helper and
future integrated-runtime acceptance boundaries remain explicit.

## Verification and remaining scope

On Python 3.14.8 and 3.11.17, in an immutable export under the shared advisory
lock, all 12 unchanged helper tests pass with GC disabled. The unchanged stdlib
oracle passes 11,804 floored capture checks and 410 positive translations.
Separately authored client vectors verify all 27 selection combinations,
44,380 flooring checks and 960 positive translations across different clock
offsets, and reproduce WS-P1-2. The three project modules loaded by those vectors
match exact Git blobs. Dual-version vector results agree apart from the version.

Private reproducible evidence is retained at repository-root
`.cache/observer-working-set-20261018/p1-995401e/review.json`, SHA-256
`15f926c1cb4869713bd651aebce3c5e44241495ffd070e88fb0489cc9acd3d0c`,
with the immutable export, input pins, scripts and raw logs.

The R2 review separately replays all 16 unchanged upstream named models on
Python 3.14.8 and 3.11.17; output exactly matches the pinned producer JSON.
New independent finite models pass 1,024 scalar-prefix checks, 16,384 exact
candidate-minimum checks, 5,200 union-horizon checks and 3,564 coverage-expiry
checks on each version. The WS-P1-2 range counterexample separately reproduces
on exact R2 source; its three loaded project modules match Git blobs. All model
and counterexample outputs are byte-equal between Python versions. These are
finite equations/decisions, not actual cache, receipt, capacity or GC qualification.
Unchanged helper suites and the full canonical suite were not rerun for R2.

The separate private R2 evidence is repository-root
`.cache/observer-working-set-20261018/p1-r2-58b04ac/review.json`, SHA-256
`84253f07957d6a7efcdbf1a4440d22e4915a62ea112c23fffe78a5fac267f835`,
with immutable export, scripts, raw outputs and pins. Runs were serialized under
the shared advisory lock. The saved R2 961-test result was read/hash-verified.

Future stateful vectors must cover same-event ceilings through quiet loss,
re-entry and reconnect; older events and wall changes; independent active support
with unknown recent evidence; separate quiet/observation revisions; exact absence
joins; and refusal without removal authority. Native schema/profile/runtime,
resource/CPU/native transport and paired installed/client adoption gates remain
open. No live native collection, device change or historical delta test replay
was performed for this review.
