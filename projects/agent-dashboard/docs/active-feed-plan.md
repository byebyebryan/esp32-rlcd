# Active-session feed coordination plan

Status: G0 planning agreement reached by RLCD, Mesh Plus and Agent Observer,
2026-10-16 UTC. G1 execution is now authorized: owning producers implement and
independently qualify the agreed seams, followed by gated RLCD integration and
operational validation here. Exact future schemas, artifacts and operational
selection still require their stated acceptance gates.

## Problem and desired behavior

The accepted [owned-admission client](../../../docs/evidence/2026-10-15-owned-admission/REPORT.md)
selects rows after receiving the full Observer roster through Mesh. It reduces
repeated local admission and decoding but preserves acquisition bytes.

A subsequent read-only investigation observed 498 current identities and ten
selected agents. Its separate 60-second timed reader received 9,798,780 bytes
and sent 67,110 device bytes. Aggregate composition/admission used 57.5% of
that reader's Python CPU; visible-row projection used 0.2%. A 35-second audit
found 40 native validations of 14 distinct native frame contents. These are
dated diagnostic observations, not stable fleet counts or a promised saving.
Private counters and reproducible scripts are retained under
`.cache/cpu-investigation/20261016T042557Z/` at the repository root.

The target is an opt-in projected feed produced before the consumer IPC/SSH
stream. Mesh transport and RLCD processing should follow the number of loaded
eligible agents, rather than the size of saved/inactive history. The ordinary
full inventory remains available to other consumers and explicit diagnostics.
Producer projection and collection costs must be measured separately, so a
cheaper RLCD process does not conceal work moved into the publisher.

## Contract decisions to settle first

1. **Selection.** Observer supplies provider-neutral runtime and kind semantics.
   RLCD requests Codex, user/unknown kind, and currently running runtime, as
   today. Running includes idle/waiting, blocked and errored loaded threads;
   work phase is not an active-membership predicate. Confirmed child/system
   records and positively parked history do not need full bodies in this feed.
2. **Origin.** Establish the projected view at an Observer-owned cached service
   or source boundary, before consumer transport. Choose the narrowest supported
   boundary jointly; keep Observer core/local service free of Mesh imports.
   Project/cache once per accepted owner generation where possible, rather
   than once per subscriber or proof request. Do not add native collection for
   each subscriber, or embed the full original roster inside projected replies.
3. **Completeness and uncertainty.** Distinguish complete-empty, partial,
   unavailable, stale and warming projected views. A row disappearing from a
   selected list is not automatically positive parked evidence. Unknown runtime
   and incomplete native reads must preserve bounded prior context. Observer
   must propose how compact uncertainty/nonmembership facts or declared
   projection completeness make retirement decidable without sending the full
   inactive identity list on every update. Absence from a native loaded list
   alone must not create a parked fact.
4. **Replacement model.** Prefer complete filtered replacement snapshots first:
   small active sets make baseline/reconnect simple. Choose whether compact
   removal facts are additionally needed for partial coverage. A complete
   filtered snapshot may retire absent prior rows only under explicitly proved
   coverage and selection semantics. Do not add deltas/replay in the first pass.
5. **Binding and proof.** Bind the exact projection/selector and its version to
   the negotiated source/profile, payload digest, request, host/provider scope,
   owner incarnation and component receipts. Source evidence retains original
   leases and activity clocks. Reader expiry still uses the original remote
   nonce, whole RTT and safety margin; heartbeats grant no new authority.
6. **Compatibility.** Producers choose the minimal explicit version/capability
   changes after inventory and review. Do not change frozen v3 row meaning or
   packaged schema bytes in place. An unsupported active feed fails explicitly;
   the operator may deliberately select the retained full-feed tuple for
   rollback. There is no silent downgrade to expensive full acquisition.

These decisions are review questions, not assigned new API field names.

## Observer's initial G0 source findings

