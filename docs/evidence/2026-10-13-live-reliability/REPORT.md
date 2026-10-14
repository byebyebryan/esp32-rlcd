# Live dashboard reliability acceptance

The bridge reliability implementation and managed Starship service are accepted
within the automated and live-device gates below. Real USB disconnect/reconnect
transport recovery is verified; user-visible confirmation and a real host reboot
remain separately pending. [Bounded acceptance metadata](acceptance.json)
binds source, installed artifact, dependency tuple, test results, protected
owners and rollback. [Device evidence](device.json) records silence/recovery.
The [execution plan](../../../projects/agent-dashboard/docs/live-operations-refinement-plan.md)
defines the remaining physical gates.

## Implemented behavior

The host retains minimal whole-roster membership independently of the 32-row
USB prefix and 11 visible rows. Forty selected members followed by five observed
in a partial view remain five current plus 35 uncertain; subsequent whole-feed
loss retains 40 uncertain members. Positive child/system/parked reclassification
removes membership and counts beyond the device prefix. Accepted complete omission
can retire display membership. Per-host capacity remains explicitly bounded at
65,535; capacity failure never silently discards counts or grants fresh facts.

A supervisor owns the subscription and serial workers. Expected Mesh failures
retry with lease revocation. Unexpected worker return/failure and cleanup failure
reach the owner as finite failure codes. Stop/SIGTERM cancels workers, releases
exclusive serial ownership and allows bounded cleanup. An uncooperative cleanup
has a five-second grace; failure terminates the process and its service control
group supplies the final OS cleanup bound.

Serial absence and busy ownership retry with bounded backoff without taking
another owner's port. Poll hangup, device removal and read/write failures close
the descriptor. Reconnection clears framing/request state and uses a fresh bridge
incarnation. Empty raw reads alone do not mean disconnect. Matching device
acknowledgements reset retry backoff; missing acknowledgements are diagnosed
separately from source health. Finite events and repeated-failure log limits keep
provider payloads out of diagnostic failures.

## Artifact and deployment

Initial application source checkpoint: `2ad5769b2739b708b1a8fe94b2d85c0ba30bc1e6` on
local branch `dashboard-live-reliability`. Its clean source freezes to
`~/.local/share/rlcd-agent-dashboard/18531bb45ac00c42`, manifest SHA-256
`18531bb45ac00c42338db697d05fc8785c20853dd37b2bc044800e623acf53f4`.
The small bundle includes the host code, verifier and font data required by label
metrics. Exact file sets/hashes and the accepted dependency tuple are verified
before service startup. Changed/additional/symlinked inputs are rejected.

Observer 0.7.0a1 / API 4 / snapshot-watch 6 / Service 4 and Mesh 0.1.0a17 /
Agent v3 / SDK 1 remain selected. This pass changes the consumer and its user
service, with device wire 1 and the flashed firmware unchanged.

Chezmoi checkpoint `00220a0` installs the application selection, launcher, unit
and startup link on Starship only. `rlcd-agent-dashboard.service` is persistent,
enabled under the user default target, and runs the immutable bundle. Existing
Starship lingering supports startup with the user manager at boot. The service
has restart on failure, a ten-second stop timeout and no start-limit lockout for
prolonged absence. Snap/Carbon/unknown host render gates ignore the application.

Only the four application targets were applied. The first file-only apply exposed
an absent configuration parent; including the new application configuration
directory completed the scoped apply. The source checker and operation guide
now record that requirement. Unrelated managed drift was preserved. Shared
check-script staging included only the new RLCD invocation; existing Codex/Claude
changes were left unstaged. The producer selection/launcher edits from the prior
pass retain their independent local delivery status.

## Validation

| Gate | Result |
| --- | --- |
| Projection and C admission | 25 tests pass under ASan/UBSan, including whole-roster partial counts through the real C decoder |
| Worker lifetime | Five tests pass: failure/return, cleanup failure, finite grace, cancellation and limited/redacted events |
| Serial | Four tests pass: private tty no-data/busy/hangup, actual supervisor SIGTERM/release, missing/busy/disconnect/reappearance with new incarnation, prompt retry cancellation |
| Artifact | Two tests pass: exact reuse and rejection of modified files, wrong manifest pin, extra files and symlinks |
| Existing renderer/motion | UTF-8/fallback/ellipsis, 4,488 packed rectangle comparisons, identity/geometry/source-loss/motion checks pass |
| Deployment | Full chezmoi canonical gate, new host render/wiring gate, installed artifact verification and systemd unit validation pass |
| Paired adoption | Candidate, retained baseline rollback and candidate reselection each produce matched healthy device acknowledgements |
| Final live capture | Two 15-second windows, 14 healthy matched acknowledgements each; seven rows in these samples; zero render deadline misses |
| Feed silence | Six-second silence clears blocked/waiting/working counts and retains seven uncertain identities; new bridge recovers |

