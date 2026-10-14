# Live dashboard reliability refinement plan

The dashboard already consumes real Codex observations from Snap and Starship,
and its names, host badges and activity ages have physical readability acceptance.
This pass makes the host bridge recover predictably, gives Starship durable
startup, and repairs whole-roster counts during partial inventory. Planning
status: implementation and managed rollout are pending.

The [integration contract](live-integration.md) and
[accepted refinement receipt](../../../docs/evidence/2026-10-13-dashboard-refinement/REPORT.md)
remain the baseline. Observer 0.7.0a1 / API 4 / snapshot-watch 6 / Service 4 and
Mesh 0.1.0a17 / Agent v3 / SDK 1 stay pinned. Device wire 1 and the accepted
24-pixel layout remain the target. A new producer contract or firmware revision
requires a demonstrated defect and its own review.

## Scope and ownership

Application changes belong in `projects/agent-dashboard`: host projection,
subscription supervision, serial lifetime, diagnostic output, tests, installation
support and operation documentation. Starship deployment selection and the
user-unit templates belong in chezmoi. The permanent unit uses the existing name
`rlcd-agent-dashboard.service` and the stable RLCD serial identity
`94:A9:90:F3:43:74`. Snap remains a remote observation source.

Keep provider sessions/settings, Tmux owners and factories, the historical writer,
ESP32-349 service/device and unrelated source/deployment edits intact. Preserve
the existing dirty dashboard integration while preparing scoped checkpoints.
Source publication is a separate delivery step.

## Execution checkpoints

1. **Capture the baseline and reproduce the failures.** Record current source
   changes, the transient unit, its exact command/dependency prefix, both source
   statuses, stable serial owner and a bounded healthy device receipt. Retain
   a runnable bridge bundle for rollback before service replacement. Add
   regressions for the two reproduced code defects and serial lifetime tests
   using disposable endpoints. These tests must exercise behavior without
   touching ordinary provider sessions or the live serial owner.

2. **Repair whole-roster membership and counts.** Maintain bounded identity
   membership separately from the 32-row USB prefix and 11 visible rows. Retain
   enough minimal identity/label metadata to reconcile previously selected
   sessions, with a hard per-host bound matching the existing 65,535 roster
   limit. Expired or unproved members supply uncertain context, never cached
   phase or age authority. A partial omission preserves uncertain membership;
   accepted complete omission can retire display membership. Positive child,
   system or parked classification removes the identity from membership,
   retained labels, counts and overflow even beyond the device prefix. Newly
   observed eligible identities are counted once. Capacity exhaustion produces
   an explicit finite failure rather than silent eviction or false totals.

3. **Supervise the subscription and serial workers.** One supervisor owns their
   lifetime. Expected Mesh disconnection uses bounded retry and existing lease
   revocation; an unexpected worker exit or cleanup failure cannot leave an
   apparently healthy bridge with a dead subscription. Terminate the bridge
   with a finite failure code after bounded cleanup so the service can recover.
   Handle normal stop/cancellation and SIGTERM by closing the subscription and
   serial descriptor and releasing exclusive ownership. Preserve healthy
   siblings during an individual host failure.

4. **Implement USB absence and reconnection.** Open only the reviewed stable
   serial path. Detect hangup/device removal as well as read/write errors;
   ordinary no-data reads are not themselves a disconnect. Close obsolete
   descriptors and clear partial input/request state before reopening with
   bounded backoff. A fresh serial incarnation uses a fresh bridge identifier
   and the current device boot/request, and does not renew source evidence.
   A busy port never authorizes taking ownership from another process. Stop
   requests interrupt retry promptly. Device silence continues to revoke work
   styling and ages through the existing firmware expiry path.

5. **Add bounded operational diagnostics.** Emit finite events for source
   connect/retry, worker failure, serial missing/busy/disconnected/recovered,
   and normal stop. Include source health, last valid request/acknowledgement,
   and retry state where relevant. Distinguish bridge-to-device feed health
   from native observation health; a transport acknowledgement does not prove
   current native work state. Repeated failures use limited logging. Keep raw
   provider payloads, authentication and conversation bodies out of diagnostics.