Observer reports that current Service 4 runtime coverage is `daemon_threads`.
Codex marks it complete only after both loaded and saved censuses finish with
no unresolved statuses. Preserve that conservative completeness; a loaded-only
feed cannot acquire retirement authority merely by omitting saved records.

The proposed placement is a Mesh-free pure projection/cache hosted by
`ServiceState`, before local service IPC and therefore before Mesh IPC/SSH.
Observer's networking component would expose an optional projected source and
profile. This needs a new opt-in projected local wire, rather than relabeling
Service 4/profile v3 snapshots. Ordinary full inventory and native collection
cadence remain unchanged. The first projection may still scan a full admitted
generation once; its amortized producer cost belongs in the acceptance report.

The proposal carries bounded recent-member uncertainty and positive nonmember
facts instead of the entire inactive identity list. G0 must specify retention
limits, overflow/eviction behavior, original receipt dependencies and partial
baseline/reconnect behavior. Expiry or eviction of bookkeeping alone must not
become positive parked/removal evidence. Exact local-wire, profile, proof and
version bindings remain under joint producer review.

## Observer draft review and coordinator position

The full Observer draft is `agent-observer/docs/active-feed-proposal.md`.
Both producer drafts agree on placement, selector binding and the full projected
replacement/proof baseline. The following are agreed G0 implementation targets,
not runtime or package acceptance:

- Preserve existing RLCD context retention for this feed migration. Positive
  facts expire under original leases; previous rows can remain visibly uncertain
  afterward until valid membership authority resolves them. Do not introduce a
  finite age-based context timeout as a prerequisite for the new producer wire.
  Any later timeout is an explicit presentation refinement. Partial reconnect
  and missed expired negatives can leave context unresolved without requesting
  all inactive identities. This conservative unresolved outcome is accepted for
  first-pass planning; exact eventual retirement through arbitrary partial
  outages is not promised. A new prior-identity reconciliation query is deferred,
  not a G0 prerequisite or an assumed capability. Fresh complete authority or
  current exact decisions from the agreed feed can later resolve prior context.
- Use 4,096 identities and 1 MiB canonical whole-ledger metadata as the G0
  tracking ceilings, including active/recent identities, all support references
  and ordering watermarks. Full row bodies and total frames have separate
  existing size ceilings; runtime resident and pinned-generation memory also
  need bounded implementation evidence. Overflow fails only the affected
  provider/namespace, uses reserved failure metadata and changes that scope's
  continuity token without sibling eviction. These are implementation targets,
  not measured or deployed capacity acceptance. Original horizons never slide with cache
  reads, uncertainty, generation changes or reconnect. Unknown and negative
  facts have their own original dependencies; pruning/overflow grants no
  retirement authority. Expired negative facts cannot be replayed as current.
- Observer has chosen transient per-field support references captured at actual
  component acceptance: provider/namespace/context/component/accepted/sample/
  expiry, bound to service incarnation. Reconciliation copies the actual chosen
  runtime/history kind support; retention never rebinds it. Complete scope uses
  the original complete daemon census and internal census set plus all actual
  classification/positive-saved-identity supports, conservatively bounded by
  runtime/history per source. Missing support yields uncertainty/partial.
  Activity/outcome support is also captured at acceptance and copied with the
  chosen value. A stale/missing actual producing dependency makes the value
  last-known; retention never constructs a new still-live-only dependency set.
- Both drafts now choose selected bodies in `NativeState.records` and typed
  domain claim metadata in the projected owner header. Observer's facade checks
  every claim on every read against public translated host receipts, original
  binding, ready delivery, reader clock, selector and scope continuity. This
  includes complete-empty scopes; raw `context()` grants no current authority.
  Observer pins body access to one public `snapshot()` export per replacement,
  retaining only admitted selected bodies and support metadata. Reads use public
  `current(now_ms, clock)` first, then `context()` for clock/generation and translated
  receipts, with independent field/claim masking even if generic whole-row
  eligibility rejects a body. Mesh has confirmed this public seam, including
  zero-body complete-empty views. No private guard state or new generic expiry
  API is required. A changed original accepted/sample/expiry/context reference
  is context-only; it cannot bind to a newer receipt under the same key. The
  existing 32-receipt per-host bound stays in force: do not create an historical
  receipt bank per tracked identity or truncate required dependencies.
