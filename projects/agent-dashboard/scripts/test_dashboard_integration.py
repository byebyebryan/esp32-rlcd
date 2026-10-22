#!/usr/bin/env python3
"""Run the required installed Observer/Mesh working-set integration gate."""

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
TEST_PATHS = (
    ("dashboard_home_profiles_public", APP_ROOT / "tests" / "test_home_profiles_public.py"),
    ("dashboard_working_set_fleet", APP_ROOT / "tests" / "test_working_set_fleet.py"),
)
WORKING_SET_PROFILE = "agent-observer.mesh-working-set.v1"
EXPECTED_CASES = 12


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
    from agent_observer.service_state import ServiceState
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

try:
    locked_sdk = subprocess.run(
        [sys.executable, str(APP_ROOT / "scripts" / "verify-sdk.py")],
        capture_output=True,
        text=True,
        timeout=30,
    )
except (OSError, subprocess.SubprocessError):
    fail("could not verify the selected interpreter against the committed SDK lock")
if locked_sdk.returncode != 0:
    fail(
        "the selected Observer/Mesh versions or wheel hashes do not match "
        "sdk-release-lock.json"
    )
print(locked_sdk.stdout, end="")

if not callable(getattr(Reader, "watch_admitted", None)):
    fail("Mesh Reader.watch_admitted is unavailable")
if not callable(getattr(Reader, "compose_admitted", None)):
    fail("Mesh Reader.compose_admitted is unavailable")
if not callable(getattr(ServiceState, "working_set_frame", None)):
    fail("Observer ServiceState.working_set_frame is unavailable")

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
print("PASS: working-set profile, public frame composition, and prepared admission are available")

os.environ["RLCD_RUN_PUBLIC_INTEGRATION"] = "1"
modules = []
for module_name, test_path in TEST_PATHS:
    spec = importlib.util.spec_from_file_location(module_name, test_path)
    if spec is None or spec.loader is None:
        fail(f"cannot load integration test module: {test_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        fail(
            "the integration test could not import its required public APIs "
            f"({type(error).__name__}: {error})"
        )
    modules.append(module)

suite = unittest.TestSuite(
    unittest.defaultTestLoader.loadTestsFromModule(module)
    for module in modules
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.skipped:
    fail(f"{len(result.skipped)} integration test(s) were skipped", status=1)
if result.testsRun != EXPECTED_CASES:
    fail(
        f"expected {EXPECTED_CASES} integration cases, ran {result.testsRun}",
        status=1,
    )
if not result.wasSuccessful():
    raise SystemExit(1)
