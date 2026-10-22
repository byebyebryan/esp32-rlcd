# Recent-first RLCD trial

Starship and Snap now run the paired **wire-5** trial from clean source
`388a774558cd3c03167b806001f4c7b4c93a7f65`. Attention and known errors stay first.
Other current loaded **ready and working rows share one tier**, newest conversation
activity first; uncertainty follows. Exact ties preserve prior order. Status
icons, separate header counts, ST/SN/SW, loaded-only admission, independent
active-or-recent membership, the 72-hour window and always-on behavior remain.
Age changes prominence; it never proves a session finished or unloaded.

The immutable host bundle is `0908c9dc1e5a3090`, manifest
`0908c9dc1e5a3090a691e3196b83c6ba00a7b534c3954cd617325079bbbe6edf`.
The application is 1,243,920 bytes, SHA256
`9ebbe8709f541318b368f159509c3262a1f51f002c8a20f111a843850c5d6cec`,
built with ESP-IDF 5.5.3. Observer a8 and Mesh a24 remain pinned; semantic delta
and view-feed remain disabled. [receipt.json](receipt.json) binds exact selections,
readbacks, backups, tests and deployment identities; the companion manifests
bind all twelve client inputs and firmware components.

The sort uses each row's original runtime source sample minus supported
conversation activity, in exact milliseconds. Absolute timestamps from different
hosts and rounded age labels never determine order. The full diagnostic adapter
now uses that same per-row sample instead of the later collection-envelope time.
Changing a read/heartbeat cannot rejuvenate age. Firmware preserves host order
within the three tiers and stably attenuates expiring rows into uncertainty.
Status-total mapping is separate from ordering. Wire 5 retains the wire-4 fields
and bounds but versions this ordering change; old/new packets, requests and
bundle declarations fail closed instead of silently mixing pairs.

Luna implemented the source, tests and current documentation/media. The primary
reviewed the full diff, resolved the per-row clock decision, requested and
reviewed a failing-then-passing expiry-order regression, independently checked
25 translated-clock and 25 arrival-permutation cases, and owned packaging,
publishing and both scoped deployments. The primary also added an optional
`--profiles-config` to the capture tool so actual capture matches the managed
Starship Default and Snap Default/Work routes.

The full installed suite passed **124 tests, zero skips** on Python 3.11 and
3.14; the strict SDK gate passed **12/12** on both. Feed/motion/frame sanitizers,
current gallery hashes, docs, eleven negative deployment-policy controls,
installed current/rollback artifact gates and the full dotfiles check pass.
[All ten hosted source jobs](https://github.com/byebyebryan/esp32-rlcd/actions/runs/39713957878)
passed, including both fresh public SDK installs, complete zero-skip suites,
five firmware builds and both gallery modes. Current gallery assets changed
with the new demo order; historical evidence and all old deployment gates remain
unaltered.

Each host's exact board MAC was rechecked, a complete 16 MiB backup and managed
preimages were saved, scoped status/diff/dry-run reviewed, and only the application
was flashed. Exact readback passed on both; bootloader, partition table, NVS/device
data and the untouched application tail remain exact. Each host then admitted
nine initial and nine recovery frames through the installed bridge with the
explicit managed profile config, separated by silence that revoked live claims.
Both managed services resumed active with zero automatic restarts and fresh
health=0, partial=0, miss=0 diagnostics. Actual post-update inspection on both
hosts independently confirms mixed ready/working rows in exact increasing age
order and all three profiles current. The sampled nine-row view placed a
three-hour-old ready session last; counts/ages can change with real activity.

Only RLCD was stopped/restarted. All seven recorded native daemon identities
and all eighteen other recorded service identities remain exact. Profile config,
startup links, collectors, publishers, Tmux, 349 and native sessions are preserved.
Snap's three original dirty source files remain byte-and-mode exact. A further
concurrent desktop source edit changed twelve existing paths and added six new
paths during the run; these remain untouched and outside the RLCD commit and
scoped apply. Starship's
stale desktop overlay already matched the published descendant byte-for-byte;
its HEAD/index baseline was reconciled without writing any worktree file, with
recovery metadata and before/after hashes retained. No desktop settings were
applied by this rollout.

Rollback is the matched wire-4 bundle `d4304a1ff7e07ac4` and application
`094ecc7be6e6b735c03e3b140a6228b40af65b2dea60a3bdb328ebb8dc52556a`,
plus each host's exact managed preimages. Both old and new archives remain
read-only. Restore the old application and client selection together; a producer
restart is unnecessary. Earlier a7/a23, SDK-upgrade and firmware records retain
their original tuples and claims.

Serial admission/readback and automated sorting are verified. Physical
readability and the user's preference for mixed ordering remain an actual-use
judgment. No host reboot/unplug or new whole-producer CPU/RSS/capacity/recovery
campaign was performed. Private raw reads, logs and complete backups remain in
`~/.local/state/rlcd-recent-first-trial/20261022T023619Z/` on their owning hosts.
