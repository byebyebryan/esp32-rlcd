# Roster ordering and state transitions

Date: 2026-10-02. Design captured below. Update 2026-10-03: synthetic sorting
and animation are implemented in the separate dashboard example; native checks
and both firmware builds pass. [The motion proof](ui-motion.md) records behavior
and evidence. The first motion prototype passed a complete on-board timing
trace after USB reconnection. Physical feedback requested shared progress for
all row paths, with upward rows in front and downward rows behind. That refinement
is now flashed, passes native checks and a new complete timing trace, and is
accepted on the panel for easier tracking. Attention rows keep their inverse style and status icons
retain their original polarity.
See [the earlier layout study](ui-study.md).

## Agreed ordering

The user chose these groups, in descending urgency:

1. Waiting for attention.
2. Waiting for a prompt / idle.
3. Running.

Within **every group**, the user chose oldest state first. Age means time
since entering the current state, not session lifetime, last observation,
file modification time or the latest successful poll.

Proposed treatment of the other existing presentation states:

| Observed state | Placement |
| --- | --- |
| Needs input | Attention group, persistent inverse row |
| Error requiring intervention | Attention group, persistent inverse row |
| Settled / awaiting a new prompt | Idle group |
| Interrupted but still an available interactive session | Idle group, retaining the stopped symbol |
| Working | Running group |
| Stale, unavailable, conflicting, unsupported or unknown state | Separate uncertain section; never classified using a cached work state |

A terminated runtime is not automatically an idle interactive session.
The live-roster inclusion policy must distinguish it from saved history or
retained jobs. Errors and interrupted-session placement above are proposals
to validate against the eventual observer capabilities.

## Age and stable ordering

Sort the selected live roster by group, then decreasing known state age.
Equal ages preserve the prior relative order. Give new equal-age entries a
stable admission order; titles and directory names are not identity keys.
Unknown ages display `?` and follow known ages within the same group, with
stable relative ordering rather than invented timestamps.

Examples:

| Transition | Immediate state/age change | Ordered destination |
| --- | --- | --- |
| Approval or blocking question answered | Needs input → running, age resets | End of running group |
| New prompt sent to an idle session | Idle → running, age resets | End of running group |
| Response settles | Running → idle, age resets | End of idle group |
| New blocking input wait | Running → needs input, age resets | End of attention group, below older waits |

These moves depend on an authoritative observation of the new state. The
RLCD does not infer that a question was answered or send prompts itself.
Settled/idle does not assert task success.

Ordinary age ticks do not change relative order: all uninterrupted state ages
increase together. Repeated snapshots must not reset age or trigger movement.
A distinct state episode can reset age even when the display label is the
same, but only if the source establishes that distinction. Timing recovered
after an observation gap must retain its actual provenance or remain unknown.

The earlier static demo's preformatted strings such as `45S` are insufficient for
sorting. The motion proof uses numeric fixture entry times and explicit episodes.
Live inputs need a trustworthy numeric state duration or entry
time with provenance, plus stable hidden logical identity. Missing timing
support must remain explicit; `state_observed_at` is not a substitute for
state entry time.

## Transition presentation

Apply the new icon, attention highlight and header counts as soon as a valid
state update is accepted. For an answered wait, remove the attention highlight
immediately; the row must not keep showing a blocked state during animation.
Status icons keep their original polarity, including white-on-black waiting
and error symbols.

The prototype uses a 360 ms vertical slide to the new ordered position, while
displaced rows slide into the vacated slots. Use one shared ease-out progress
for each row's own starting and destination positions. The scheduler targets
25 frames/s and rounds positions to whole pixels. The on-board write cadence
is measured separately from physical animation acceptance.

Keep the header and footer stationary. Clip moving content to the roster
area. Moving rows need an opaque background and deliberate foreground order
so crossing rows do not superimpose their text. Draw downward rows first,
stationary rows next, and upward rows last, with direction determined by the
start/destination geometry. A direct reorder remains the fallback if motion
reduces readability.

Retain eight rows without separate group-title rows. Try a small two-pixel gap
at group boundaries; even three boundaries fit the existing roster area.
Attention highlights and state symbols already distinguish the groups.

Age-only text changes do not animate. The first snapshot after boot appears
directly, without eight entrance animations. A brief new-wait attention pulse
is a separate proposal; do not combine it with the first movement experiment.

## Rapid changes, overflow and observation loss

- Track movement by host/provider/native logical identity, not visible name,
  short ID, worker PID or array index. Explicit same-project labels remain
  presentation hints.
- Keep only the latest target layout. A new update during movement changes
  state immediately and retargets from the current displayed positions;
  never queue a sequence of obsolete waits/runs.
- Sample updates at frame boundaries and accept new state promptly. If updates
  keep interrupting movement, snap to the latest layout within the 720 ms burst
  limit rather than extending animation indefinitely. The prototype has no
  separate coalescing timer.
- Apply priority before the eight-row visible limit. A newly waiting session
  can enter the visible roster and displace a lower-priority row. Keep overflow
  counts explicit, including when more than eight sessions need attention.
- Individual uncertain entries belong in the marked uncertain section.
  If the entire feed becomes unavailable, freeze the last layout, replace
  cached state indicators with source-health indicators, suppress misleading
  counts/ages and cancel motion. Frozen positions are historical layout,
  not assertions of current group membership.

## Responsibilities and bounded proof

Agent Observer supplies factual identity, state, timing capabilities and
observation health. RLCD host-bridge policy selects the live roster and its
urgency/age order. Firmware owns pixel layout and optional motion. These
requirements do not freeze the observer wire schema or move display-specific
priority rules into the shared component.

The implemented bounded UI proof uses numeric synthetic state ages and explicit
fixture identities without waiting for the live data source. Its original checks were:

1. Prove group/age ordering, stable ties, unknown-age handling and age reset
   for the four transitions above. Repeated snapshots must preserve age/order.
2. Render one answered-wait move, verifying correct endpoints, immediate
   state/highlight changes, clipping and fixed status-icon polarity.
3. Exercise idle → running, running → attention, running → idle, concurrent
   changes, overflow admission and source loss. Compare native previews with
   the board at actual viewing distance.

The existing SPI transport stays at 10 MHz with queued full-frame writes and
one framebuffer owner. The measured [UI/transport evidence](ui-study.md)
suggests room for a short animation, but does not prove its visual smoothness
or performance. Record actual draw/transfer times and any missed frame targets
before adopting the motion.
