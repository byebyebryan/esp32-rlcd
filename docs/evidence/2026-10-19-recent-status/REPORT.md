# Recent conversation status correction

Snap's working-set feed showed `mesh-plus` with a neutral dash. A passive native
read of the same identity confirmed `notLoaded`, absent from loaded inventory,
and a completed latest turn. Delivery was current; the bridge unconditionally
replaced every known parked result with the neutral marker.

Runtime source `71726b08c439a27e3bb92fd33439a2a389409bb4` preserves runtime and
membership facts while showing the last terminal result: agreeing current
outcome/latest-turn completion uses the ready check, and failure uses the error
cross. Recent-only rows still count only as recent and have no active styling.
Missing, stale, conflicting or interrupted results retain the neutral marker;
original field leases and device expiry still apply.

The new regressions fail twice against the previous projection. All 71 dashboard
checks pass without skips on Python 3.14.8 and 3.11.17, including native C packet
admission and expiry. The immutable bundle is `c638c29d0f779017` and keeps the same
Observer/Mesh wheel pair and wire 3. No firmware rebuild or flash was performed.

Only Snap's managed dashboard selection/unit were applied and its bridge was
restarted. A live configured read produces a ready check for the recent mesh-plus
row; the device acknowledges frames and reports 11 healthy rows, zero misses,
and no restart failures. Observer, all three Agent publishers and 349 service
incarnations remain exact. Starship's client selection is unchanged. The old
bundle and deployed-file preimages remain available for rollback.

[Receipt](receipt.json) pins the bundle, bounded observations, test logs and
post-activation diagnostics. Device acknowledgements and native parser tests do
not claim a new manual panel or reboot qualification. Source/config commits are
local and have not been published to GitHub by this correction.