6. **Freeze and install the host runtime.** Create a small versioned immutable
   bundle containing the bridge modules and font data needed by label metrics.
   Verify its hashes and the accepted Observer/Mesh dependency tuple. The
   production unit runs this installed bundle rather than the mutable checkout.
   Preserve a foreground entry point for bounded diagnostics and captures.
   Configuration, selected artifact, source revision and actual installed
   runtime have separate provenance.

7. **Deploy the Starship user service.** Render and validate only the new
   Starship unit, startup link and application selection/configuration targets.
   Startup follows the user manager's default target; Starship already has
   `Linger=yes`, so this pass does not alter account lingering. Startup must
   tolerate an absent device or unavailable source and recover when it appears.
   Retry/start-limit settings must permit prolonged absence without leaving
   the feed permanently stopped. Stop timeout must cover bounded cleanup.
   Stop the transient owner, verify serial release, replace it with the
   persistent unit and start exactly one owner. Avoid hard dependency coupling
   that suppresses a healthy remote source during a local service outage.

8. **Accept operation and retain rollback evidence.** Run the regression and
   live gates below, verify installed/source selection agreement, update the
   operation guide and record bounded evidence. Exercise rollback to the
   retained bridge bundle/dependency pin, then reselect the candidate. Restore
   the exact prior scoped deployment targets if rollout fails. Rollback does
   not require a provider restart, producer downgrade or firmware flash.

## Acceptance gates

| Area | Required result |
| --- | --- |
| Counts and membership | Forty selected identities followed by a five-row partial inventory report five current and 35 uncertain members, total 40. Whole-feed loss keeps total 40 as uncertainty. Positive exclusions and accepted complete omissions reduce membership exactly once. |
| Capacity and recovery | Exercise 11, 32 and larger rosters; partial views, repeated loss, new identities and reclassification beyond the USB prefix. Counts and overflow agree with membership through recovery. The hard roster bound fails explicitly. |
| Worker lifetime | Inject stream iteration, cleanup and unexpected return failures. The supervisor retries expected failures or exits visibly; no dead worker remains behind an active serial loop. Cancellation/stop closes owned resources. |
| USB lifetime | Simulate absent startup, busy ownership, hangup, fragmented input, reappearance and a new device boot nonce. Recovery admits only fresh requests and preserves exclusive ownership. |
| Native and projection regression | Existing title/fallback/collision, system filtering, source-sampled age, phase/outcome separation, source expiry and healthy-sibling checks continue to pass. Renderer/motion and C admission checks pass. |
| Installation and service | Bundle hashes/dependency tuple agree; unit configuration validates; startup, prolonged absence, stop/start and rollback/reselection succeed with one serial owner and no unrelated managed drift. |
| Live device | Healthy acknowledgements match sent request/checksum/rows. Bridge stop clears work claims; restart recovers. A failed source expires while its healthy sibling remains useful. Capture bounded render/heap/stack diagnostics. |
| Physical operation | Confirm actual unplug/replug and visible offline/recovery behavior in a coordinated hardware window. Record a real host reboot separately from simulated startup and unit enablement checks. |

Use deterministic fake clocks/endpoints for the new failure cases, with finite
timeouts. Device interaction is exclusive and sequential. Preserve the known
RLCD identity and separate 349 serial/service. The existing accepted readability
does not need a new layout study unless this pass changes visible presentation.

## Completion and boundaries

Acceptance requires repaired membership, supervised workers, tested USB recovery,
a verified installed bundle, enabled Starship startup, scoped rollback and the
live/physical operation receipts. Report physical unplug/replug or reboot checks
as pending until actually performed. A host reboot needs a coordinated window
because other active workloads must be preserved.

Prepare scoped local commits around application logic/tests, installation and
managed deployment, and acceptance documentation. Producer fixes already reside
on their isolated accepted branches; merging or publishing those branches and
the dashboard changes has separate review and remote-delivery status.
