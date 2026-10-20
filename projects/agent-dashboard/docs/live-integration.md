# Live dashboard integration

The bridge's default source is Observer's explicit 72-hour working-set profile,
`agent-observer.mesh-working-set.v1`, delivered by Mesh as
`agent_working_set` from `mesh-plus-agent-working-set/read.sock`. The source
membership rule is eligibility AND (active OR recent): an active member remains
included even when its activity is older than 72 hours, while the independent
recent branch includes eligible parked or runtime-unknown conversations within
the window. This is feed membership, not display membership: the dashboard
requires current running-runtime evidence and excludes unloaded history, children
and system rows. A missing or
unsupported working-set route fails closed; it never falls back to another
source.

The configured Reader passes public `WorkingSetAgentProfile` reads through
`PreparedWorkingSetAgentWatch`. The adapter pairs each returned body with the
public `member_leases` entry using its complete exact identity. The lease export
supplies active/recent membership deadlines, the eligibility membership
deadline, and independent field deadlines. The bridge does not reconstruct
policy from raw support tables. `--roster` remains the explicit full-history
diagnostic using Observer's full `AgentProfile`, source `agent`, and
`mesh-plus-agent/read.sock`. Existing full API, snapshot/watch, service and
full-Agent routes remain available.

Observer owns native facts, classification and scope; Mesh owns delivery and
admission; this bridge owns display selection, labels, counts and retained
uncertainty; firmware owns packet admission, expiry, layout and animation. This
client performs no provider actions.

## Membership and presentation

An admitted row must have a current positive active or recent lease, eligible
kind and Codex provider. Active and recent deadlines remain independent. When a
source row is admitted under the active branch, its lease includes that deadline;
a source row admitted under the recent branch uses the recent deadline. This
source lease never bypasses the additional current-runtime display filter. If
the supporting branch expires before the next read, the display claim expires
with it, even if the other branch remains positive.

Each row lease is the minimum of its positive membership/category authority and
the exported deadlines for its currently displayed runtime, phase, outcome,
latest turn, activity and workspace. Informational title and cwd labels may be
retained with uncertain context; they do not establish freshness or current
work. Phase and activity age continue to use their original Observer support.
Age is time since conversation activity at the runtime's source-sampled
`observedAt`; reads, delivery proofs and bridge heartbeats cannot advance it.

Rows are selected only with current running-runtime evidence, independently of
last-turn outcome or recent-history membership. Loaded idle/waiting sessions are
included. Positively parked rows retire their prior display identity immediately;
new rows with unknown runtime are not introduced. Previously loaded rows whose
runtime becomes uncertain retain context with `?`, without a current work claim.

Rows are prioritized as attention, waiting, working, then unknown. Whole loaded
roster totals are computed before the first 32 rows are sent; 11 complete rows fit
the display and overflow remains explicit. Every current row has active display
category; the source's recent branch is not a display category. Historical
completion cannot establish readiness.

The five per-host totals are attention (blocked plus known current failures),
waiting, working, recent, and uncertain. The retained wire field for recent is
zero in this loaded-only view. Loaded rows with unknown or expired
display state and retained context count as uncertain. Host-total validity is
capped by the earliest membership, selected-category or current displayed-field
deadline across the whole counted roster, including rows beyond the 32-row USB
prefix. A row may keep a longer individual lease after the aggregate totals
expire; firmware then preserves that row while qualifying the host totals as
partial.

Header counts use the same 24-pixel font as the title and conversation rows.
Counts above 99 use `99+`; overflow uses `+99+`. The title abbreviates when
needed so the four visible totals and overflow fit without shrinking the numbers.
The header shows attention, ready, working and uncertain; unloaded recent-only
threads are excluded from the list and totals.

Fresh complete coverage may retire absent members only in its exact host,
provider and namespace. A current exact child/system or other positive
nonmember decision may retire its identity. Partial omissions, positive expiry,
producer pruning/overflow and missed negatives retain existing context as
uncertain. There is no context timeout or fallback negative inference. Healthy
hosts remain useful when a sibling fails, and a missing host cannot make the
whole fleet appear complete.

## Device wire 4

USB carries ASCII LF-delimited protocol records alongside boot and diagnostic
logs. Only tagged records enter the protocol. A device request is:

```text
RLCD?4 <16 lowercase hex boot nonce> <positive request number>
```

Responses are tab-separated ASCII with this field order:

```text
RLCD!4 boot request bridge sequence host_count row_count
  [alias_hex status valid_ms attention waiting working recent uncertain total] per host
  [identity_sha256 host_index badge_hex category work health valid_ms label_hex age] per row
  crc32
```

Each response is one physical line. CRC32 covers all bytes before the final
tab/checksum. Text fields are lowercase hex UTF-8 bytes; ages are `?`, `+++`, or
a bounded number with s/m/h/d. Category codes are 0 active, 1 recent and 2
uncertain. Work codes are 0 working, 1 blocked, 2 waiting, 4 derived error,
5 unknown and 6 parked. Health codes are 0 current, 1 stale, 2 unavailable,
3 ambiguous and 4 unsupported. Host status is 0 current, 1 partial, 2 offline
and 3 warming.

Limits are 16 KiB per response, 32 rows, two configured hosts, 63 UTF-8 label
bytes and 65,535 selected identities per host. All fields, counts, enums,
encodings, duplicate identities and checksums validate before mutation.
Truncated, excessive or malformed lines are discarded. Wire 2 and wire 3 records
are rejected by the wire 4 firmware and bridge.

The per-row badge is normally its physical host alias (`ST` or `SN`). `SW` is
allowed only for a Snap row and denotes the trusted `work` profile. It changes
only the left-hand display badge. Native identities, the two physical host
slots, per-host totals, expiry and row ordering remain unchanged. The receiver
checks the badge/host association before mutation.

Firmware requests the latest view every second. A response must match the
current boot/request and arrive within that request's one-second window; each
request is consumable once. A bridge restart changes its random incarnation,
and sequence must increase within an incarnation. Every accepted view is a
replacement.

The bridge rechecks Mesh admission on each request. Leases are capped at three
seconds and reduced by a 100 ms safety margin. Firmware anchors row and host
expiry to request-send time, not response-receive time, so transport latency
shortens authority. Host totals and individual row leases expire independently.
Firmware checks expiry during silence without another packet. Expired rows
stop flashing and lose current work and age claims; uncertain identity context
can remain visible. If a host expires, healthy sibling rows remain available.

The host's retained identity cache is bounded and never grants native facts.
The bridge supervises subscription and serial workers, retries expected source
loss with lease revocation, and treats unexpected worker exit or cleanup failure
as an owner failure after bounded cleanup. Missing or busy hardware is retried;
hangup closes framing before a fresh serial incarnation.

## Acceptance and rollback

Native admission, projection, working-set lease, Python runtime, bundle and
motion checks cover deterministic behavior. Installed source and artifact
identity, configured host routes, bundle installation, device ACK/silence /
recovery, and physical readability are separate acceptance gates. Preview,
serial ACK and readback do not establish physical readability.

The current bridge and firmware require the paired wire 4 contract. Archived
wire 2 and wire 3 bundles and firmware remain immutable; rollback must select
a matching bridge/firmware pair and its source/client selections. Do not mix
wire versions. A wire-4 badge rollback does not require a producer restart. The earlier
[active-feed receipt](../../../docs/evidence/2026-10-16-active-feed/REPORT.md)
records the prior wire 2 rollout and its own rollback evidence. Tmux, 349,
ordinary native sessions and historical writers remain independent.
