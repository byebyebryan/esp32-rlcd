# Owned admission and selected dashboard reads

This host-only application checkpoint adopts the independently accepted Observer
a6 and Mesh a22 artifacts. It preserves API 4/read wire 6/Service 4/Agent v3 and
device wire 2. Firmware, source cadence, receipt lifetimes and presentation policy
remain unchanged. Source and controlled acceptance pass; managed service/device
acceptance follows this source checkpoint.

## Producer and package inputs

The [producer handoffs](producers.json) bind Observer runtime `fefa52d` / evidence
`0539420` and Mesh runtime `f1ced05` / evidence `f773154` to exact private wheels:

| Package | Version | Wheel SHA256 |
| --- | --- | --- |
| Agent Observer | 0.7.0a6 | `e01a712934a1c13aaf5dca011321ce62e9cadd6abf2d4b89bd263f57a56e8125` |
| Mesh Plus | 0.1.0a22 | `5ac484d7dcb3f60665a66b5b6dcff780a967afa1d24a8c092800a430399f3314` |

The application gets its own Python 3.14.8 environment at
`~/.local/share/rlcd-agent-dashboard-python/a6-a22-e01a7129-5ac484d7`.
[Installed-byte comparison](installed-artifacts.json) matches all 55 Observer and
64 Mesh package files to those wheels. Dependencies retain the baseline versions.
No collector, normal reader/publisher, Tmux, historical writer or 349 selection is
changed. Read interface 2 and preparation/admission/selection interfaces 1 are
verified alongside the pinned package tuple; Mesh lock 4 and wire schemas remain.

Native producer acceptance is bounded: Starship has 395 independently matched
native identities. Snap's existing native daemon, selected a5 baseline and a6
candidate all return empty; Snap supplies empty-source/transport acceptance,
not populated classification proof. Cached Starship thread-update timestamps
lag contemporaneous native samples by 9–26 seconds on changing rows. The supported
activity and original receipt semantics remain; no phase-entry clock is inferred.

## Application behavior and correctness

Reader and prepared helper share the same AgentProfile instance. The application
uses `execute_admitted` and Observer's explicit AgentSelection for current running
Codex user/unknown-kind records. Device requests materialize those full bodies,
plus complete current identity/kind/runtime summaries for membership and positive
child/system/parked exclusions. Exclusions beyond the 32-row transport prefix
remain effective; absence or rejection alone cannot retire uncertain membership.
Both bodies and summaries retain their independent original leases.

The `--roster` diagnostic explicitly retains full current bodies, names and
exclusion reasons, including `--all`. Normal requests use selected reads. Raw
admission and Client validation remain strict. Acquisition still makes fresh
correlated full replies under the frozen contract; watch-body reuse is deferred.

All 54 installed application tests pass without skips, including the ASan/UBSan
C wire-admission harness. Seven optional installed-contract cases cover strict
raw/owned parity, mutation, partial/complete membership, independently expiring
history/runtime receipts, gaps/resync, clock failures, reconnect cleanup and full
diagnostics. Rows beyond the prefix with unknown/unavailable runtime retain only
uncertain context; positive exclusions retire it. The stdlib-only gate passes
with seven explicit optional skips. Frame checks cover 120,000 pixels; motion
checks cover 4,488 packed rectangles and the unchanged presentation behavior.

## Controlled pipeline comparison

The [six serial trials](controlled-cost.json) run fresh processes in A,B,C,C,B,A
order, with five seconds of warm-up and 30 measured seconds each. All use two
owned synthetic publishers with 250 records each, the production Fleet,
projection and serial supervisor, and one-second fake-device requests.

| Application and dependency tuple | Mean CPU percent of one core |
| --- | ---: |
| Existing bundle 807e / a5 + a20 | 10.34 |
| Existing bundle 807e / a6 + a22 | 9.65 |
| Selected/admitted client / a6 + a22 | 7.53 |

Combined CPU reduction is 27.25%; client adoption saves 22.04% relative to the
old client on the new dependencies. Every trial has identical wire semantics
and complete admitted/excluded identity signatures, six cached fixture reads,
matching request/response counts, zero late replies and complete cleanup.
Candidate windows have 30 replies; the others have 31 at the measurement boundary.

CPU includes fixture publishers, Reader, application and membership signature
generation in one process. Providers, ordinary endpoints, SSH crypto/server and
physical USB are excluded. Original ten-minute fictional leases are unchanged.
Two trials per variant and uncontrolled host frequency/activity are not a
confidence interval or a managed-service saving. These percentages describe the
whole application pipeline and must not be added to upstream operation timings.

## Managed and device acceptance

Pending the clean source freeze, verified host bundle, live feed/expiry/recovery,
actual matched host-tuple rollback and descriptive resource readback. The
preceding [accepted firmware readback](../2026-10-15-prepared-reads/firmware-readback.json)
remains the device baseline; this pass changes no firmware bytes or flash.
Manual panel/readability and host reboot acceptance remain deferred.
