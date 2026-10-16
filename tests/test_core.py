"""Behavioural tests for editing, data, conversion and filesystem safeguards."""
import ast
import gzip
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gunterdown import config, recovery, template
from gunterdown.autocomplete import Engine
from gunterdown.detect_lang import detect
from gunterdown.editor import Buffer
from gunterdown.export import basic_html, export, import_document
from gunterdown.markdown_parser import Parser, validate
from gunterdown.menus import bindings
from gunterdown.treeview import TreeView
from gunterdown.tui import cell_width, fit, main


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"GUNTERDOWN_HOME": str(self.root / "config")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()


class EditorTest(WorkspaceTest):
    def test_unicode_edit_undo_redo_and_dirty_state(self):
        b = Buffer("# Bonjour\n日本語")
        b.row, b.col = 1, 3
        b.insert(" 中文\n한국어")
        edited = b.text
        self.assertTrue(b.modified)
        b.undo()
        self.assertEqual(b.text, "# Bonjour\n日本語")
        self.assertFalse(b.modified)
        b.redo()
        self.assertEqual(b.text, edited)
        b.backspace()
        b.delete()
        self.assertTrue(b.text.endswith("한국"))
        b.move(dc=-100)
        self.assertEqual((b.row, b.col), (0, 0))
        b.delete()
        self.assertTrue(b.text.startswith(" Bonjour"))

    def test_selection_cut_indent_and_paste(self):
        b = Buffer("one\ntwo\nthree")
        b.anchor, b.row, b.col = (0, 0), 2, 0
        b.indent(4)
        self.assertEqual(b.text, "    one\n    two\nthree")
        b.indent(4, True)
        self.assertEqual(b.text, "one\ntwo\nthree")
        b.undo()
        b.undo()
        b.row, b.col = 1, 0
        self.assertEqual(b.cut(), "two\n")
        self.assertEqual(b.text, "one\nthree")
        b.undo()
        b.anchor = (0, 0)
        b.row, b.col = 0, 3
        b.insert("ONE")
        self.assertEqual(b.lines[0], "ONE")

    def test_navigation_and_autoindent(self):
        b = Buffer("  hello world\nend")
        b.col = 7
        b.newline()
        self.assertEqual(b.text, "  hello\n   world\nend")
        b.move(dr=100)
        self.assertEqual(b.row, 2)
        b.word(-1)
        b.move(dc=-1, select=True)
        self.assertIsNotNone(b.anchor)
        b.move(dc=1)
        self.assertIsNone(b.anchor)
        b.row, b.col = 0, 0
        b.word(1)
        self.assertEqual(b.col, 2)
        for i in range(len(b.text) + 1):
            self.assertEqual(b.offset(b.position(i)), i)

    def test_atomic_save_idempotence_external_change_readonly_and_symlink(self):
        path = self.root / "article.md"
        b = Buffer.open(path)
        b.insert("Bonjour 日本語")
        b.save()
        stamp = path.stat().st_mtime_ns
        b.save()
        self.assertEqual(stamp, path.stat().st_mtime_ns)
        path.write_text("changed externally")
        b.insert("!")
        with self.assertRaises(FileExistsError):
            b.save()
        b.save(force=True)
        self.assertEqual(path.read_text(), b.text)
        link = self.root / "link.md"
        link.symlink_to(path)
        linked = Buffer.open(link)
        linked.insert("# ")
        linked.save()
        self.assertTrue(link.is_symlink())
        self.assertEqual(path.read_text(), linked.text)
        path.chmod(0o444)
        linked.insert("x")
        with self.assertRaises(PermissionError):
            linked.save()
        path.chmod(0o644)
        self.assertFalse(list(self.root.glob(".article.md.*")))

    def test_save_as_and_missing_name(self):
        b = Buffer("new")
        with self.assertRaises(ValueError):
            b.save()
        path = self.root / "new.md"
        b.save(path)
        self.assertFalse(b.modified)
        self.assertEqual(b.path, path)

    def test_find_replace_wrap_and_invalid_regex(self):
        b = Buffer("Hello hello\n# Section\nhello world\n# Next\nhello")
        self.assertEqual(b.find("hello"), (0, 5))
        self.assertEqual(b.find("hello"), (6, 11))
        self.assertEqual(b.find("hello", reverse=True), (6, 11))
        self.assertIsNone(b.find("absent"))
        with self.assertRaises(re.error):
            b.find("[", regex=True)
        b.row, b.col = 2, 0
        self.assertEqual(b.substitute("hello", "HI", section=True), 1)
        self.assertIn("HI world", b.text)
        self.assertTrue(b.text.endswith("hello"))
        b.undo()
        self.assertEqual(b.substitute("hello", r"\1", all_matches=False), 1)
        self.assertTrue(b.text.startswith(r"\1"))
        self.assertEqual(b.substitute("hello", "X", case=True), 3)

    def test_history_bound_and_redo_invalidation(self):
        b = Buffer()
        for _ in range(1010):
            b.insert("a")
        self.assertEqual(len(b.undo_stack), 1000)
        b.undo()
        b.insert("b")
        self.assertEqual(b.redo_stack, [])


