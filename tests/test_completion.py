"""Downloaded data, typo suggestions, and safe completion acceptance."""
import json
import tempfile
import unittest
from pathlib import Path

from gunterdown import config
from gunterdown.autocomplete import Engine
from gunterdown.editor import Buffer
from gunterdown.tui import Application, argument_parser


class CompletionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine(config.DATA / "dicts")

    def test_real_corpora_and_attribution(self):
        sources = json.loads((config.DATA / "dicts/SOURCES.json").read_text())
        self.assertEqual(set(self.engine.entries), {"fr", "en", "ja", "zh", "ko"})
        for lang, entries in self.engine.entries.items():
            self.assertGreater(len(entries), 30000)
            self.assertEqual(len(entries), sources["languages"][lang]["entries"])
            self.assertIn("CC BY-SA", (config.DATA / "dicts" / (lang + ".LICENSE.txt")).read_text())
        self.assertTrue(self.engine.suggest("bonj", "fr"))
        self.assertTrue(self.engine.suggest("aujourd’h", "fr"))
        self.assertTrue(self.engine.suggest("hel", "en"))
        self.assertTrue(self.engine.suggest("こん", "ja"))
        self.assertTrue(self.engine.suggest("你", "zh"))
        self.assertTrue(self.engine.suggest("안녕", "ko"))

    def test_typos_accents_known_words_and_disabled_languages(self):
        for typo in ("bonjor", "bonjjour", "bnojour", "bonjoru"):
            result = self.engine.corrections(typo, "fr")
            self.assertIn("bonjour", [e.word for e in result])
            self.assertTrue(all(e.kind == "correction" for e in result))
        self.assertIn("hello", [e.word for e in self.engine.corrections("helllo", "en")])
        self.assertEqual(self.engine.corrections("bonjour", "fr"), [])
        self.assertIn("développement", [e.word for e in self.engine.corrections("developpement", "fr")])
        self.assertEqual(self.engine.corrections("x" * 100, "fr"), [])
        self.assertEqual(self.engine.corrections("日本語", "ja"), [])
        self.assertEqual(self.engine.corrections("hello", "missing"), [])
        _, _, result = self.engine.complete("helllo", 6, "", "en", "en")
        self.assertIn("hello", [e.word for e in result])
        self.assertLessEqual(len(result), 5)

    def test_case_and_midword_acceptance_are_one_undo(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argument_parser().parse_args(["-w", directory, "-l", "fr"])
            buffer = Buffer("BONJxxx")
            buffer.col = 4
            app = Application(args, config.load(), self.engine, buffer, {})
            app.refresh_completion()
            app.suggestion_index = next(i for i, e in enumerate(app.suggestions) if e.word == "bonjour")
            app.accept_suggestion()
            self.assertEqual(buffer.text, "BONJOUR")
            self.assertEqual(app.suggestions, [])
            buffer.undo()
            self.assertEqual(buffer.text, "BONJxxx")
            buffer.anchor = (0, 0)
            app.refresh_completion()
            self.assertEqual(app.suggestions, [])

    def test_popup_stays_within_the_editor_at_screen_edges(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argument_parser().parse_args(["-w", directory])
            app = Application(args, config.load(), self.engine, Buffer("bonj"), {})
            app.suggestions = self.engine.suggest("bonj", "fr")
            class Screen:
                def getmaxyx(self):
                    return 12, 60
            app.screen = Screen()
            calls = []
            app.put = lambda y, x, text, attr=0, width=None: calls.append((y, x, text))
            for cy in (2, 9):
                calls.clear()
                app.draw_suggestions(cy, 57, 2, 10, 20)
                self.assertTrue(calls)
                for y, x, text in calls:
                    self.assertGreaterEqual(x, 20)
                    self.assertLessEqual(x + len(text), 59)
                    self.assertTrue(2 <= y <= 10)
                    self.assertNotEqual(y, cy)


if __name__ == "__main__":
    unittest.main()
