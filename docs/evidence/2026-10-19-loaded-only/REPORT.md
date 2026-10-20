# Loaded-only dashboard selection

The working-set migration had exposed the producer's active-plus-72-hour-recent
membership directly on RLCD. The requested dashboard view is loaded sessions
only. Source `11e54f2` now requires current running-runtime evidence before adding
a row. A loaded idle session remains visible as ready; an unloaded session is
removed regardless of its historical completion or failure. Unknown runtime
cannot introduce a new row. Source loss preserves existing context as uncertain
until a positive exclusion or current complete census authorizes retirement.

The source route, public membership/field leases and strict admission remain the
same. The bridge filters the admitted working set before row selection and whole
roster totals. No recent rows or recent counts are emitted by this view. Header,
firmware, packages and producer behavior are unchanged.

All 72 dashboard checks pass on Python 3.14 and 3.11, without skips. They include
current loaded/waiting inclusion, positive unloading despite recent membership,
unknown-runtime exclusion, retained uncertainty, recent history at the capacity
boundary, and native wire admission clearing previously displayed rows on unload.
Generated images remain unchanged; source manifests and docs are refreshed.

A live current read selected exactly six eligible running user sessions and
excluded five positively parked sessions, including `codex` and `mesh-plus` on
Starship. Both managed device services now use verified bundle
`1ad6ef316f2aba74`; each returned healthy USB acknowledgements with six rows,
five ready, one working and zero recent or uncertain. Only the four dashboard
client targets were applied. All protected collector/publisher/Tmux/349 service
invocations match the fresh preimages. Private preimages and scoped apply logs
are retained at `~/.local/state/rlcd-loaded-only-20261020` on each host, and the
previous immutable bundle remains available for rollback.

[The receipt](receipt.json) records the source, exact bundle, tests and per-host
health. Earlier recent-display receipts retain their original historical policy
and evidence. These are current native-source projection and USB acknowledgement
checks; manual panel/reboot observation is separate.
