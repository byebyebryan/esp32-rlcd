# Dashboard test gates

`scripts/test-live-dashboard.sh` is the dependency-free native and Python test
gate. It compiles the local C feed harness, then discovers every
`tests/test_*.py` test with the selected interpreter. Set `PYTHON` to choose a
Python executable. It needs no installed Observer or Mesh package; SDK-specific
acceptance cases report labeled skips when those packages are absent. Test files
added under `tests/` are picked up by discovery automatically.

The public two-home Observer/Mesh integration has its own strict gate:

```sh
PYTHON=/home/bryan/.local/share/agent-observer/0.7.0a7-a3983afc-ws72-m4f598719/bin/python \
  ./projects/agent-dashboard/scripts/test-dashboard-integration.sh
```

The gate requires the selected Python environment to contain installed
`agent_observer` and `mesh_plus` packages. It rejects packages loaded from a
source checkout or outside that interpreter's prefix, checks that the
working-set profile, public frame composition, and prepared admission guard are
available, then runs twelve required cases: nine installed working-set fleet
lifecycle cases and the three public two-home cases. Any skip, missing case,
API mismatch, or assertion failure exits nonzero. It does not modify
`PYTHONPATH` or import an Observer/Mesh sibling checkout. The tests use
synthetic fixture data and disposable Unix sockets where needed.

The public two-home cases are excluded from ordinary discovery even when an SDK
happens to be installed; only the strict command opts them in. To direct the
native harness output elsewhere, set `RLCD_TEST_OUTPUT_DIR` when running
`test-live-dashboard.sh`.

The nine fleet cases use the installed Observer `ServiceState` working-set
frames and Mesh's public reader composition and admission APIs. They cover
selected-view parity with explicit full diagnostics, complete-empty and partial
scope expiry, independent activity and runtime support, rejected receipt
replacement, exact exclusion beyond the 32-row display limit, namespace and
sibling isolation, stream control failures, and reconnect cleanup. Ordinary
dependency-free discovery labels these installed cases as optional skips; the
strict command requires all nine to execute.

The three cases cover two distinct Codex home namespaces on one host with the
same native ID, independent expiry and close, rejection of a valid frame bound
to the wrong home while its sibling remains current, and preservation of a
default row when the Work scope is complete but empty. The fixture's source and
byte hash are recorded in
[`tests/fixtures/service-v4/PROVENANCE.md`](../tests/fixtures/service-v4/PROVENANCE.md).

The hosted native job runs the dependency-free gate. Hosted strict SDK
qualification is pending a compatible Mesh working-set source revision becoming
publicly reachable; the workflow does not substitute a released SDK that lacks
the registered profile. The installed-runtime command above is the current
strict integration acceptance gate.
