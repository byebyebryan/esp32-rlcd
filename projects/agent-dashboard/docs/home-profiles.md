# Codex home profiles

The host bridge can combine explicitly configured Codex homes on one real host.
Each route has an independent public Reader, prepared guard and receipt/clock
lifetime. Rows retain their full host/provider/namespace/native-kind/native-ID
identity. Session titles stay plain, without a profile prefix. Same native UUIDs
in different home namespaces remain distinct, and matching titles use the
existing collision suffix. Starship Default displays `ST`, Snap Default `SN`,
and Snap Work `SW`. These are row display badges; Work remains part of Snap
for identity, totals and source admission. An uncertain Work row retains `SW`.
Profile health remains available in diagnostics.

Pass a private, owned JSON file with `--profiles-config PATH`. Its version 1
object contains `routes`, each with exact fields `host`, `profile`, `label`,
`codex_home`, `source` and `socket`. Hosts are Snap or Starship, with at most two
profiles each and four routes total. The managed deployment derives this file
from its Observer home declaration. The bridge rejects duplicate bindings,
homes, source IDs and sockets. Admitted owner provenance must match the exact
configured home and namespace before rows or completeness are used.

With no filter all configured routes for `--hosts` are combined. Add `--profile
work` or `--profile default` to select a subset; a host without that profile is
omitted. `--inspect` reports selected rows and per-profile health without opening
USB. Full diagnostics still use each profile's explicit Observer service socket;
`--roster` is the retained single-default full diagnostic path.

The loaded-session filter and 32-row device bound apply after the union. A
profile outage makes combined coverage partial but does not shorten another
profile's row leases. Its old rows become uncertain context. Complete-empty or
negative coverage affects only the admitted namespace. Refreshing, closing or
reconnecting one route cannot renew or reset another route's clock state.

Stopping the bridge closes all owned watches; ordinary route failures retry
independently. Failure to clean up an owned worker reaches the supervisor. The
default invocation without `--profiles-config` retains its previous route and
projection. The `SW` badge uses the paired wire-4 bridge/firmware extension;
no generic Mesh API or native Observer wire contract changes are required.

Validation includes the existing native wire/serial/supervisor/bundle suite,
profile configuration and composition cases, and actual disposable Observer
Runtime -> publisher -> IPC -> public Reader/facade tests. These cover repeated
native IDs, independent expiry and closure, one-host wrong-home refusal,
complete-empty scoping, plain titles, filters and post-union capacity. They do not
claim new physical panel, fleet capacity or provider lifecycle acceptance.
