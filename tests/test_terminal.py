"""Real curses workflows exercised through a standard-library pseudo-terminal."""
import fcntl
import json
import os
import pty
import select
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Terminal:
    def __init__(self, directory, path=None, extra=(), executable=None):
        self.master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 100, 0, 0))
        self.output = b""
        config = directory / "config"
        config.mkdir(exist_ok=True)
        (config / "config.json").write_text(json.dumps({"template": {"auto_insert": "never"}}))
        env = dict(os.environ, TERM="xterm-256color", LANG="en_US.UTF-8" if sys.platform == "darwin" else "C.UTF-8", GUNTERDOWN_HOME=str(config))
        command = [str(executable or ROOT / "gunterdown"), "-w", str(directory), *extra]
        if path:
            command.append(str(path))
        self.process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave,
                                        env=env, start_new_session=True)
        os.close(slave)
        self.wait_for("Gunterdown")

    def drain(self, duration=.15):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            if select.select([self.master], [], [], max(0, deadline - time.monotonic()))[0]:
                try:
                    chunk = os.read(self.master, 65536)
                    if not chunk:
                        break
                    self.output += chunk
                except OSError:
                    break

    def wait_for(self, text, timeout=4):
        deadline = time.monotonic() + timeout
        while text.encode() not in self.output and time.monotonic() < deadline:
            self.drain(.05)
        if text.encode() not in self.output:
            raise AssertionError(f"Missing {text!r}; output: {self.output[-2000:]!r}")

    def send(self, text):
        os.write(self.master, text.encode())
        self.drain()

    def close(self):
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=3)
        os.close(self.master)

    def exit_ok(self):
        self.drain(.2)
        code = self.process.wait(timeout=4)
        if code:
            raise AssertionError(self.output[-4000:].decode(errors="replace"))


class CursesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.term = None

    def tearDown(self):
        if self.term:
            self.term.close()
        self.tmp.cleanup()

    def test_unicode_save_undo_redo_and_quit(self):
        path = self.root / "article.md"
        self.term = Terminal(self.root, path)
        self.term.send("# Bonjour\n日本語 中文 한국어")
        self.term.send("\x15")  # undo final character
        self.term.send("\x19")  # redo
        self.term.send("\x13")  # save
        self.term.wait_for("enregistré")
        self.term.send("\x18")
        self.term.exit_ok()
        self.assertEqual(path.read_text(), "# Bonjour\n日本語 中文 한국어")
        self.assertFalse((self.root / "config/crash.log").exists())

    def test_dirty_quit_cancel_save_as_and_menu(self):
        self.term = Terminal(self.root)
        self.term.send("draft")
        self.term.send("\x18")
        self.term.wait_for("Modifications")
        self.term.send("\x1b")  # cancel quit
        self.term.send("\x1bOQ")  # F2 xterm
        self.term.wait_for("Enregistrer")
        self.term.send("\x1b")
        self.term.send("\x13")
        self.term.wait_for("Enregistrer sous")
        self.term.send("\x15" + str(self.root / "saved.md") + "\n")
        self.term.send("\x18")
        self.term.exit_ok()
        self.assertEqual((self.root / "saved.md").read_text(), "draft")

    def test_search_replace_and_html_export(self):
        path = self.root / "article.md"
        path.write_text("# Test\nhello world\n")
        self.term = Terminal(self.root, path, ("--no-color",))
        self.term.send("\x17world\n")
        self.term.send("\x1cworld\nmonde\n\n")  # replace + all
        self.term.send("\x13")
        self.term.send("\x05\n")  # export + HTML
        self.term.send("\x15" + str(self.root / "article.html") + "\n")
        self.term.send("\x18")
        self.term.exit_ok()
        self.assertIn("hello monde", path.read_text())
        self.assertIn("hello monde", (self.root / "article.html").read_text())

    def test_completion_and_typo_popup_acceptance_without_idle_repaint(self):
        path = self.root / "article.md"
        self.term = Terminal(self.root, path)
        self.term.send("bonj")
        self.term.wait_for("Compléter")
        self.term.drain(.15)
        previous = len(self.term.output)
        self.term.drain(.25)
        self.assertEqual(self.term.output[previous:], b"")
        self.term.send("\x1bOB\x1bOA")  # select next then previous suggestion
        self.term.send("\t\nbonjoru")
        self.term.wait_for("Corriger")
        self.term.send("\t\x13\x18")
        self.term.exit_ok()
        self.assertEqual(path.read_text(), "bonjour\nbonjour")

    def test_modal_screens_stay_still_until_input(self):
        path = self.root / "article.md"
        path.write_text("# Stable document\nhello world\n")
        self.term = Terminal(self.root, path)

        def assert_idle():
            self.term.drain(.15)
            previous = len(self.term.output)
            self.term.drain(.35)
            self.assertEqual(self.term.output[previous:], b"",
                             "An unchanged modal screen must not repaint")

        self.term.send("\x1bOQ")  # F2, menus
        assert_idle()
        self.term.send("\x1bOC\x1bOB")  # Right to Edit, then Down
        assert_idle()
        fcntl.ioctl(self.term.master, termios.TIOCSWINSZ,
                    struct.pack("HHHH", 16, 70, 0, 0))
        self.term.process.send_signal(signal.SIGWINCH)
        self.term.drain(.15)
        assert_idle()
        self.term.send("\x1b")
        self.term.send("\x17hello")  # incremental search prompt
        assert_idle()
        self.term.send("\x1b")
        self.term.send("\x1bOP")  # F1, help viewer
        assert_idle()
        self.term.send("\x1b")
        self.term.send("x\x18")  # modified document, quit confirmation
        assert_idle()
        self.term.send("\x1b")
        self.term.send("\x15\x18")  # undo edit, quit
        self.term.exit_ok()
        self.assertEqual(path.read_text(), "# Stable document\nhello world\n")

    def test_recovery_replaces_disk_text_and_resize(self):
        path = self.root / "article.md"
        path.write_text("old")
        directory = self.root / "config/recover"
        directory.mkdir(parents=True)
        import hashlib
        name = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:24] + ".recover"
        (directory / name).write_text(json.dumps({"text": "recovered", "timestamp": time.time()}))
        self.term = Terminal(self.root, path)
        self.term.wait_for("Restaurer")
        self.term.send("\x1bOB\n")  # down, Yes
        fcntl.ioctl(self.term.master, termios.TIOCSWINSZ, struct.pack("HHHH", 10, 38, 0, 0))
        self.term.process.send_signal(signal.SIGWINCH)
        self.term.drain()
        self.term.send("\x13\x18")
        self.term.exit_ok()
        self.assertEqual(path.read_text(), "recovered")


if __name__ == "__main__":
    unittest.main()
