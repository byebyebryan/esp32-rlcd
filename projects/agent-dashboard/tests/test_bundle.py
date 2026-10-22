import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "dashboard_bundle", APP / "scripts/dashboard-bundle.py"
)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
EXPECTED_DEPENDENCIES = {
    "observer": "0.7.0a8",
    "mesh": "0.1.0a24",
    "profile": "agent-observer.mesh-working-set.v1",
    "nativeVersion": 1,
    "sdk": 1,
    "api": 4,
    "service": 4,
    "preparation": 1,
    "admission": 1,
    "selection": 1,
    "read": 2,
    "workingSetRead": 1,
    "memberLease": 1,
    "scopeLease": 1,
    "windowMs": 259200000,
}
EXPECTED_ARTIFACTS = {
    "observerWheelSha256": "d960872074f8586d2bb56ea97678096a25525ff34796dbf390c94627fd949928",
    "meshWheelSha256": "9bca5b554babfa59ba56b1a4ac5e8e5c66a85e63709731ee1fe7d4f0ed6a18a6",
}

OBSERVED = {
    "dependencies": EXPECTED_DEPENDENCIES,
    "artifacts": EXPECTED_ARTIFACTS,
}


class Bundle(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        for name in bundle.INPUTS:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if name == bundle.LOCK_INPUT:
                path.write_bytes((APP / bundle.LOCK_INPUT).read_bytes())
            else:
                path.write_text("bounded fixture\n")
        with patch.object(bundle, "probe", return_value=OBSERVED):
            self.target, self.checksum = bundle.freeze(
                self.source, self.root / "installed", sys.executable, "fixture"
            )
        self.addCleanup(self.writable)

    def writable(self):
        for path in self.root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)

    def test_exact_freeze_is_reusable_and_rejects_changed_files(self):
        self.assertEqual(
            bundle.lock_values(APP / bundle.LOCK_INPUT),
            (EXPECTED_DEPENDENCIES, EXPECTED_ARTIFACTS),
        )
        manifest = bundle.verify(self.target, self.checksum, dependencies=False)
        self.assertEqual(manifest["sourceRevision"], "fixture")
        self.assertEqual(manifest["deviceWire"], 5)
        self.assertEqual(manifest["artifacts"], OBSERVED["artifacts"])
        self.assertEqual(manifest["dependencies"], EXPECTED_DEPENDENCIES)
        self.assertEqual(
            manifest["files"][bundle.LOCK_INPUT],
            bundle.digest((APP / bundle.LOCK_INPUT).read_bytes()),
        )
        with patch.object(bundle, "probe", return_value=OBSERVED):
            again = bundle.freeze(
                self.source, self.root / "installed", sys.executable, "fixture"
            )
        self.assertEqual(again, (self.target, self.checksum))
        changed = self.target / bundle.INPUTS[0]
        changed.chmod(0o644)
        changed.write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "bundle_file_mismatch"):
            bundle.verify(self.target, self.checksum, dependencies=False)

    def test_same_version_different_wheels_do_not_verify(self):
        replaced = {
            "dependencies": EXPECTED_DEPENDENCIES,
            "artifacts": {
                "observerWheelSha256": "c" * 64,
                "meshWheelSha256": "d" * 64,
            },
        }
        with patch.object(bundle, "probe", return_value=replaced):
            with self.assertRaisesRegex(ValueError, "dependency_artifact_mismatch"):
                bundle.verify(self.target, self.checksum)

    def test_manifest_pin_extra_file_and_symlink_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "bundle_manifest_mismatch"):
            bundle.verify(self.target, "0" * 64, dependencies=False)
        self.target.chmod(0o755)
        extra = self.target / "unexpected"
        extra.write_text("extra")
        with self.assertRaisesRegex(ValueError, "bundle_files_mismatch"):
            bundle.verify(self.target, self.checksum, dependencies=False)
        extra.unlink()
        extra.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "bundle_symlink"):
            bundle.verify(self.target, self.checksum, dependencies=False)
        extra.unlink()

    def test_old_sdk_release_lock_is_rejected(self):
        lock = self.target / bundle.LOCK_INPUT
        lock.chmod(0o644)
        locked = json.loads(lock.read_text())
        locked["releases"][0]["version"] = "0.7.0a7"
        lock.write_text(json.dumps(locked))
        with self.assertRaisesRegex(ValueError, "sdk_lock_release"):
            bundle.verify(self.target, self.checksum, dependencies=False)

    def test_old_release_tuple_is_rejected(self):
        old = self.target / "manifest.json"
        old.chmod(0o644)
        manifest = bundle.verify(self.target, self.checksum, dependencies=False)
        manifest["dependencies"]["observer"] = "0.7.0a7"
        old.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "bundle_manifest_invalid"):
            bundle.verify(self.target, dependencies=False)

    def test_wire4_bundle_is_rejected(self):
        path = self.target / "manifest.json"
        path.chmod(0o644)
        manifest = json.loads(path.read_text())
        manifest["deviceWire"] = 4
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "bundle_manifest_invalid"):
            bundle.verify(self.target, dependencies=False)


if __name__ == "__main__":
    unittest.main()