class MarkdownTest(unittest.TestCase):
    def test_state_changes_propagate_and_cache_reuses_tokens(self):
        p = Parser()
        lines = ["# Article", "```python", "# code", "```", "## Section"]
        tokens = p.parse(lines)
        self.assertEqual(tokens[2][0].kind, "code_block")
        self.assertIs(p.parse(lines)[0], tokens[0])
        lines[1] = "ordinary text"
        updated = p.parse(lines)
        self.assertEqual(updated[2][0].kind, "h1")
        self.assertEqual(updated[4][0].kind, "code_block")
        self.assertTrue(validate("```\nhello"))

    def test_blocks_inline_yaml_setext_and_anchors(self):
        text = "---\ntitle: x\n---\nTitle\n===\n\n## Café\n## Café\n> **bold** *em* `x` [link](url) ![image](x)\n- list\n| table |\n<!--\n## hidden\n-->"
        headings = template.headings(text)
        self.assertEqual([h[3] for h in headings], ["title", "cafe", "cafe-1"])
        tokens = Parser().parse(text.split("\n"))
        kinds = {t.kind for row in tokens for t in row}
        self.assertTrue({"yaml_fm", "bold", "italic", "code", "image", "link", "table", "list", "quote", "comment"} <= kinds)
        self.assertEqual(validate(text), [])
        self.assertIn("ancre absente", validate("[x](#missing)")[0])
        self.assertEqual(validate("```\n[x](#missing)\n```"), [])

    def test_template_yaml_and_toc_idempotence(self):
        text = template.render('Un "titre"\npiégé', 'L’auteur', tags='écriture, Python', summary='une\nligne')
        self.assertIn('title: "Un \\"titre\\"\\npiégé"', text)
        self.assertIn('tags: ["écriture", "Python"]', text)
        self.assertNotIn("{{", text)
        self.assertEqual(template.slugify("L'été à Paris !"), "lete-a-paris")
        minimal = template.render("Titre", minimal=True)
        self.assertNotIn("## Introduction", minimal)
        updated = template.update_toc(template.render("Titre"))
        self.assertEqual(template.update_toc(updated), updated)
        self.assertEqual(validate(updated), [])
        self.assertEqual(template.renumber("# Title\n## One\n## Two\n```\n# hidden\n```"),
                         "# 1. Title\n## 1.1. One\n## 1.2. Two\n```\n# hidden\n```")
        fm = template.frontmatter("# Body", "New", "A", "fr")
        self.assertTrue(fm.endswith("# Body"))
        self.assertEqual(template.frontmatter(fm, "New", "A", "fr"), fm)

    def test_safe_basic_html(self):
        text = "---\ntitle: hidden\n---\n# Café\n## Café\n<script>alert(1)</script>\n[bad](javascript:alert)\n[ok](https://example.test)\n- one\n- two\n1. first\n> quote\n```\n<b>code</b>\n```"
        result = basic_html(text)
        self.assertIn('id="cafe-1"', result)
        self.assertNotIn("<script>", result)
        self.assertNotIn('href="javascript:', result)
        self.assertIn('&lt;b&gt;code&lt;/b&gt;', result)
        self.assertIn('<a href="https://example.test">ok</a>', result)
        self.assertIn("<ul>", result)
        self.assertIn("<ol>", result)
        self.assertNotIn("title: hidden", result)


