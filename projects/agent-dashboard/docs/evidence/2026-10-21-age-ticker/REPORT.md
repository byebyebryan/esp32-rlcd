# Local activity-age ticker trial

The paired wire-6 bridge and firmware advance activity age on the ESP32's
monotonic clock between source samples. The initial age is an exact numeric
source-sampled duration, with an opaque activity equality key. Repeated packets
preserve the running anchor and fractional milliseconds. A larger source age
catches up without moving backward; new activity starts a new counter. Labels
change at second, minute, hour and day boundaries and saturate at `+++` at 100 days.

This is presentation of elapsed time since the last known activity. It does not
prove that newer activity cannot exist, reconstruct initial source/transport lag,
renew evidence, change status or re-sort rows between packets. Unknown age and
expired row support show `?`; bridge/device restart starts a new local anchor.
Observer's configured periodic runtime sampling remains 20 seconds on Starship
and 30 seconds on Snap, with native hints enabled. Device requests remain one
second and the render loop remains 25 fps. The local ticker requests a redraw
only when a visible age label changes.

The immutable runtime source is `629af3721b9ffc6218060c839d22472cf1b808e0`.
Bundle `164b7f99c40e7676` has manifest SHA256
`164b7f99c40e767655c94ee907d34b7b8825bb6433a9a70e11be940f8788eb59`.
The application is 1,244,816 bytes, SHA256
`d437fae37d179816e4bdf665ef4457c10ba50fe87a3a0f79bfe003d66b81f943`,
built from clean source with ESP-IDF 5.5.3. Observer a8 and Mesh a24 remain
exactly pinned. The wire version rejects mismatched old requests, packets and
bundles. Loaded-only admission, ST/SN/SW badges, recent-first ordering, 72-hour
membership, always-on behavior and separate header counts remain unchanged.
Semantic delta and view-feed stay disabled.

Validation passed 131 installed tests with zero skips on Python 3.11 and 3.14,
including seven new projection/native ticker regressions. They cover fractional
milliseconds, repeated samples, catch-up, new activity, unknown/restarted
anchors, unit boundaries, saturation, redraw boundaries, malformed numeric/key
fields, atomic rejection and expiry without packets. The strict public SDK gate
passed all twelve cases on each Python. Native feed/motion sanitizers, current
gallery hashes, documentation, nine deployment-policy rejection controls and
full dotfiles/installed-artifact gates passed. All ten jobs in the
[source CI run](https://github.com/byebyebryan/esp32-rlcd/actions/runs/39718185065)
passed, including five firmware builds and both public SDK environments.

The [receipt](receipt.json) records each host's exact application readback,
complete 16 MiB backup hash, live admission, six-second silence expiry, recovery,
managed convergence and resumed health. Each exact board MAC is checked before
application-only flashing. Bootloader, partition table, device data and untouched
application tail are compared with the backup. Only the RLCD service restarts;
profile configuration, native daemon identities and other service identities
are independently compared. Concurrent desktop source edits remain outside this
rollout: file snapshots and the three-path dotfiles commit delta distinguish
those continuing edits from the RLCD selection changes; no old snapshot is
restored over another owner's work. Scoped chezmoi
status/diff/dry-run precedes the apply; scripts are excluded.

Rollback is the matched wire-5 bundle `0908c9dc1e5a3090` and application
`9ebbe8709f541318b368f159509c3262a1f51f002c8a20f111a843850c5d6cec`.
Restore application and client selection together using the saved managed
preimages. Old archives and previous firmware/dependency evidence remain intact.
Private raw logs, full backups and source/preservation snapshots are retained at
`~/.local/state/rlcd-age-ticker/20261022T033608Z/` on their owning hosts.

Serial admission and exact image readback are software/device evidence.
Physical readability and the preference for ticking ages remain actual-use
judgments. No new whole-producer CPU/RSS/capacity campaign, host reboot or
unplug test is claimed.
