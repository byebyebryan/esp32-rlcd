# Restart context and clean test gates

Both review findings are fixed. The live host bridge persists identity and
presentation context before USB output, and clean-checkout native tests no longer
require an undeclared sibling Observer fixture or SDK installation. Runtime
`1b2717f8e48feef54b3e39a93e07f79da3c9b452` is frozen in host bundle
`de0a8ee7744e9fc9` (full manifest digest in [receipt.json](receipt.json)).

The old projector lost the unavailable Work profile after a bridge restart when
Default had already recovered, including when Default was complete and empty.
The new private file retains full bounded identity keys, labels/projects, host,
order and badges, including rows beyond the USB limit. It stores no leases,
phase, outcome, current status or age. Restored rows are uncertain with zero
validity; exact negative evidence or current complete coverage still retires
only the matching namespace. Per-host initialization markers prevent a corrupt,
missing or changed-route file from turning a partial startup into an empty
replacement. The file is locked, bounded to 8 MiB, atomically replaced with
fsync, owner-private and opened without following symlinks. An unchanged roster
does not fsync again. File failure stops output before an undurable identity
change. Firmware still anchors validity to its original request: a slow-save
regression proves an expired response remains stale on arrival.

Validation: clean Python 3.14.8 and 3.11.17 environments each ran 110 cases, with
89 passes and 21 explicitly labeled SDK skips. This includes the original
restart case through the native C feed, complete-empty/exclusion isolation,
independent host initialization, oversized/deep/corrupt files, private-file and
lock refusal, write failure, full-roster persistence, slow save and real PTY
release/reopen. The separate strict gate ran three public two-home cases against
the exact installed Observer/Mesh pair with zero skips and no source checkout
imports. Missing packages and outside-prefix imports fail that gate. The frame,
motion, documentation, full dotfiles and selection artifact checks pass. Debug
and Release regeneration produce the same five published image/animation bytes.
Hosted strict SDK qualification remains pending a compatible publicly reachable
Mesh source revision; it is not represented by the package-free native job.

Starship and Snap were switched using fresh exact managed-file preimages and a
scoped chezmoi diff/dry-run/apply. Only the RLCD client was restarted. Each real
device then acknowledged eight partial frames during an eight-second delay of
only the client Work watch: the SW row stayed uncertain with zero validity and
unknown age while the sibling remained current. Each acknowledged twelve
subsequent recovered frames with a current SW row. The managed services were
restored afterward and both report four rows, health 0, partial 0 and miss 0.
The durable files have four context rows, mode 0600 under a 0700 directory.
Producer, publisher, 349 and Tmux service invocation/PID snapshots are unchanged.

The installed Observer/Mesh wheels, wire 4 firmware, loaded-only selection, plain
titles and ST/SN/SW badges are unchanged. The original wire-4 host bundle and
firmware pairing remains in the dotfiles host-refinement rollback record, as do
the older wire-3 rollback and immutable producer artifacts. Private preimages
and foreground traces remain under
`~/.local/state/rlcd-recovery-fixes-20261020/` on each host. The physical evidence
is matched USB acknowledgements and diagnostics; no visual panel, reboot, unplug
or whole-producer resource/performance acceptance is claimed. Luna Max
implemented recovery and test-gate slices; the primary reviewed invariants,
validated the final gates and performed the scoped deployments.
