"""Theme portability, custom palette validation and preview transactions."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from gunterdown import config, themes
from gunterdown.autocomplete import Engine
from gunterdown.editor import Buffer
from gunterdown.tui import Application, argument_parser
from test_terminal import Terminal


class PaletteTest(unittest.TestCase):
    def test_all_palettes_support_8_16_and_256_colors(self):
        for name in themes.BUILTINS:
            theme = themes.load(name, Path('/unused'))
            for count in (8, 16, 256):
                for key in themes.COLOR_KEYS:
                    self.assertTrue(0 <= themes.terminal_color(theme[key], count) < count)
                self.assertNotEqual(themes.terminal_color(theme['fg'], count),
                                    themes.terminal_color(theme['bg'], count))
        self.assertEqual(themes.terminal_color(255, 0), 0)

    def test_custom_themes_merge_and_reject_invalid_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'custom.json'
            path.write_text('{"fg":255,"bg":17,"accent":81}')
            self.assertEqual(themes.load('custom', root)['bg'], 17)
            self.assertIn('custom', themes.available(root))
            for content in ('[]', '{"bg":256}', '{"bg":true}', '{"unknown":1}'):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    themes.load('custom', root)
                self.assertNotIn('custom', themes.available(root))
            for name in ('../escape', '', '..', 'missing'):
                with self.assertRaises(ValueError):
                    themes.load(name, root)

    def test_preview_cancel_restores_and_accept_persists(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'GUNTERDOWN_HOME':directory}):
            args = argument_parser().parse_args(['-w', directory])
            app = Application(args, copy.deepcopy(config.DEFAULTS), Engine(disabled=['fr','en','ja','zh','ko']), Buffer('unchanged'), {})
            app.screen = Mock()
            app.screen.getmaxyx.return_value = (24, 100)
            app.draw = Mock()
            app.put = Mock()
            app.present = Mock()
            app.initialize_colors = Mock()
            app.read_modal_key = Mock(side_effect=['Down', 'Escape'])
            app.select_theme()
            self.assertEqual(app.settings['ui']['theme'], 'dark')
            self.assertFalse((Path(directory)/'config.json').exists())
            app.read_modal_key = Mock(side_effect=['Down', 'Down', 'Down', 'Enter'])
            app.select_theme()
            self.assertEqual(config.load()['ui']['theme'], 'nord')
            app.read_modal_key = Mock(side_effect=['Down', 'Escape'])
            app.select_theme()
            self.assertEqual(app.settings['ui']['theme'], 'nord')
            self.assertEqual(config.load()['ui']['theme'], 'nord')
            self.assertEqual(app.buffer.text, 'unchanged')


class ThemeTerminalTest(unittest.TestCase):
    def test_preview_in_terminal_and_persistent_theme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / 'article.md'
            terminal = Terminal(root, document, ('--theme','light'))
            try:
                terminal.send('\x1by')
                terminal.wait_for('Clair papier')
                terminal.drain(.15)
                before = len(terminal.output)
                terminal.drain(.25)
                self.assertEqual(terminal.output[before:], b'')
                terminal.send('\x1bOB\x1bOB\n')
                saved = json.loads((root/'config/config.json').read_text())
                self.assertEqual(saved['ui']['theme'], 'nord')
                terminal.send('\x1by\x1bOB')
                terminal.send('\x1b')
                self.assertEqual(json.loads((root/'config/config.json').read_text())['ui']['theme'], 'nord')
                terminal.send('# Theme test\x13\x18')
                terminal.exit_ok()
                self.assertEqual(document.read_text(), '# Theme test')
                self.assertEqual(json.loads((root/'config/config.json').read_text())['ui']['theme'], 'nord')
            finally:
                terminal.close()


if __name__ == '__main__':
    unittest.main()
