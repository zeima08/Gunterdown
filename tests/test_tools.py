"""Optional tool invocation, CLI failure paths, and conversion publication."""
import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gunterdown import config
from gunterdown.editor import Buffer
from gunterdown.export import export, import_document
from gunterdown.tui import main


class OptionalToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"GUNTERDOWN_HOME": str(self.root / "config")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_pandoc_exports_publish_only_on_success(self):
        target = self.root / "article.epub"
        target.write_bytes(b"original")
        def convert(command, **kwargs):
            self.assertNotIn("shell", kwargs)
            self.assertEqual(kwargs["input"], "# Article")
            Path(command[command.index("--output") + 1]).write_bytes(b"converted")
            return subprocess.CompletedProcess(command, 0, "", "")
        with patch("gunterdown.export.shutil.which", return_value="/test/pandoc"):
            with patch("gunterdown.export.subprocess.run", side_effect=convert):
                export("# Article", target, "epub")
                self.assertEqual(target.read_bytes(), b"converted")
                export("# Article", self.root / "article.pdf", "pdf")
            with patch("gunterdown.export.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "conversion failed")):
                with self.assertRaisesRegex(RuntimeError, "conversion failed"):
                    export("# Broken", target, "epub")
                self.assertEqual(target.read_bytes(), b"converted")
            with patch("gunterdown.export.subprocess.run", side_effect=subprocess.TimeoutExpired("pandoc", 60)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    export("# Broken", target, "epub")
                self.assertEqual(target.read_bytes(), b"converted")
        with patch("gunterdown.export.shutil.which", side_effect=lambda name: "/test/pandoc" if name == "pandoc" else None):
            with self.assertRaisesRegex(RuntimeError, "xelatex"):
                export("# Article", self.root / "article.pdf", "pdf")

    def test_pandoc_import(self):
        source = self.root / "article.org"
        source.write_text("* Article")
        with patch("gunterdown.export.shutil.which", return_value="/test/pandoc"):
            with patch("gunterdown.export.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "# Article", "")) as call:
                self.assertEqual(import_document(source), "# Article")
                self.assertIn(str(source.absolute()), call.call_args.args[0])
                self.assertTrue(call.call_args.kwargs["check"])

    def test_cli_version_diagnostics_and_errors(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--version"]), 0)
            self.assertEqual(main(["--diagnostics", "-w", str(self.root)]), 0)
        self.assertRegex(output.getvalue(), r"fr \(\d+\)")
        self.assertTrue((config.config_home() / "diagnostics.log").exists())
        path = self.root / "existing.md"
        path.write_text("keep")
        for argv in (["--new", str(path)], ["--no-lang", "invalid"],
                     ["--template", str(self.root / "missing")],
                     ["-w", str(self.root / "missing")], []):
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(argv), 1)
        self.assertEqual(path.read_text(), "keep")
        with patch.dict(os.environ, {"GUNTERDOWN_LANG": "invalid"}), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--version"]), 1)

    def test_crlf_round_trip(self):
        path = self.root / "windows.md"
        path.write_bytes(b"# Title\r\nline\r\n")
        buffer = Buffer.open(path)
        self.assertEqual(buffer.text, "# Title\nline\n")
        buffer.row, buffer.col = 1, 4
        buffer.newline()
        buffer.insert("new")
        buffer.save()
        self.assertEqual(path.read_bytes(), b"# Title\r\nline\r\nnew\r\n")


if __name__ == "__main__":
    unittest.main()