- The proposed `active-feed/1` local wire and distinct active Mesh profile names
  remain review names. ServiceState hosting requires a new Observer service
  artifact and later collector/service adoption, in addition to publisher/read
  and consumer changes. The current client-only a6/a22 adoption cannot enable
  the proposed local endpoint on an older service.

## Ownership and deliverables

| Owner | Responsibility | First deliverable |
| --- | --- | --- |
| Agent Observer | Meaning of the projected roster; current/uncertain/nonmember facts; coverage and removal semantics; producer-side cached projection; pure validation/profile and supported read facade | Domain contract proposal, exact source boundary, schema/version requirements, lifecycle examples and independent acceptance plan |
| Mesh Plus | Generic negotiation/routing, projected payload delivery, digest and proof binding, scope/expiry/gap/reconnect; installed SDK support; acquisition byte accounting | Transport/profile compatibility proposal coordinated with Observer, proof/ownership boundaries and independent acceptance plan |
| RLCD (this repository) | Consumer requirements and cross-producer reconciliation; later Fleet/Projector adoption, explicit diagnostics, matched benchmarks, installed/feed/device checks and paired rollback | This plan, an agreed lifecycle matrix, integration prerequisites and measurable acceptance criteria |

### G1 execution split

- **Observer:** implement transient actual-value support and census provenance;
  the pure fixed-selector projection/ledger and projected local wire; ServiceState
  cache and opt-in service delivery; optional projected source/profile/codec and
  pure active-read facade. Keep core Mesh-free and ordinary full inventory
  unchanged. Coordinate concrete schema/descriptor bindings with Mesh before
  dependent edits. Own Observer source, schema, installed, bounded native,
  per-field/empty/partial/overflow and publisher/service acceptance evidence.
- **Mesh:** implement the reviewed new-profile/native-schema addendum and lock
  checkpoint, strict profile/source admission and supported delivery seams.
  Coordinate the generic factory interface with Observer, which owns its Agent
  factory/source implementation. Qualify the public snapshot/current/context
  path, full projected proofs and old full-feed/Tmux compatibility. Independently
  qualify the existing library catalog path, keeping fresh checks and writer
  ownership. Own Mesh source, schemas, installed transport/SDK/conformance and
  bounded native/performance evidence.
- **RLCD:** prepare an exact old-tuple rollback/baseline and reproducible fixture/
  cost harness while producers work. Do not implement speculative consumer APIs.
  After both immutable producer artifacts and supported APIs are accepted, adopt
  the active facade and qualified catalog choice, prove semantic and scaling
  parity, then perform scoped service/device/rollback integration here.

Producers may create isolated branches, commit their reviewed changes, allocate
fresh reconciled artifact versions and run owned acceptance fixtures. They are
not alone in these repositories: preserve concurrent work, retain previously
accepted artifacts, and never revert another owner's changes. Source/wheel
readiness does not select normal collector/publisher/services. RLCD owns later
coordinated deployment configuration and operational gates.

Before readiness, each producer returns exact source/evidence revisions, branch,
immutable wheel paths/SHA-256, dependencies, interface/schema/lock descriptors,
installed gates and explicit coverage limits, performance scope, cleanup and
consumer adoption requirements. Freeze interfaces and artifacts without silently
changing previously handed-off bytes. Qualify each other's exact artifacts;
development-source screens do not replace installed-wheel acceptance.

