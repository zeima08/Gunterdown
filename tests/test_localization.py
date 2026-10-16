"""Native interfaces, CJK thresholds and multilingual terminal workflows."""
import ast
import copy
import json
import os
import string
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gunterdown import config
from gunterdown.autocomplete import Engine
from gunterdown.editor import Buffer
from gunterdown.i18n import CATALOG, UI_LANGUAGES, translate
from gunterdown.menus import MENUS
from gunterdown.tui import Application, argument_parser, pad_cells, text_width
from test_terminal import Terminal


class LocalizationTest(unittest.TestCase):
    def test_complete_menu_catalogs_and_format_fields(self):
        for fr, _, items in MENUS:
            self.assertIn(fr, CATALOG)
            for name, _, _, _ in items:
                self.assertIn(name, CATALOG)
        formatter = string.Formatter()
        for key, values in CATALOG.items():
            self.assertEqual(len(values), 4, key)
            fields = {name for _, name, _, _ in formatter.parse(key) if name is not None}
            for value in values:
                self.assertTrue(value.strip(), key)
                self.assertEqual(fields, {name for _, name, _, _ in formatter.parse(value) if name is not None}, key)
        self.assertEqual(translate("Fichier", "ja"), "ファイル")
        self.assertEqual(translate("Fichier", "zh"), "文件")
        self.assertEqual(translate("Fichier", "ko"), "파일")
        self.assertEqual(translate("saved", "en"), "File saved")

    def test_dialog_labels_and_native_manuals_have_translations(self):
        tree = ast.parse(Path("src/gunterdown/tui.py").read_text())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("prompt", "choose", "view", "confirm")
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                self.assertIn(node.args[0].value, CATALOG)
        for lang in UI_LANGUAGES[1:]:
            manual = (config.DATA / "docs" / f"MANUEL.{lang}.md").read_text()
            self.assertIn("--ui-lang", manual)
            self.assertIn("Alt+L", manual)
            self.assertIn(translate("Fichier", lang), manual)

    def test_settings_cli_and_terminal_cell_widths(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"GUNTERDOWN_HOME": directory}):
            for lang in UI_LANGUAGES:
                settings = copy.deepcopy(config.DEFAULTS)
                settings["ui"]["language"] = lang
                config.save(settings)
                self.assertEqual(config.load()["ui"]["language"], lang)
                args = argument_parser().parse_args(["--ui-lang", lang, "--lang", "en"])
                self.assertEqual((args.ui_lang, args.lang), (lang, "en"))
            for value in ("ファイル", "文件", "파일", "Save as"):
                self.assertEqual(text_width(pad_cells(value, 23)), 23)
                self.assertLessEqual(text_width(pad_cells(value, 3)), 3)


class MultilingualCompletionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine(config.DATA / "dicts")

    def test_short_native_prefixes_and_sentences_without_spaces(self):
        cases = [("en", "hel", "hel", "hello"),
                 ("ja", "こん", "こん", "こんにちは"),
                 ("ja", "今日はこん", "こん", "こんにちは"),
                 ("zh", "你", "你", "你好"),
                 ("zh", "我想说你好世", "你好世", "你好世界"),
                 ("ko", "안녕", "안녕", "안녕하세요")]
        for lang, text, prefix, expected in cases:
            with self.subTest(language=lang, text=text):
                detected, fragment, entries = self.engine.complete(text, len(text), text, "fr", lang)
                self.assertEqual((detected, fragment), (lang, prefix))
                self.assertIn(expected, [entry.word for entry in entries])
                self.assertTrue(all(e.language == lang for e in entries))
        self.assertEqual(self.engine.complete("안", 1, "안", "fr", "ko")[2], [])
        self.assertEqual(self.engine.complete("こ", 1, "こ", "fr", "ja")[2], [])
        self.assertTrue(self.engine.complete("こ", 1, "こ", "fr", "ja", 1)[2])

    def test_automatic_english_and_script_switching(self):
        entries = self.engine.complete("hel", 3, "hel", "fr")[2]
        self.assertIn(("hello", "en"), [(e.word, e.language) for e in entries])
        for lang, word in [("ja", "こん"), ("ko", "안녕"), ("zh", "你好世")]:
            detected, _, entries = self.engine.complete(word, len(word), "Un texte français " + word, "fr")
            self.assertEqual(detected, lang)
            self.assertTrue(entries)

    def test_ui_language_does_not_force_document_language(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"GUNTERDOWN_HOME": directory}):
            args = argument_parser().parse_args(["-w", directory, "--lang", "en", "--ui-lang", "ja"])
            buffer = Buffer("hel")
            buffer.col = 3
            app = Application(args, copy.deepcopy(config.DEFAULTS), self.engine, buffer, {})
            app.refresh_completion()
            self.assertEqual((app.ui_lang, app.lang), ("ja", "en"))
            app.set_ui_language("ko")
            self.assertEqual(config.load()["ui"]["language"], "ko")
            self.assertEqual(app.forced, "en")
            self.assertTrue(app.suggestions)
            app.suggestion_index = next(i for i, entry in enumerate(app.suggestions) if entry.word == "hello")
            app.accept_suggestion()
            self.assertEqual(buffer.text, "hello")


class MultilingualTerminalTest(unittest.TestCase):
    def test_native_interfaces_and_completion_acceptance(self):
        cases = [("en", "hel", "hello", 1),
                 ("ja", "今日はこん", "今日はこんにちは", 0),
                 ("zh", "我想说你好世", "我想说你好世界", 0),
                 ("ko", "안녕", "안녕하세요", 0)]
        for lang, text, expected, selection in cases:
            with self.subTest(language=lang), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "article.md"
                terminal = Terminal(root, path, ("--ui-lang", lang, "--lang", lang))
                try:
                    terminal.wait_for(translate("Fichier", lang))
                    terminal.send(text)
                    terminal.wait_for(expected if lang in ("en", "ko") else expected[-(5 if lang == "ja" else 4):])
                    terminal.send("\x1bOB" * selection + "\t\x13")
                    terminal.wait_for(translate("saved", lang).split()[-1])
                    terminal.send("\x18")
                    terminal.exit_ok()
                    self.assertEqual(path.read_text(), expected)
                    saved = json.loads((root / "config/config.json").read_text())
                    self.assertEqual(saved["ui"]["language"], lang)
                finally:
                    terminal.close()

    def test_switch_ui_language_immediately_and_open_native_help(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            terminal = Terminal(root, root / "article.md", ("--lang", "en"))
            try:
                terminal.send("\x1bu")  # interface language, Alt+U
                terminal.wait_for("日本語")
                terminal.send("\x1bOB\x1bOB\n")
                terminal.wait_for("ファイル")
                self.assertEqual(json.loads((root / "config/config.json").read_text())["ui"]["language"], "ja")
                terminal.send("\x1bOP")
                terminal.wait_for("Gunterdown マニュアル")
                terminal.send("\x1b")
                terminal.send("hel\x1bOB\t\x13\x18")
                terminal.exit_ok()
                self.assertEqual((root / "article.md").read_text(), "hello")
            finally:
                terminal.close()


if __name__ == "__main__":
    unittest.main()
