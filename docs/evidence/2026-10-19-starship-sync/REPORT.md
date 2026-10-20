# Starship repository, service and RLCD synchronization

Starship now selects the same verified working-set host bundle and firmware
components as Snap: 72-hour active-or-recent membership, terminal ready/error
marks for recent unloaded threads, readable 24-pixel header counts, and no separate
recent counter. The repository is on published `main` rather than the retained
delta-review branch. That branch and all prior artifacts remain available.

The source at preparation was `50ee79e0b344d84ba94ff584a6a7bc53944d4db3`.
Only documentation differs from firmware source
`df89736842857dc0606775ffaf4cf92b63284339`; every selected host-bundle input also
matches current source. The installed Observer/Mesh pair passed wheel, package
inventory, RECORD and interface verification before the switch. Existing source
CI results retain their own commit and scope; no producer/performance gate is
relabelled by this deployment.

The exact board `94:a9:90:f3:43:74` was independently identified as ESP32-S3,
16 MiB flash and 8 MiB PSRAM. A fresh full 16 MiB flash backup was verified before
writing the selected bootloader, partition and application. All three component
readbacks match their pinned SHA-256 values. The prior partition layout is exact.
The managed wire-2 bridge remained stopped until the matching wire-3 client was
applied through four scoped chezmoi targets.

The actual cached IPC/fixed-SSH route passed for both hosts with complete scopes,
zero uncertainty and four distinct remote proof nonces. On the physical RLCD,
15 healthy frames were confirmed before silence and 15 after recovery. Six seconds
without feed cleared all current counters and retained 11 uncertain rows.
Request/sequence/CRC checks pass, with no missed frames. The final managed service
reports 11 healthy rows, zero uncertainty, zero missed frames and no restart
failures; user startup remains enabled with lingering.

Only Starship's dashboard bridge was stopped/replaced. Collector, full/active/
working-set publishers, Tmux selections and 349 service incarnations remain exact.
Snap's device and client selection were unchanged. The native provider, historical
writer and dark delta-sync feature were not modified. Manual panel/reboot and
whole-producer acceptance remain separate.

[Receipt](receipt.json) pins the bounded observations, images, artifact checks and
logs. Full flash and exact managed-file preimages are retained outside Git at
`~/.local/state/rlcd-starship-sync/20261020T004355Z/`. Rollback restores this host's
wire-2 flash image plus its captured bridge selection/unit/launcher/startup; no
collector or sibling-device change is required.
