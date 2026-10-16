# Owned admission and selected dashboard reads

This host-only application checkpoint adopts the independently accepted Observer
a6 and Mesh a22 artifacts. It preserves API 4/read wire 6/Service 4/Agent v3 and
device wire 2. Firmware, source cadence, receipt lifetimes and presentation policy
remain unchanged. Source, installed artifact, controlled pipeline and managed device acceptance
pass independently. The final resource window is recorded separately below.

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

The [media readback](media.json) regenerates all five PNG/GIF assets with
unchanged byte hashes. Only the three source-provenance manifests change.

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

The [clean host bundle](bundle.json), frozen at source `ed08709`, is
`5bf9f44fa523123c`, manifest SHA-256
`5bf9f44fa523123c1694daec549d94e5cb8c45120bafa428c158b0dc68385532`.
Its nine runtime files exactly match the controlled candidate. The
[source CI](ci-source.json) passes native and Debug/Release presentation jobs.
Scoped [deployment](deployment.json) selects that bundle and its independent
Python through dotfiles `5c5cb12`; rendered unit/launcher/config/startup and exact
installed verification pass. Existing primary dotfiles drift is preserved by a
separate two-file publication from an isolated origin/main worktree.

[Real cached-generation parity](live-parity.json) matches strict full projection:
395 Starship current identities, eight selected full bodies and 387 positive
exclusions (252 children and 135 parked). Snap is current and empty. The complete
diagnostic retains all 395 rows. The reference resets only Reader ordering for a
fresh guard; native proofs, receipts and query time remain unchanged. This is
consumer parity, not another independent native completeness claim.

The [physical device capture](live-device/summary.json) confirms 24 healthy
CRC/request/row matches before and after six seconds of silence. Eight real rows
recover; silence clears all work/age claims and retains eight uncertain identities.
Sampled render time peaks at 17,385 microseconds, with zero deadline misses,
292,171 bytes of internal heap and a 4,776-byte stack watermark. The
preceding [accepted firmware readback](../2026-10-15-prepared-reads/firmware-readback.json)
remains the unchanged wire-2 device baseline; no firmware build, flash or reset
is performed in this host pass.

[Actual rollback](rollback-health.json) reselects bundle `807eab96b48825ae` and its
retained a5/a20 Python; the running old owner receives an admitted eight-row
ACK. [Reselection](final-health.json) restores the candidate with healthy ACKs,
NRestarts 0 and exactly one serial owner. Host selections, unit bytes and manifests
are backed up outside Git under the directory recorded in deployment.json.
[Protected-state comparison](protected.json) retains collector/publisher, Tmux and
349 incarnations locally and selected collector/publisher incarnations on Snap.

Manual panel/readability and host reboot acceptance remain deferred.

## Descriptive service resources

The old and new selected-service resource windows are separate from controlled
fixture timings. Each spans 120 seconds with no added reader; the candidate gets
60 seconds of warm-up after final reselection. Original native work and host
frequency remain uncontrolled. The [resource summary](live-cost-summary.json)
binds the [old](old-live-cost.json) and [new](new-live-cost.json) windows:

| Selected tuple | CPU percent of one core | Mean process-tree PSS |
| --- | ---: | ---: |
| Existing a5/a20 bundle | 10.68 | 51.28 MiB |
| Selected a6/a22 bundle | 8.12 | 40.75 MiB |

The observed CPU difference is 23.96%. Each window has stable unit incarnations,
two processes and 19 file descriptors. Old and new process ages differ; these
memory snapshots are not a universal saving claim. Unit CPU and process-tree
memory accounting have different scopes and must not be added to overlapping
collector/publisher totals. Fresh correlated acquisition and strict Client/native
validation still contribute cost; no cadence or protocol shortcut is selected.

The [installed full diagnostic](installed-roster.json) records 396 identities and
nine selected rows after measurement, one more than the earlier 395/eight parity
checkpoint. [Final readback](final-readback.json) retains the same selected owner,
zero restarts, one serial descriptor owner and healthy device diagnostics. This source shape is smaller than the original
494-record/13% investigation: Snap is now empty at native and baseline sources.
That input change is separate from this implementation's controlled saving.