Observer owns edits in `agent-observer`; Mesh owns edits in `mesh-plus`; this
thread owns `esp32-rlcd` and later scoped RLCD deployment configuration. All
owners preserve concurrent work and adjust to agreed producer interfaces.
Shared deployment/launcher changes require explicit coordination, especially
the independently selected Tmux domain. No owner edits a sibling repository as
part of its producer checkpoint.

The Mesh planning brief also includes a separate catalog-cost lane. Current
authority monitoring starts the catalog CLI on a five-second idle cadence. Twelve isolated
calls averaged 44.97 ms child CPU, about 0.90% of one core at that cadence; the
live 120-second window accounted for 0.93% in reaped children. Preserve the
existing idle check cadence and five-second check budget; this does not promise
unconditional end-to-end change detection within five seconds under stalls.
Investigate a supported cheaper check while retaining Host Mesh ownership. This
lane must not hold up the projected-feed contract or weaken authority checks.
Mesh's reviewed G0 draft first proposes qualifying the existing opt-in
`LibraryMeshAuthority` with `report_routes=False` and owned close, using a full
fresh load on each check. Qualify actual selected SSH Plus/library semantics,
canonical inputs, locks, permissions, cancellation and cleanup before adoption.
Route-report writes remain outside this read lane; library reads can still have
lock/permission effects. A persistent service and revision-only caching are not
the initial proposal. Suitability remains a producer acceptance question.

Further whole-roster validator tuning, identity-token caching and compact
digest proofs are secondary lanes. Mesh confirmed that lock 4 explicitly
excludes digest-proof. Generic Lifecycle syntax/capability checks and reserved
schemas do not establish accepted native adapter support. Projected full replies
are the baseline; any compact digest-proof path needs a separate contract and
native acceptance review.

## Lifecycle matrix required from the producer agreement

| Case | Required consumer result |
| --- | --- |
| Loaded idle, working, blocked or capacity-error thread | Retain its running membership; preserve independent phase/outcome uncertainty |
| Running to positively parked or confirmed excluded kind | Retire the exact prior row using valid projection/nonmembership authority |
| Running to unknown or failed source read | Retain bounded uncertain context; do not declare parked or complete-empty |
| Original positive lease expires or recent-member bookkeeping is evicted | Revoke positive authority; neither event alone proves retirement. Agree context retention separately |
| Complete and authoritative empty active view | Clear prior active rows for that covered scope |
| One host/provider partial, unavailable or expired | Affect only its dependent claims; preserve healthy siblings |
| A prior visible row lies beyond a display prefix | Correctly retire or retain it before applying USB32/display limits |
| Same native ID on another host/provider/namespace | Keep identities distinct using the full five-part reference |
| Silence, heartbeat, suspend or clock change | Never extend source evidence; expire/revoke according to the accepted clock rules |
| Gap, publisher restart, reconnect or late old proof | Revoke affected authority, reject old epochs and require a proved replacement baseline |
| Unsupported selector/profile/capability | Bounded explicit incompatibility; no implicit full-roster fallback |

Current RLCD retains previous rows as uncertain context after positive leases
expire. Mesh has corrected its draft to separate positive-fact expiry,
negative/completeness evidence lifetime and presentation-context lifetime.
Neither expiry nor pruning reverses an already valid retirement or grants a
new retirement decision. On partial reconnect, a missed or expired negative
can leave retained context uncertain until fresh authority resolves it. That
limitation is the selected first-pass behavior, rather than a requirement for
a new reconciliation RPC or context timeout. A later context timeout would be
a presentation policy decision, not a producer-derived parked fact.

## Sequence and acceptance gates

**G0 — Planning review.** Both peers return proposals and unresolved decisions.
RLCD reconciles selection, uncertainty/removal, source placement, negotiated
binding, versions and the lifecycle matrix. Review any normative Mesh change
explicitly. G0 is agreed and G1 is authorized under the execution split above.
The selected route is a distinct opt-in active native contract/profile with a
fixed canonical selector, full projected nonce replies, and unchanged existing
full-feed bytes. SDK 1, Mesh Read 1 and Delivery 1 remain the target, subject to
explicit new-profile addendum/schema-lock review. Planning agreement does not
certify the future schemas, artifacts or implementation.

