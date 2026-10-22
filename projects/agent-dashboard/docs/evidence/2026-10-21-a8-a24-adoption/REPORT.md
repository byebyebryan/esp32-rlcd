# Published a8/a24 host-client adoption

Starship and Snap now select released Observer **0.7.0a8** and Mesh
**0.1.0a24** in immutable RLCD host bundle `d4304a1ff7e07ac4`. Its full manifest
digest is `d4304a1ff7e07ac4aa99ed5244f2b571f274860926a11c8bcfafaecc2f2c7b9d`;
the clean runtime source is `c4db92f1b8c7c7c609975c20fc2d1dc114570547`.
[receipt.json](receipt.json) records exact public artifacts, checks and deployed
identities; [bundle-manifest.json](bundle-manifest.json) binds all twelve inputs.

The public [Observer release](https://github.com/byebyebryan/agent-observer/releases/tag/v0.7.0a8)
and [Mesh release](https://github.com/byebyebryan/mesh-plus/releases/tag/v0.1.0a24)
were downloaded independently and matched the selected wheels on both hosts.
Installed package inventories, RECORD entries and locked transitive dependencies
were checked. The release lock is now shared by the installer, strict SDK gate,
hosted CI and bundle verifier. It pins wheel URLs/hashes and source metadata;
there is no SDK source-checkout or package-index fallback during installation.

The full client suite passed **112 tests with zero skips** on Python 3.11.17 and
3.14.8. The strict gate passed all twelve required cases on each version and
refused the retained a7/a23 environment and a package-free interpreter. The
cases cover public admission, native identity/home isolation, activity and
membership expiry, complete/partial coverage, exact exclusion, bad receipts,
gap/clock/disconnect, fresh reconnect and owned cleanup. The ordinary reader
boundary requires the working-set source/socket, a host-scoped cached watch and
empty extensions. The package-free suite passed 91 cases with 21 labeled SDK
skips. Shared frame/motion sanitizers, docs and workflow checks passed.
The installed dotfiles artifact gate passed on both hosts, and the full local
dotfiles check passed against the current worktree, including the retained
concurrent desktop edits.
[All ten hosted jobs](https://github.com/byebyebryan/esp32-rlcd/actions/runs/39700693244)
passed, including fresh locked SDK installation and zero-skip client suites on
both Python versions, five firmware compile variants and both gallery modes.

The new bundle adds the release lock and changes its verifier. Its ten
application runtime/font inputs are byte-identical to the preceding bundle.
Wire 4, loaded-only selection, independent active-or-recent membership with the
72-hour window, full identities, ST/SN/SW, restart context and always-on behavior
are unchanged. Delivery remains ordinary complete selected views. Semantic
delta and Mesh view-feed remain disabled/unselected.

Each host received the verified read-only bundle before selection. Exact managed
preimages and a working old bundle were retained; scoped chezmoi status, diff
and dry-run preceded the apply. Only the RLCD launcher, selection and service
changed; no externals or desktop scripts were applied. Starship switched first,
then Snap. Both new services reported zero automatic restarts and healthy USB
frames with health 0, partial 0 and miss 0. Counts were sampled at different
times: ten rows on Starship and eleven on Snap. Subsequent managed-client reads
were current for Starship Default and Snap Default/Work on both hosts, with
eleven selected rows in that sample. Counts may change as native sessions change.

Both managed target sets converge, profile configuration and startup links are
unchanged, and all six native daemon PID/start/executable identities remain
exact. Core collector/publisher, writer, full/active, Tmux and 349 roles were not
restarted or reselected. A concurrent Starship desktop update recreated its
Tmux desktop/fleet context during preparation; the first guarded apply stopped
before mutation. That external change is recorded separately, and its refreshed
pre-apply state was preserved through the RLCD switch. Unrelated dirty desktop
edits on both dotfiles worktrees were retained, not committed with this change.

The original wire-4 firmware and all historical profile/flash/rollback records
remain intact. No firmware was flashed. The a7/a23 client bundle and exact
managed-file preimages under `~/.local/state/rlcd-a8-a24-20261021/` provide the
client rollback boundary; rollback was prepared and verified, not exercised in
this run. Private raw reads, logs and preservation snapshots remain under the
repository's ignored `.cache/a8-a24-adoption-20261021/`.

The earlier handoff's `serial_missing` report was stale: both exact boards were
connected and admitted replacements during this rollout. USB diagnostics are
bounded admission evidence, not new visual readability, panel contrast, reboot,
unplug or whole-producer performance/resource acceptance. No new CPU/RSS,
dense-capacity or recovery campaign was run. Luna Max implemented the locked SDK,
CI and bundle slice; the primary reviewed and corrected it, performed final
qualification, froze the clean bundle and completed scoped deployment.
