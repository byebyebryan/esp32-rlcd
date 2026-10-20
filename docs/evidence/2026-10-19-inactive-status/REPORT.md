# Inactive-session status correction

An unloaded recent session was incorrectly shown with a ready check because its
last completed turn was reused as a current work state. Passive native inspection
confirmed Starship's `codex` was `notLoaded` and absent from the loaded inventory;
the admitted runtime was correctly parked. The bug was in the display projection.

Host source `e118bd2` restores the neutral dash for every currently parked session,
including completed and failed historical turns. Ready requires current running
runtime and a current waiting phase. Unknown runtime remains unknown. Recent
membership, expiry, counts and active highlighting rules are unchanged.

All 72 dashboard checks pass on each installed Python 3.14 and 3.11 pair, with no
skips. They cover matching and conflicting terminal evidence, a single identity's
ready-to-parked transition, native wire marker 6, and device expiry. Frame checks
pass; regenerated presentation images remain byte-identical. The live `codex` row
changed from waiting to parked, and every remaining ready row has current
running/waiting evidence.

Both managed clients select verified bundle `271ef152d3c4e155`. Starship and Snap
returned healthy USB device ACKs with 11 rows, zero misses, no partial source and
zero uncertain rows after restarting only the dashboard bridge. Fresh managed
preimages were preserved on each host before applying the four client targets;
collector, publishers, Tmux and 349 service invocations stayed unchanged.

Firmware, package wheels, serial identities and the four-counter header did not
change. Original evidence for the earlier terminal-result policy remains intact.
The private recovery/evidence directory on each host is
`~/.local/state/rlcd-inactive-status-20261020T012308Z`; the immutable prior bundle
remains installed for rollback. [The receipt](receipt.json) pins the runtime,
checks and per-host device health. This is host-status and USB acknowledgement
evidence; no new manual panel or reboot acceptance is claimed.