class LanguageTest(WorkspaceTest):
    def setUp(self):
        super().setUp()
        fixtures = {
            "fr": [("bonjour", 100), ("bonsoir", 80)],
            "en": [("hello", 100), ("help", 80)],
            "ja": [("こんにちは", 100)], "zh": [("你好", 100)],
            "ko": [("안녕하세요", 100)],
        }
        for lang, rows in fixtures.items():
            raw = [{"word": word, "freq": freq, "pos": []} for word, freq in rows]
            (self.root / (lang + ".json.gz")).write_bytes(gzip.compress(json.dumps(raw).encode()))
        patcher = patch.dict(os.environ, {"GUNTERDOWN_DICT_PATH": str(self.root)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_detection_overrides_and_ambiguity(self):
        self.assertEqual(detect("日本語で書きます"), "ja")
        self.assertEqual(detect("한국어 문서"), "ko")
        self.assertEqual(detect("中文文章"), "zh")
        self.assertEqual(detect("漢字", fallback="ja"), "ja")
        self.assertEqual(detect("Ceci est rédigé en français", "en"), "fr")
        self.assertEqual(detect("the and of to a an in for with on by is", "fr"), "en")
        self.assertEqual(detect("hello", "fr"), "fr")
        self.assertEqual(detect("", "en"), "en")
        self.assertEqual(detect("日本語", forced="en"), "en")
        self.assertEqual(detect("的" * 50), "zh")
        self.assertEqual(detect("円" * 50), "ja")

    def test_suggestions_frequency_and_disabled_languages(self):
        engine = Engine(disabled=["ja", "ko"])
        self.assertNotIn("ja", engine.entries)
        self.assertEqual(engine.suggest("bon", "fr")[0].word, "bonjour")
        self.assertEqual(engine.suggest("bonjour", "fr"), [])
        self.assertEqual(engine.suggest("", "fr"), [])
        self.assertEqual(engine.suggest("unknown", "fr"), [])
        self.assertEqual(engine.suggest("bon", "xx"), [])
        lang, prefix, suggestions = engine.complete("BON", 3, "Bonjour", "fr")
        self.assertEqual((lang, prefix, suggestions[0].word), ("fr", "BON", "bonjour"))
        self.assertEqual(engine.complete("bo", 2, "", "fr")[2], [])
        self.assertTrue(Engine().suggest("안녕", "ko"))
        self.assertTrue(Engine().suggest("こん", "ja"))

    def test_corrupt_missing_and_malformed_dictionaries(self):
        missing = self.root / "missing"
        missing.mkdir()
        engine = Engine(missing)
        self.assertEqual(len(engine.warnings), 5)
        path = missing / "fr.json.gz"
        path.write_bytes(b"invalid gzip")
        with self.assertRaisesRegex(ValueError, "corrompu"):
            Engine(missing)
        for data in [{}, [{"word": "x", "freq": "bad"}], [{"word": "x", "freq": 1, "pos": [3]}]]:
            path.write_bytes(gzip.compress(json.dumps(data).encode()))
            with self.assertRaises(ValueError):
                Engine(missing)


class FilesystemTest(WorkspaceTest):
    def test_tree_lazy_filter_sort_operations_and_symlink_cycle(self):
        (self.root / "folder").mkdir()
        (self.root / "folder" / "écriture.md").write_text("hello")
        (self.root / "a.md").write_text("A")
        (self.root / ".hidden.md").write_text("secret")
        (self.root / "ignored.png").write_text("x")
        (self.root / "folder" / "loop").symlink_to(self.root, target_is_directory=True)
        tree = TreeView(self.root)
        self.assertEqual([n.path.name for n, _ in tree.visible_nodes], ["folder", "a.md"])
        tree.toggle_expand()
        self.assertEqual(tree.visible_nodes[1][0].path.name, "écriture.md")
        tree.filter("écriture")
        self.assertEqual(len(tree.visible_nodes), 2)
        with self.assertRaises(re.error):
            tree.filter("[")
        tree.filter("")
        tree.cursor_index = 2
        path = tree.create("new.md")
        tree.cursor_index = next(i for i, (n, _) in enumerate(tree.visible_nodes) if n.path == path)
        tree.rename("renamed.md")
        self.assertTrue((self.root / "renamed.md").exists())
        tree.cursor_index = next(i for i, (n, _) in enumerate(tree.visible_nodes) if n.path.name == "renamed.md")
        with self.assertRaises(FileExistsError):
            tree.rename("a.md")
        tree.delete()
        self.assertFalse((self.root / "renamed.md").exists())
        with self.assertRaises(ValueError):
            tree.create("../escape.md")
        for sort in ("reverse", "mtime", "size"):
            tree.sort = sort
            tree.refresh()
        tree.hidden = True
        tree.refresh()
        self.assertIn(".hidden.md", [n.path.name for n, _ in tree.visible_nodes])
        tree.move(999)
        tree.move(-999)
        self.assertEqual(tree.cursor_index, 0)

    def test_configuration_and_keymap_validation(self):
        settings = config.load()
        settings["editor"]["default_lang"] = "en"
        config.save(settings)
        self.assertEqual(config.load()["editor"]["default_lang"], "en")
        keymap = self.root / "keymap.json"
        self.assertEqual(bindings(keymap)["Ctrl+S"], "save")
        keymap.write_text('{"save": "Ctrl+X"}')
        with self.assertRaisesRegex(ValueError, "Conflit"):
            bindings(keymap)
        keymap.write_text('{"save": "Ctrl+I"}')
        with self.assertRaises(ValueError):
            bindings(keymap)
        keymap.write_text('{"save": "Alt+1"}')
        self.assertEqual(bindings(keymap)["Alt+1"], "save")
        path = config.config_home() / "config.json"
        path.write_text('{"editor":{"auto_save_interval":-1}}')
        with self.assertRaises(ValueError):
            config.load()
        path.write_text('{"ui":false}')
        with self.assertRaises(ValueError):
            config.load()
        path.write_text('[]')
        with self.assertRaises(ValueError):
            config.load()

    def test_recovery_round_trip_and_cleanup(self):
        b = Buffer("disk", self.root / "article.md")
        b.insert("edited ")
        recovery.snapshot(b)
        self.assertEqual(recovery.restore(b.path), b.text)
        recovery.clear(b.path)
        self.assertIsNone(recovery.restore(b.path))
        recovery.snapshot(b)
        path = recovery.recovery_path(b.path)
        os.utime(path, (0, 0))
        recovery.purge()
        self.assertFalse(path.exists())
        try:
            raise RuntimeError("test crash")
        except RuntimeError:
            recovery.log_crash()
        self.assertIn("test crash", (config.config_home() / "crash.log").read_text())

    def test_export_fallback_and_import(self):
        path = self.root / "article.html"
        with patch("gunterdown.export.shutil.which", return_value=None):
            export("# Title", path)
            self.assertIn("<h1", path.read_text())
            with self.assertRaises(RuntimeError):
                export("# Title", self.root / "article.pdf", "pdf")
            org = self.root / "article.org"
            org.write_text("* Title")
            with self.assertRaises(RuntimeError):
                import_document(org)
        text = self.root / "article.txt"
        text.write_text("hello")
        self.assertEqual(import_document(text), "hello")
        with self.assertRaises(ValueError):
            export("", path, "invalid")
        with self.assertRaises(ValueError):
            import_document(self.root / "bad.exe")

    def test_terminal_width_and_python39_syntax(self):
        self.assertEqual(cell_width("日"), 2)
        self.assertEqual(cell_width("\u0301"), 0)
        self.assertEqual(fit("a日本", 4), "a日")
        self.assertEqual(fit("a\x1b", 3), "a�")
        for path in Path("src/gunterdown").glob("*.py"):
            ast.parse(path.read_text(), feature_version=(3, 9))


if __name__ == "__main__":
    unittest.main()
