# Dashboard helper and failure refinement

Planned pass: remove Codex title-generation helpers from the live roster and
distinguish known failed turns from unavailable observations. Preserve Observer
API 4, source-sampled activity ages, full native identity and provider ownership.

## Target behavior

| Admitted evidence | Dashboard behavior |
| --- | --- |
| Confirmed `kind=system` title helper | Excluded from rows, counts, overflow and retained context |
| Current running runtime, `native_runtime_error` phase reason and current failed outcome | Error cross using the existing error style; counted as needing attention |
| Current working, blocked or waiting phase | Existing phase presentation takes precedence over an older failed outcome |
| A fresh in-progress latest turn | Previous failure marker clears for the same identity |
| Missing failure evidence or an unproved unknown phase | Unknown marker |
| Expired source, outcome or runtime evidence | Uncertain context without a current error marker, age or flashing |

The error marker describes a known failure; it does not assign a new provider
phase or infer that the thread is awaiting input. Capacity-specific text needs a
supported public error category. The existing public failed outcome supports a
generic failure marker now.

## First checkpoint Observer classification

The independent source correction is `2356323`, accepted through `e399dd0` in
Agent Observer. It maps the native `thread_title` tag to existing `kind=system`.
Its 411 source tests and passive comparisons against both ordinary host daemons
pass. Unknown feature tags remain unknown; ephemeral user threads remain users.

The packaged core-only 0.7.0a3 collector is independently accepted and selected
on both hosts; see the [producer receipt](https://github.com/byebyebryan/agent-observer/blob/e399dd0/docs/evidence/2026-10-14-title-helper/REPORT.md).
The remaining device checkpoints below govern the consumer pass. Check
raw Service 4 and Agent v3 output, default rosters and retained unknown-to-system
reclassification. Keep the accepted prepared-reader handoff and its immutable
artifacts intact. Existing read clients understand the system kind; changing a
read CLI alone does not change the collector's classification.

Accept the packaged producer checkpoint before implementing the consumer pass.
The RLCD's existing system exclusion then removes both helper identities.

## Second checkpoint Bridge and firmware

In `host/live_dashboard/projection.py`, derive an error display state only from
an admitted current running runtime, the existing `native_runtime_error` reason
and a current failed outcome. A positive working/blocked/waiting phase or a
current in-progress latest turn takes precedence. Do not infer failure from an
arbitrary unknown phase, source error or preceding turn outcome alone.

Derive failure presentation health from the admitted failure/runtime evidence.
Use the existing source-sampled activity clock when current; retain `?` for a
missing or future clock. Failure styling cannot renew any evidence lease.

Reuse `DASH_ERROR` and its existing cross/flashing row style. Group errors with
blocked rows in the attention band, followed by waiting, working and uncertain
rows. Keep oldest known activity first and stable ties within each band. Define
the `!` header count as attention: blocked plus known failed rows. Update complete
roster totals, overflow and per-host counts together.

Introduce device wire 2 for the additional live error state. Update request and
response tags, bridge encoding and firmware admission together; retain strict
CRC, bounds, identity, nonce/request/sequence and source-lifetime checks. Define
code 4 as the derived error display state. Firmware admission, selected-row
count validation and expiry ordering must put it in the attention group.
Reject protocol mismatches; retain the matching wire-1 bundle/firmware pair for
rollback. Observer API 4 and Agent v3 remain unchanged.

## Regression and acceptance checks

Use the captured capacity case as a portable corpus with fictional identities,
paths and clocks. The live incident confirmed three Snap user failures with
native `systemError`, latest turn `failed` and error category `serverOverloaded`.
A later native sample confirmed mesh-plus entered a fresh active turn and its
feed row returned to working. The two title helpers were independently idle.

Test the following through projection, encoded wire and native C admission/render:

1. Three known failures show error crosses and three attention counts; both
   system helpers contribute zero rows or counts.
2. A fresh active turn clears that identity's failure marker. An older failed
   outcome cannot override current working, blocked or waiting evidence.
3. Unknown phase without the specific runtime-error/failed-outcome evidence
   remains unknown. Failed history on a parked identity remains excluded.
4. Outcome expiry, source silence and partial host loss clear current error
   styling and ages; healthy sibling facts remain useful. Heartbeats do not
   renew failure evidence.
5. Partial reclassification removes retained helper context, including identities
   beyond the USB prefix. Real conversations sharing a project remain distinct.
6. Error-containing frames enforce counts, CRC, bounds and protocol version;
   delayed, duplicate and mismatched replies retain the existing rejection rules.

Run dashboard native/sanitizer checks and documentation/media checks. Refresh
the native gallery provenance manifests if authoring inputs change, and build
the ESP-IDF application and immutable host bundle.

## Paired rollout

After producer acceptance, stage the matching bridge and firmware artifacts and
retain the current selections and a device backup. Replace the RLCD application
with exclusive serial ownership, then select/start its matching verified bridge.
Verify flashed-image readback, admitted roster, attention counts, retry/expiry
and scoped rollback with serial/native evidence. The shared Codex daemons and
ordinary sessions retain their ownership; failure presentation performs no
automatic retry, model change, archive or unload.

Manual panel readability and reboot checks remain deferred under the user's
existing instruction. Prepared-reader performance adoption remains a separate
client pass with its own output/cost comparison.
