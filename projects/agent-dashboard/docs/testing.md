# Dashboard test gates

`scripts/test-live-dashboard.sh` is the dependency-free native and Python test
gate. It compiles the local C feed harness, then discovers every
`tests/test_*.py` test with the selected interpreter. Set `PYTHON` to choose a
Python executable. It needs no installed Observer or Mesh package; SDK-specific
acceptance cases report labeled skips when those packages are absent. Test files
added under `tests/` are picked up by discovery automatically.

The reproducible SDK input is
[`sdk-release-lock.json`](../sdk-release-lock.json). It records the public
Observer `0.7.0a8` and Mesh `0.1.0a24` wheel URLs and SHA-256 values, their
release source metadata, and the pinned transitive wheels for the qualified
CPython 3.11/3.14 Linux x86_64 environments. The installer verifies each wheel
before local-only, dependency-free pip installation; it has no source-checkout
or index fallback. Verify the installed versions, wheel-origin hashes, and
public API before running the strict gate. The installer currently supports
CPython 3.11 or 3.14 on Linux x86_64:

```sh
python3.14 -m venv .venv/dashboard-sdk
.venv/dashboard-sdk/bin/python projects/agent-dashboard/scripts/install-sdk.py
.venv/dashboard-sdk/bin/python projects/agent-dashboard/scripts/verify-sdk.py
```

Use Python 3.11 in the first command to qualify that supported interpreter.

The public two-home Observer/Mesh integration has its own strict gate:

```sh
PYTHON=/path/to/qualified/python \
  ./projects/agent-dashboard/scripts/test-dashboard-integration.sh
```

The gate requires the selected Python environment to contain installed
`agent_observer` and `mesh_plus` packages. It rejects packages loaded from a
source checkout or outside that interpreter's prefix, checks that the
versions and wheel-origin SHA-256 values match the committed release lock, and
the working-set profile, public frame composition, and prepared admission guard
are available, then runs twelve required cases: nine installed working-set fleet
lifecycle cases and the three public two-home cases. Any skip, missing case,
API mismatch, or assertion failure exits nonzero. It does not modify
`PYTHONPATH` or import an Observer/Mesh sibling checkout. The tests use
synthetic fixture data and disposable Unix sockets where needed.

The public two-home cases are excluded from ordinary discovery unless
`RLCD_RUN_PUBLIC_INTEGRATION=1`; the strict command sets this internally. Set
`RLCD_REQUIRE_ZERO_SKIPS=1` to make the complete suite fail on any skipped test.
The hosted SDK job sets both variables so the full installed suite executes
every case with no skips. To direct the native harness output elsewhere, set
`RLCD_TEST_OUTPUT_DIR` when running `test-live-dashboard.sh`.

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

The hosted `sdk` job installs the exact locked public pair on CPython 3.11 and
3.14, verifies the installed wheel hashes and public APIs, then runs both the
strict twelve-case gate and the complete dashboard client suite. The native job
continues to exercise the dependency-free path.
