# Plain titles and SW profile badge

Both managed RLCD dashboards now use plain session titles and per-row badges:
Starship Default `ST`, Snap Default `SN`, and Snap Work `SW`. Work keeps its
native Snap host and home namespace. There are still two physical hosts and
two host totals. The loaded-session policy and observation packages are unchanged.

The [receipt](receipt.json) pins consumer runtime
`883f77f99d470efb42d5c0a7cf701ac7c3488991`, host bundle `95ecb5378a248111`,
ops selection `1dc7cae`, private evidence hashes, both hardware readbacks and
managed-service results. This is a paired wire-4 bridge/firmware update.
Wire 3 is rejected rather than guessed or silently converted.

## Validation

All 90 dashboard tests pass, including three simultaneous ST/SN/SW rows,
same native ID in distinct home namespaces, malformed badge/host rejection,
expiry and retained Work context. Native motion/render checks pass. The
source preview was visually inspected, and a clean ESP-IDF 5.5.3 build succeeded.
Existing presentation images are byte-unchanged; their source manifests were
refreshed for wire 4.

Only the application at `0x10000` was written on each board. The 1,243,904-byte
image SHA256 is
`6c17962f1c30bfa0866879647eb3b5e0110757a36c80df7c742940756045e1d1`.
Exact readback matches on Starship (`94:a9:90:f3:43:74`) and Snap
(`94:a9:90:de:d0:04`). Bootloader and partition-table bytes remain unchanged.

Each board acknowledged 12 healthy frames before a six-second feed interruption
and 12 after recovery. Request, sequence and CRC match the original encoded
frames. The live view contained three ST rows and one SW row. During silence,
all four became uncertain and current waiting/working/attention counts fell
to zero; both recovered. No render deadline miss was reported in these captures.

Both ordinary managed services then passed exact bundle verification and
reported healthy admitted device ACKs, zero restarts and no scoped chezmoi
drift. Installed inspection confirms SW still has native `hostScope=snap`.
Scoped source status/diff/dry-run preceded application. The ops artifact gate
passes on both hosts.

## Rollback and diagnostics

Private backups retain the boot/layout region and full two-MiB application
partition for each board under `~/.cache/rlcd-sw-wire4-20261019` on both hosts.
Retain those archives and the wire-3 bundle `bcc1077fe14d738d`. Badge-only
rollback restores that host's exact old application partition and matching
bundle/selection together. It does not stop Work observation or restart Codex.
The new ops gate preserves the exact old selection and archive hashes.

The first Snap capture asserted equal row counts during partial warm-up;
firmware correctly retained uncertain context, so the safety path restored
and verified the old app. The capture was corrected to the existing partial
row rule, then the unchanged new image was reapplied and passed. That attempt
and the aborted earlier full-flash backup remain separate private diagnostics.
Test-offset and managed-audit field-name corrections also remain identified
in the receipt; no production change was inferred from those helper errors.

USB admission, native rendering and feed recovery were verified. No physical
photograph, cold power-cycle or unplug/replug acceptance is claimed. This
display update does not qualify or restart the dark delta feature.

See [profile operation](../../../projects/agent-dashboard/docs/home-profiles.md)
for route selection and the presentation-only badge boundary.
