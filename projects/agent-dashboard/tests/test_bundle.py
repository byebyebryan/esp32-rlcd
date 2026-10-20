import importlib.util
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

OBSERVED = {
    "dependencies": bundle.EXPECTED,
    "artifacts": {
        "observerWheelSha256": "a" * 64,
        "meshWheelSha256": "b" * 64,
    },
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
        manifest = bundle.verify(self.target, self.checksum, dependencies=False)
        self.assertEqual(manifest["sourceRevision"], "fixture")
        self.assertEqual(manifest["deviceWire"], 4)
        self.assertEqual(manifest["artifacts"], OBSERVED["artifacts"])
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
            "dependencies": bundle.EXPECTED,
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


if __name__ == "__main__":
    unittest.main()
