# Live dashboard implementation and device receipt

2026-10-13. The dashboard now consumes the installed Observer API 3 / snapshot 5 /
Service 3 / Mesh SDK 1 Agent v2 contract. The source implementation is in
`projects/agent-dashboard`; its [contract](../../../projects/agent-dashboard/docs/live-integration.md)
owns the device projection and admission rules. No Observer, Mesh, provider or
global-service selection changed.

## Implemented behavior

One cached Mesh subscription supplies running Codex sessions across explicit
Starship/Snap scopes. Confirmed children and positively parked sessions are
excluded. Full identity has a bounded stable digest token; project names have
rendered-width collision handling. ST/SN badges identify hosts. Current blocked,
waiting and working map to the retained flashing/inverse/normal styles.

Conversation-activity age is source-sampled. It replaces the synthetic exact
phase-age assumption without supplying a phase-entry clock. The host orders
blocked, waiting, working, uncertain, then oldest known activity with stable ties.
Whole-roster counts and omission remain explicit beyond the 32-row device bound
and eleven-row visible prefix.

Tagged USB replacements have strict byte/field/count/UTF-8/CRC bounds. Every
response matches a fresh device boot/request and a bridge incarnation/sequence.
Current authority expires from request-send time, capped at three seconds and
bounded by remaining Mesh leases. Duplicate/delayed delivery cannot renew it.
Expiry runs during silence; host failures do not suppress healthy siblings.
Bridge warm-up/restart retains device identity context without old work claims.

## Automated and live-input checks

The live suite passes 18 meaningful projection and C admission cases under
ASan/UBSan and warnings-as-errors. Cases include phase versus outcome, sampled
age, source loss/recovery, complete versus partial membership, full-roster
counts, rendered Unicode/truncation/suffix collisions, distinct namespaces/hosts,
request/nonce/sequence/CRC/encoding/bounds rejection, request-anchored late
delivery, expiry during silence, sibling preservation, bridge warm-up, retained-context duplicate rejection and already-expired arrivals.

Existing motion/UTF-8/rectangle checks pass, including 4,488 rectangle comparisons.
Pixel packing passes all 120,000 distinct pixels. All 42 prior static frame
SHA-256 values match their accepted baseline. Python lint/format and Git whitespace
checks pass. ESP-IDF 5.5.3 builds the live firmware with an 8 KiB main-task stack.

An installed SDK view admitted eight running rows across the two hosts and
rendered through the same C decoder/controller into a native preview. Preview
names/data stay in ignored local output. These checks establish projection and
admission, not independent proof of new native provider predicates.

## Device and rollback evidence

RLCD MAC `94:a9:90:f3:43:74` was verified through its stable USB identity and
esptool before replacement. A complete 16 MiB backup remains outside Git at
`/home/bryan/.local/state/esp32-rlcd/backups/20261013T220340Z-94a990f34374-live/flash-before.bin`.
Its SHA-256 is `7d6c302e9c114f70ea7784f1fb7152c0cbd202b26da69bf3dedadb517fd31456`.
An initial 180-second read timeout performed no writes; the longer/faster retry
completed and verified the full size. Backup logs/metadata retain both attempts.

All three flash-write hashes verified. The final 1,242,560-byte application readback
matches build SHA-256
`9945cab1b297440fc2a935f1d783ca29ce65e1e50100a77d373cf00e9c6abcfb`.
The [device capture](device.json) records two 15-second live windows around a
six-second bridge-stop window. There were 14/13 healthy checksum/row confirmations
in the final live windows, with nine selected sessions. Initial buffered old requests
were rejected by device request binding; accepted frames match their sent CRC.
Silence clears blocked/waiting/working counts, retaining nine uncertain rows.
A new bridge incarnation restores the live view.

The largest recorded live frame was 18,095 microseconds; neither window logged a
40 ms deadline miss. Minimum recorded internal free heap was 292,171 bytes;
minimum stack watermark was 4,776. These are bounded descriptive device samples,
not long-term capacity or physical display measurements. Observer collector and
Agent publisher PIDs remained 33895/33898. The separate 349 serial path was not
opened by this integration. The [initial candidate capture](initial-device.json)
retains the earlier two 25-second windows. The [five-minute review run](review-run.json)
records 301 health reports, a maximum of 18,776 microseconds and zero logged
deadline misses on that preceding candidate. The final firmware adds rejection
of duplicate retained identities and clears authority on controller rejection;
it is independently rebuilt, flashed, read back and recaptured above.

## Remaining acceptance

On-panel readability of real names, host badges and activity ages remains a
human review. Native previews, readback and serial admission do not establish it.
The bridge is a foreground process; no permanent bridge service is installed.
Stopping it intentionally leaves the panel in the unavailable state. Broader
native transition coverage, physical suspend and provider lifecycle predicates
retain the upstream producer's bounds.
