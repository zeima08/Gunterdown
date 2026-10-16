"""Optional first-run configuration workflows."""
import copy
import os
import tempfile
import unittest
from unittest.mock import patch

from gunterdown import config
from gunterdown.autocomplete import Engine
from gunterdown.editor import Buffer
from gunterdown.tui import Application, argument_parser


class StartupTest(unittest.TestCase):
    def make_app(self):
        args = argument_parser().parse_args([])
        return Application(args, copy.deepcopy(config.DEFAULTS), Engine(disabled=('fr', 'en', 'ja', 'zh', 'ko')), Buffer(), {})

    def test_skip_and_escape_do_not_save_or_prompt_for_template(self):
        for answer in (None, 2):
            app = self.make_app()
            with patch.object(app, 'choose', return_value=answer), patch.object(config, 'save') as save:
                self.assertFalse(app.startup_menu())
                save.assert_not_called()

    def test_quick_setup_saves_defaults(self):
        app = self.make_app()
        with patch.object(app, 'choose', return_value=1), patch.object(config, 'save') as save:
            self.assertTrue(app.startup_menu())
            save.assert_called_once_with(config.DEFAULTS)

    def test_guided_setup_persists_language_and_template(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'GUNTERDOWN_HOME': directory}):
            app = self.make_app()
            with patch.object(app, 'choose', side_effect=[0, 1, 1, 2]):
                self.assertTrue(app.startup_menu())
            settings = config.load()
            self.assertEqual(settings['ui']['language'], 'en')
            self.assertEqual(settings['editor']['default_lang'], 'en')
            self.assertEqual(settings['template']['auto_insert'], 'never')
