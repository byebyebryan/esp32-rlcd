# Dashboard release and logging refinement

The dashboard runs a verified quiet bundle on Starship. Observer, Mesh, dashboard
and scoped chezmoi source are published on their remote `main` branches. The
[acceptance metadata](acceptance.json) binds source publication, installed runtime,
validation, live adoption, rollback and journal measurements. The
[preceding reliability receipt](../2026-10-13-live-reliability/REPORT.md) retains
its original artifact and physical USB recovery evidence.

## Quiet operation and diagnostic refinements

Production omits per-frame ACK/health/summary output. `--verbose` retains that
trace for bounded foreground captures. Validated `device_health` events report
feed state, counts and sampled render/heap/stack values once a minute and on
health, partial or deadline transitions. Source changes, ACK loss/recovery,
serial retry and worker failures remain visible.

Malformed, duplicate and out-of-range health fields are discarded. Health reports
cannot acknowledge a request or renew source evidence. ACK events also report
changes in source admission, distinguishing initial transport recovery during
warm-up from later admission of current observations.

A 70-second baseline window produced 210 lines and 29,330 bytes. The quiet
70.01-second window produced one health summary and 193 bytes, with the same
process, seven rows, both sources current and zero logged deadline misses.
These are bounded steady-state samples; failure and transition traffic remains
intentional.

## Validation and deployment

| Gate | Result |
| --- | --- |
| Dashboard | 40 tests pass: 25 projection/C admission, 5 worker lifetime, 8 serial/diagnostics and 2 bundle checks |
| Observer | 401 tests pass; profile and network conformance pass 7 and 10 cases |
| Mesh standalone | 121 tests pass, including all four independent Agent v3 cases |
| Mesh native and SSH | 159 tests pass with the separate legacy Agent/Tmux reference tuple |
| Managed configuration | Canonical chezmoi gates and final installed artifact/unit checks pass |
| Live rollout | Candidate, prior-bundle rollback and reselection each admit seven rows from both current hosts with matched acknowledgements |
| Preservation | Eight concurrent source files retain their hashes; collector, publisher, Tmux and 349 retain their process IDs and active state |

The selected immutable bundle is `ccb8f7b3fa388f1d`, built from clean application
source `41d22c287ce9bc9de0780ccb3255c65f4741af23`. Its manifest SHA-256 is
`ccb8f7b3fa388f1d59986ba6753ce24060a7febccefffb0c03fc16918dd45d96`.
The previous `30c0fb475fe13866` bundle and exact managed selection remain
available for rollback. The enabled persistent unit is active with zero automatic
restarts. Firmware, device wire 1, accepted layout and producer artifact selections
retain their existing bytes.

## Source publication and release gates

Publication uses ordinary fast-forward pushes. The isolated chezmoi release
branch preserves remote report/runtime work and carries only reviewed dashboard
and producer-selection changes. Unrelated dirty work in the canonical source
checkout remains intact.

Hosted Observer CI exposed two release-gate gaps: obsolete Mesh SDK pins and a
managed-render fixture dependent on a production hostname. CI now selects the
accepted immutable Agent v3 SDK source revision, and the disposable fixture maps
its runner hostname explicitly. Mesh's standalone gate now includes the Agent v3
module that previously ran only in the full suite. Latest hosted checks pass for
both producer repositories; their exact runs are linked in the acceptance metadata.

Source publication does not create new hosted wheel releases. The selected
Observer 0.7.0a1 / Mesh 0.1.0a17 artifacts retain their accepted hashes. Manual panel
and real reboot/post-boot checks remain deferred by the user's prior instruction.