**G1 — Independent producer implementation, when requested.** Observer and Mesh
implement the agreed seams in their own repositories. Agree interfaces before
parallel edits. Use exact accepted wheels for dependency qualification, fresh
artifact allocations and immutable hashes. Preserve strict validation for
public mutable/raw entry points and independently check dynamic proof/lease
facts. Each producer supplies source, installed-package, correctness, bounded
native and performance evidence; source readiness does not select services.

**G2 — RLCD adoption.** Begin consumer edits only after both exact producer
artifacts and supported interfaces are ready. Replace full-roster membership
bookkeeping with the accepted projected membership semantics. Preserve sorting,
names, host badges, activity ages, retry/error display, partial retention and
the one-second device request cadence. Keep explicit full-roster diagnostics.
Use matched old/new fixtures and compare complete semantic results before
display truncation as well as final device frames.

**G3 — Measured acceptance.** Hold the active set fixed and vary dormant history
(for example 100/500/2,000 records, also respecting encoded-byte bounds). The
existing full snapshot admits at most 4,096 rows per host. A 5,000-row single-host
fixture is a capacity/partial test; a 5,000-row multi-host aggregate is optional
only after verifying each host and enclosing Mesh bounds. IPC/SSH bytes and
RLCD work must remain effectively independent of dormant history; explain any
remaining dependence. Exercise zero/one/many active records, uncertainty,
membership churn, child/system exclusions and multi-host failure. Measure
collector, publisher, catalog children and RLCD scopes separately, with matched
work, serial ABBA trials and no profiler during CPU acceptance windows. Record
absolute CPU, bytes, memory, response latency, semantic parity and cleanup.
No fixed CPU target is accepted before the candidate is measured.

**G4 — Operational integration, separately scoped.** Qualify projected local
IPC and fixed SSH sources with original proofs/leases, then the installed
launcher/feed and actual device acknowledgements. Exercise the paired old/new
collector/service, publisher/read, Mesh and client selections during rollback
and healthy reselection; do not roll
back just one producer incompatibly. Verify protected services and exclusive
port ownership. Preserve the healthy deployed a6/a22 tuple until these gates.
Manual panel/readability and reboot checks remain explicitly deferred.

Execution authorizes no provider/session actions, daemon repair, archival/hiding
policy, firmware change, ESP32-349 rollout or Tmux change. Producers do not
select production roles. RLCD's later coordinated collector/service, publisher,
Mesh and consumer selection follows the exact accepted tuple and G2-G4 gates;
preserve the current healthy tuple until then.

## Coordination status

Initial draft prepared. Planning briefs were sent once to the verified existing
Mesh Plus and Agent Observer threads through native task messaging. Both sends
returned successfully. Mesh acknowledged G0-only scope, reported a clean CPU
branch and confirmed no implementation/version/install/rollout work is planned.
Mesh's draft `mesh-plus/docs/active-feed-g0-proposal.md` is now reviewable and
has been read here. It proposes a fixed canonical selector with separate
projected source/profile/native DTO, complete projected replies, and selector,
coverage and original receipts inside the payload digest. Its final reported
canonical checks pass on Python 3.14.8: lock 29/package 22, design 116,
delivery 169 and core 165 with zero skips, plus lint. Mesh explicitly ran no
native, WSS, sibling-source, installed-package or live acceptance for G0.
These are planning/baseline checks, not projected-feed implementation acceptance.
Observer's revised `agent-observer/docs/active-feed-proposal.md` has been read
here. Concrete kind/complete-scope provenance, exact ledger accounting and
per-scope failure/reset rules are now specified, and both drafts select the
metadata/facade representation. Observer reports 434 synthetic tests with 43
expected optional-dependency skips and 163 Markdown/link/fence checks in its
Mesh-free planning environment; no implementation gates were claimed. Observer
has now resolved the activity/outcome support and public snapshot body-access
review points in its draft. Mesh has explicitly confirmed the public
current-before-context read seam, exact-support matching, zero-body expiry,
provenance/ledger rules, and distinct projected native/profile route with full
proofs. Observer independently read Mesh's revision, adopted the explicit read
order and receipt-map bound, and returned planning acceptance. RLCD has reviewed
both updated documents and closes G0 on those choices. Producer documentation
commit/check receipts remain separate evidence; no implementation gates are
implied. Future normative schemas/addendum/lock and implementation acceptance
remain G1 gates. The G0-only reply watches were retired after recording agreement.
The subsequent execution request opens the G1 split above and new producer
readiness follow-ups; it does not renew the cancelled G0 watch intent.

