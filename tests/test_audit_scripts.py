"""Storage audit behavior with synthetic files; no real user scripts are executed."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_scripts.py"
SPEC = importlib.util.spec_from_file_location("law_audit_scripts", SCRIPT)
audit_scripts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_scripts)


class AuditScriptsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, rel, text="pass\n"):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_empty_scope_and_default_threshold(self):
        self.assertEqual(audit_scripts.audit(self.root)["exit_code"], 0)
        self.write("build.py")
        result = audit_scripts.audit(self.root)
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(result["over"], [(".", 1)])

    def test_legacy_threshold_is_per_directory(self):
        for rel in ("a/one.py", "a/two.py", "a/three.py",
                    "b/one.py", "b/two.py", "b/three.py"):
            self.write(rel)
        self.assertEqual(audit_scripts.audit(self.root, 3)["exit_code"], 0)
        self.write("b/four.py")
        self.assertEqual(audit_scripts.audit(self.root, 3)["over"], [("b", 4)])

    def test_invalid_roots_are_incomplete(self):
        path = self.write("file.py")
        for root in (self.root / "missing", path):
            with self.subTest(root=root):
                result = audit_scripts.audit(root)
                self.assertEqual(result["exit_code"], 2)
                self.assertTrue(result["errors"])

    def test_negative_threshold_rejected_by_cli(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                audit_scripts.main([str(self.root), "--max-loose", "-1"])
        self.assertEqual(exc.exception.code, 2)

    def test_declared_exclusions_and_nested_owned_name(self):
        for rel in ("tools/core.py", "skills/example/a.py", "en/tool.py",
                    "job/scripts/a.py", "job/_nguon_dung/a.py",
                    "working/_scratch/a.py", ".venv/a.py"):
            self.write(rel)
        self.write("job/tools/loose.PY")
        result = audit_scripts.audit(self.root)
        self.assertEqual([p for p, _ in result["files"]],
                         [os.path.join("job", "tools", "loose.PY")])
        self.assertEqual(len(result["skipped"]), 7)
        self.assertEqual(result["exit_code"], 1)

    def test_hash_duplicates_across_directories_not_function_names(self):
        self.write("a/one.py", "def same():\n    return 1\n")
        self.write("b/two.PY", "def same():\n    return 1\n")
        self.write("c/three.py", "def same():\n    return 2\n")
        result = audit_scripts.audit(self.root)
        self.assertEqual(result["duplicates"], [
            [os.path.join("a", "one.py"), os.path.join("b", "two.PY")]
        ])

    def test_never_runs_scripts_and_preserves_files(self):
        self.write("poison.py", "raise RuntimeError('MUST NOT EXECUTE')\n")
        self.write("data.txt", "synthetic source\n")
        before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.root.rglob("*") if p.is_file()}
        result = audit_scripts.audit(self.root)
        after = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(before, after)

    def test_read_error_overrides_threshold_and_never_reports_clean(self):
        self.write("a.py")
        output = io.StringIO()
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            with contextlib.redirect_stdout(output):
                code = audit_scripts.main([str(self.root), "--max-loose", "3"])
        self.assertEqual(code, 2)
        self.assertIn("INCOMPLETE", output.getvalue())
        self.assertNotIn("WITHIN THRESHOLD in", output.getvalue())

    def test_walk_error_is_not_silently_clean(self):
        def broken_walk(root, topdown, onerror, followlinks):
            onerror(PermissionError("cannot enumerate"))
            return iter(())
        with mock.patch.object(audit_scripts.os, "walk", side_effect=broken_walk):
            result = audit_scripts.audit(self.root)
        self.assertEqual(result["exit_code"], 2)

    def test_reparse_root_ancestor_directory_and_file_are_not_read(self):
        self.write("sub/a.py")
        self.write("loose.py")
        original = audit_scripts.os.lstat
        # Model the Windows reparse bit even on hosts without symlink privilege.
        for target in (self.root, self.root.parent, self.root / "sub",
                       self.root / "loose.py"):
            target_name = os.path.normcase(os.path.abspath(str(target)))

            def fake_stat(path):
                actual = original(path)
                if os.path.normcase(os.path.abspath(str(path))) == target_name:
                    return mock.Mock(st_mode=actual.st_mode, st_file_attributes=0x400)
                return actual

            with self.subTest(target=target):
                with mock.patch.object(audit_scripts.os, "lstat", side_effect=fake_stat):
                    result = audit_scripts.audit(self.root)
                self.assertEqual(result["exit_code"], 2)
                self.assertTrue(any("reparse" in err for err in result["errors"]))

    def test_dotdot_does_not_hide_a_link_ancestor(self):
        self.write("linked/child/a.py")
        original = audit_scripts.os.lstat
        target = str(self.root / "linked")

        def fake_stat(path):
            actual = original(path)
            if str(path) == target:
                return mock.Mock(st_mode=stat.S_IFLNK, st_file_attributes=0)
            return actual

        with mock.patch.object(audit_scripts.os, "lstat", side_effect=fake_stat):
            result = audit_scripts.audit(str(self.root / "linked" / ".."))
        self.assertEqual(result["exit_code"], 2)

    def test_real_directory_link_is_not_traversed(self):
        target = self.root / "target"
        target.mkdir()
        (target / "outside.py").write_text("pass\n", encoding="utf-8")
        scan = self.root / "scan"
        scan.mkdir()
        link = scan / "linked"
        if os.name == "nt":
            # mklink is used only to CREATE a test junction, never for deletion.
            made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                  capture_output=True)
            if made.returncode:
                self.skipTest("junction creation unavailable")
        else:
            link.symlink_to(target, target_is_directory=True)
        try:
            result = audit_scripts.audit(scan)
            self.assertEqual(result["exit_code"], 2)
            self.assertEqual(result["files"], [])
            self.assertTrue((target / "outside.py").exists())
        finally:
            if os.name == "nt":
                os.rmdir(link)  # remove junction only; never recurse into the target
            else:
                link.unlink()

    def test_cli_reports_scope_even_when_within_threshold(self):
        self.write("scripts/accepted_location.py")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = audit_scripts.main([str(self.root)])
        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn("Root exclusions:", text)
        self.assertIn("SKIPPED: scripts", text)
        self.assertIn("not a safety/content verdict", text)


if __name__ == "__main__":
    unittest.main()
