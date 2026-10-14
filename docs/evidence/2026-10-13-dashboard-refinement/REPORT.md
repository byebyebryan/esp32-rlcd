# Dashboard classification and naming refinement

The refined live dashboard is accepted on the RLCD. The user confirmed
**“Looks readable”** for conversation names, ST/SN badges and activity ages at
normal viewing distance. [Acceptance metadata](acceptance.json) and the
[device capture](device.json) separate producer, bridge, serial and physical
evidence. The [initial live implementation](../2026-10-13-live-dashboard/REPORT.md)
retains its original firmware/flash bounds.

## Result

- Known system helpers, children and positively parked sessions are excluded
  from selected rows, retained context, whole-roster counts and overflow.
  Running historical unknown kinds remain eligible.
- Useful conversation titles precede repository/cwd fallbacks. Blank and generated
  `Codex <native ID>` titles use bounded fallback labels. Rendered collisions
  first use distinguishable project context, then stable identity suffixes.
  Renames preserve identity and animation continuity.
- Two real Starship user conversations share the title `agents` and project.
  Short suffixes distinguish their identities. Idle daemon sessions remain
  running/waiting regardless of old conversation activity age.
- `live-dashboard.py --roster` maps every selected label to its full native
  identity and explains selection, sampled ages, device and visible capacity.
  `--all` includes saved/excluded metadata. Retained uncertain context preserves
  identity without claiming current activity or work state.

## Producer selection

Snap and Starship select Observer **0.7.0a1**, API **4**, snapshot/watch **6**,
Service **4**, Mesh **0.1.0a17**, SDK **1**, and explicit Agent profile **v3**.
The sibling producer repository has `docs/api-v4.md` and independent acceptance
at `docs/evidence/2026-10-13-system-classification/REPORT.md`. Known
`threadSource=system` classification survives raw observations; ordinary read
rosters hide it with explicit diagnostic access.

Producer checks pass: 401 Observer tests, 117 Mesh tests, strict installed API
and package verification, 7 profile plus 10 network conformance cases per host,
controlled native system/persistence cases on both hosts, private service/slow
reader checks and paired rollback/reselection. Normally selected two-host Agent
v3 and independently owned Tmux v1 snapshot/watch, remote proof, expiry and
cleanup pass. No ordinary provider action was performed.

Cached metadata remains a source observation. Fresh native reads can have newer
`lastUpdated` values during work; the panel age still means source-sampled
conversation activity and never uses delivery time or native thread-update time.

## Bridge, renderer and device

The live gate passes **22 tests**, including source expiry, partial/complete
membership, positive system reclassification, collisions/renames, full roster
diagnostics, 32 transported versus 11 visible rows, and malformed/duplicate/
delayed input. C admission runs with address/undefined-behavior sanitizers.
Existing motion/font/framebuffer checks pass, including 4,488 packed rectangle
comparisons and source-loss/identity/atomic-layout behavior. The exact C-rendered
400 × 300 live preview was inspected for clipping.

The final device capture uses stable identity `94:A9:90:F3:43:74` without reset
or flashing:

| Phase | Result |
| --- | --- |
| Initial 20-second live feed | 18 healthy checksum/request-matched acknowledgements; eight rows |
| Six seconds of bridge silence | Eight identities retained as unknown; blocked/waiting/working counts zero |
| Restarted 20-second feed | 18 healthy matched acknowledgements; all eight rows recover |
| Render health | Maximum 17,413 µs frame; zero deadline misses; minimum internal heap 292,171 bytes; stack watermark 4,776 |
| Physical readability | User accepted names, host badges and ages |

This refinement changes host projection/read diagnostics and documentation.
Device wire **1**, the accepted 24-pixel row layout, renderer and flashed firmware
remain unchanged. App image SHA-256:
`9945cab1b297440fc2a935f1d783ca29ce65e1e50100a77d373cf00e9c6abcfb`.
The original full-flash backup remains outside Git under
`~/.local/state/esp32-rlcd/backups/20261013T220340Z-94a990f34374-live/`.
The separate ESP32-349 serial device/services were untouched.

The foreground live bridge was restored after capture, but later exited and the
user observed FEED OFFLINE. Observer/Mesh services on both hosts remained healthy;
the serial port had no owner. The bridge was restored under the transient user
unit `rlcd-agent-dashboard.service`, independent of the tool terminal lifetime.
It uses the selected Python and stable serial identity, with restart on failure.
Fresh device acknowledgements match request/checksum and report feed health zero,
seven current roster rows and no render deadline misses. The changed roster size
reflects a fresh source observation, not a restoration of cached membership.

Inspect with `systemctl --user status rlcd-agent-dashboard.service` and
`journalctl --user -u rlcd-agent-dashboard.service`; stop with
`systemctl --user stop rlcd-agent-dashboard.service`. This transient unit is not
enabled for boot. The previous foreground log remains in ignored build output.
Preview, raw roster and serial logs remain in local build/cache/journal storage;
repository evidence contains bounded metadata only.

Source publication and permanent bridge service/reconnect policy remain
separate. Producer rollback was exercised and retains the previous 0.6.0a2/Mesh
a16 prefix plus exact per-host paired baselines under
`~/.cache/agent-dashboard-refine/paired-baseline.json`.