The final capture's largest frame was 16,351 microseconds, minimum internal heap
292,171 bytes and stack watermark 4,776. These are bounded diagnostic samples,
not physical contrast or long-term performance claims. The managed service was
restored after capture and admits fresh frames from both hosts.

Protected collector/publisher, Tmux and 349 process IDs/command definitions and
provider/producer selection hashes match the baseline. Systemd reload clears
some `ExecStart` execution bookkeeping while retaining live owners; the check
compares owners and definitions separately from that bookkeeping. No ordinary
provider action, producer service restart, firmware flash or 349 device access
was performed.

## Audit followup and final artifact

The completion audit found a diagnostic gap: warm-up packets can validly retain
previous device rows. Their acknowledgement row count can exceed the packet's
new row count. The bridge now accepts bounded retained-row acknowledgements for
offline/warming hosts, while healthy views still require exact row-count equality.
Matching CRC/request/sequence remain required. This does not renew source facts.
Recovered-acknowledgement events and missing-acknowledgement events now include
last valid request/acknowledgement counters and sampled ages where applicable.

The regression gate passes **37 tests**, including a fifth serial case proving
valid retained rows during warm-up and rejection of an incorrect healthy count.
Final application source: `1632d8c4ab5b942ba55404e315110568401de90c`.
Final selected bundle: `~/.local/share/rlcd-agent-dashboard/30c0fb475fe13866`,
manifest SHA-256
`30c0fb475fe13866b6fcf201c75055ef062e1c30f991a5fa47915e7906558db4`.
The original artifact above retains its dated acceptance scope.

The [installed lifecycle proof](installed-isolated-lifecycle.json) runs this final
CLI in owned user/mount/PID namespaces, masking the stable serial directory with
private PTYs. Sixteen seconds of absence, exclusive busy ownership, actual tty
hangup, reappearance/new boot nonce and clean SIGTERM/release pass in one process.
Request/checksum agreement and a fresh bridge incarnation are verified. Five local
cached rows were admitted in this isolated source context; normal fleet/device
adoption separately verifies both hosts. The real RLCD and 349 serial devices
are inaccessible through the fixture's masked directory and were never opened.
The private child/PID namespace terminated, releasing its tty and watch resources.
No borrowed provider credentials or native model turns were created.

Final candidate, baseline rollback and reselection again pass with healthy matched
device acknowledgements. The [final artifact capture](device-final.json) repeats
15-second feed windows around six seconds of silence: 14 healthy matched
acknowledgements per window, seven rows restored, all work claims cleared during
silence, and zero logged deadline misses. Its maximum frame is 16,380 microseconds.
The final installed artifact gate and complete chezmoi canonical check pass.
The later real USB transport check below supplements the isolated proof.
User-visible confirmation and reboot remain pending.

## Real USB disconnect and recovery

The [hardware transport receipt](physical-usb-recovery.json) records the known
RLCD at USB path `5-1.1.1` disconnecting at 19:42:56 PDT on October 13 and
re-enumerating at 19:43:01 with serial identity `94:A9:90:F3:43:74`. The same
bridge PID `1297804` observes hangup and absence, reopens the port at 19:43:03,
and admits fresh device requests starting from the new device counter.
Request/checksum/row-matched acknowledgements restore seven rows from both
current hosts. There are zero service restarts and zero render deadline misses
in the recovery window. The restored device reports healthy feed state.

These are actual kernel/bridge/device observations. They establish hardware
transport recovery without restarting the service; visible panel recovery still
awaits user confirmation. Starship's host boot ID remains unchanged.

## Rollback and remaining acceptance

Retained baseline bundle: `~/.local/share/rlcd-agent-dashboard/ab87015dbfc58201`,
manifest `ab87015dbfc582012e02b4d8aa0995148cb114624d6c3705bb158e646a0c9899`.
Its previously accepted bridge code comes from the `2ef1151` checkpoint; added
verification helpers are separately reflected by exact input hashes and the
manifest's dirty/mixed source marker. The rollback was exercised against the
same accepted producer dependency environment and followed by reselection.

Exact candidate/baseline selections, scoped render/diff/dry-run receipts, protected
before/after data, private logs and rollout helper remain under
`~/.cache/rlcd-reliability-20261013/`. To roll back, stop the application service,
restore the retained application selection, scoped apply the four targets,
reload/start and verify device admission. Provider, Observer/Mesh, Tmux and firmware
rollback are not involved.

The user has a pending request to confirm the visible roster after reconnect.
Reboot timing is separately pending because Starship
has active workloads. Enabled startup and service stop/start do not count as an
actual reboot. Previous physical readability remains accepted for the unchanged
layout. These local checkpoints and installed artifacts are unpublished.
