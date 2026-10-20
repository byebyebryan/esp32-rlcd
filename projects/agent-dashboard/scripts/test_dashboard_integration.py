#!/usr/bin/env python3
"""Run the required installed Observer/Mesh two-home integration gate."""

import importlib.util
import os
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = APP_ROOT / "tests" / "test_home_profiles_public.py"
WORKING_SET_PROFILE = "agent-observer.mesh-working-set.v1"
EXPECTED_CASES = 3


def fail(message, *, status=2):
    print(f"ERROR: strict dashboard integration gate: {message}", file=sys.stderr)
    raise SystemExit(status)


missing = [
    name
    for name in ("agent_observer", "mesh_plus")
    if importlib.util.find_spec(name) is None
]
if missing:
    fail(
        "the selected interpreter "
        f"{sys.executable} lacks {', '.join(missing)}; set PYTHON to the installed "
        "Observer/Mesh environment for this gate"
    )

try:
    import agent_observer
    import mesh_plus
    from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
    from agent_observer.mesh_working_set_read import PreparedWorkingSetAgentWatch
    from mesh_plus.api import Reader
except Exception as error:
    fail(
        "the selected Observer/Mesh environment is missing a required integration "
        f"API ({type(error).__name__}: {error})"
    )

prefix = Path(sys.prefix).resolve()
package_paths = {
    "agent_observer": Path(agent_observer.__file__).resolve(),
    "mesh_plus": Path(mesh_plus.__file__).resolve(),
}
for package, path in package_paths.items():
    try:
        path.relative_to(prefix)
    except ValueError:
        fail(
            f"{package} resolved outside the selected interpreter prefix: {path}; "
            "remove source checkouts from PYTHONPATH"
        )

if not callable(getattr(Reader, "watch_admitted", None)):
    fail("Mesh Reader.watch_admitted is unavailable")

try:
    profile = WorkingSetAgentProfile()
    if profile.descriptor.profile_id != WORKING_SET_PROFILE:
        fail("Observer constructed an unexpected working-set profile descriptor")
    admission = PreparedWorkingSetAgentWatch(
        "0" * 32,
        host_ids=["dashboard-integration-preflight"],
        profile=profile,
    )
    admission.disconnect()
except SystemExit:
    raise
except Exception as error:
    fail(
        "the installed working-set profile or prepared admission API is incompatible "
        f"({type(error).__name__}: {error})"
    )

print(
    f"Observer {getattr(agent_observer, '__version__', 'unknown')}: "
    f"{package_paths['agent_observer']}"
)
print(
    f"Mesh {getattr(mesh_plus, '__version__', 'unknown')}: "
    f"{package_paths['mesh_plus']}"
)
print("PASS: working-set profile construction and prepared admission are available")

os.environ["RLCD_RUN_PUBLIC_INTEGRATION"] = "1"
spec = importlib.util.spec_from_file_location("dashboard_home_profiles_public", TEST_PATH)
if spec is None or spec.loader is None:
    fail(f"cannot load integration test module: {TEST_PATH}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
try:
    spec.loader.exec_module(module)
except Exception as error:
    fail(
        "the integration test could not import its required public APIs "
        f"({type(error).__name__}: {error})"
    )

suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.skipped:
    fail(f"{len(result.skipped)} integration test(s) were skipped", status=1)
if result.testsRun != EXPECTED_CASES:
    fail(
        f"expected {EXPECTED_CASES} two-home cases, ran {result.testsRun}",
        status=1,
    )
if not result.wasSuccessful():
    raise SystemExit(1)