G1 implementation briefs were sent once to both verified existing producer
threads. New implementation-readiness follow-ups are registered; send success
is distinct from accepted scope and artifact readiness. RLCD work is isolated
on `active-feed-integration-20261016`. The selected a6/a22 bundle, all installed
package files and protected service incarnations were captured unchanged in
the private `.cache/active-feed-integration/20261016T052335Z/` baseline. Owned
synthetic scaling screens and an eleven-case G0 consumer acceptance matrix are
being prepared there while the producer artifacts are developed. No candidate
consumer API or production selection has been introduced.

## G1 accepted; RLCD G2 integration

Both producer handoffs accept Observer `0.7.0a7` runtime `7807160` and Mesh
`0.1.0a23` runtime `1978805`. Their immutable wheel SHA-256 values are
`5eafd4c126fb31a0574c3c0500998084c6ccc8d4d813df1805e6d21ce4b85bb0` and
`73455186e187198c8e44b6ae6c381926809931a176f17614864141c62ff850c2`.
Observer acceptance evidence is `b0cea487`; Mesh acceptance evidence is `b0d78604`.
The accepted APIs are active read 1, SDK/preparation/admission 1 and lock 5, with
full API 4, Service 4 and full read 2 retained for diagnostics.

RLCD uses source `agent_active`, profile `agent-observer.mesh-active.v1`, and
local bridge `mesh-plus-agent-active/read.sock`. `--roster` continues to use the
original `agent` source/full profile. The projector reconciles exact provider and
namespace completeness and currently proved nonmembers before its 32-row device
limit. Partial omissions, expired positives, missed negatives and scope changes
retain prior presentation context without positive phase/age/freshness.
Independent history expiry masks its fields without discarding supported runtime
membership. The catalog uses owned `LibraryMeshAuthority`, fresh checks,
`report_routes=False`, and explicit close; cadence and budgets remain unchanged.

The active DTO has no full snapshot `collectedAt`. Activity age therefore uses
the member's original current `runtime.observedAt` with `clock=sample`, only when
current `activity.at` is no later than that observation. This is age at the row's
runtime observation, rather than at snapshot publication. Otherwise age is
unknown. Cached reads, proof emission, delivery and device clocks never advance
the anchor or renew evidence. This supported per-row anchor was confirmed by
Observer during adoption.

Installed consumer checks cover nominal full-feed parity and diagnostic retention,
complete-empty independent expiry, partial reconnect/missed negatives, expired
activity with continuing runtime, same-key support rejection, exact nonmember
removal beyond the display cap, namespace/host isolation, heartbeat/gap/clock
revocation and owned reconnect/catalog cleanup. Controlled cost and operational
selection remain subsequent gates; this implementation entry is not a live
acceptance claim. Producer transport savings exclude collection/generation;
Observer separately reports increased generation and unchanged full-path cost.
The later whole-stack comparison must retain those costs and their bounds.
