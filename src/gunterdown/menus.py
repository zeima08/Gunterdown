"""Declarative menus and terminal-representable shortcut bindings."""
from __future__ import annotations

import json
from pathlib import Path

# Terminal aliases (Ctrl+I/Tab, Ctrl+H/Backspace) cannot be independent shortcuts.
MENUS = [
    ("Fichier", "File", [
        ("Nouveau", "New", "Ctrl+N", "new"),
        ("Ouvrir…", "Open…", "Ctrl+O", "open"),
        ("Récents", "Recent", "Ctrl+R", "recent"),
        ("Enregistrer", "Save", "Ctrl+S", "save"),
        ("Enregistrer sous…", "Save as…", "Alt+E", "save_as"),
        ("Enregistrer tout", "Save all", "", "save_all"),
        ("Fermer", "Close", "Alt+X", "close"),
        ("Importer", "Import", "", "import"),
        ("Exporter", "Export", "Ctrl+E", "export"),
        ("Imprimer", "Print", "Ctrl+P", "print"),
        ("Quitter", "Quit", "Ctrl+X", "quit")]),
    ("Édition", "Edit", [
        ("Annuler", "Undo", "Ctrl+U", "undo"),
        ("Rétablir", "Redo", "Ctrl+Y", "redo"),
        ("Couper", "Cut", "Ctrl+K", "cut"),
        ("Copier", "Copy", "Ctrl+C", "copy"),
        ("Coller", "Paste", "Ctrl+V", "paste"),
        ("Tout sélectionner", "Select all", "Ctrl+A", "select_all"),
        ("Indenter", "Indent", "", "indent"),
        ("Désindenter", "Unindent", "", "unindent"),
        ("Commenter", "Comment", "Alt+/", "comment"),
        ("Insérer date", "Insert date", "F5", "date"),
        ("Insérer lien", "Insert link", "Ctrl+L", "link"),
        ("Insérer image", "Insert image", "Alt+I", "image")]),
    ("Recherche", "Search", [
        ("Rechercher", "Find", "Ctrl+W", "find"),
        ("Suivant", "Next", "Ctrl+D", "next"),
        ("Précédent", "Previous", "Ctrl+B", "previous"),
        ("Remplacer", "Replace", "Ctrl+\\", "replace"),
        ("Atteindre ligne", "Go to line", "Ctrl+G", "goto"),
        ("Aller au titre", "Go to heading", "F3", "heading"),
        ("Multi-fichiers", "Find in files", "", "find_files")]),
    ("Article", "Article", [
        ("Template", "Template", "Alt+T", "template"),
        ("Front-matter", "Front matter", "Alt+F", "frontmatter"),
        ("Sommaire", "Table of contents", "Alt+S", "toc"),
        ("Renuméroter", "Renumber", "Alt+N", "renumber"),
        ("Section H2", "H2 heading", "Alt+2", "h2"),
        ("Section H3", "H3 heading", "Alt+3", "h3"),
        ("Code", "Code", "Alt+C", "code"),
        ("Citation", "Quote", "Alt+Q", "quote"),
        ("Tableau", "Table", "Alt+M", "table"),
        ("Légende image", "Image caption", "Alt+P", "caption"),
        ("Vérifier Markdown", "Check Markdown", "Alt+V", "validate")]),
    ("Outils", "Tools", [
        ("Aperçu HTML", "HTML preview", "F6", "preview"),
        ("Statistiques", "Statistics", "F7", "stats"),
        ("Orthographe", "Spelling", "F8", "spell"),
        ("Langue", "Language", "Alt+L", "language"),
        ("Langue de l’interface", "Interface language", "Alt+U", "ui_language"),
        ("Autocomplétion", "Completion", "Alt+D", "completion"),
        ("Mode focus", "Focus mode", "Alt+Z", "focus"),
        ("Retour visuel", "Soft wrap", "Alt+W", "wrap"),
        ("Numéros de ligne", "Line numbers", "Alt+#", "numbers"),
        ("Arborescence", "File tree", "F9", "tree"),
        ("Changer dossier", "Change directory", "", "workdir"),
        ("Thèmes", "Themes", "Alt+Y", "themes"),
        ("Préférences", "Preferences", "", "preferences")]),
    ("Aide", "Help", [
        ("Manuel", "Manual", "F1", "help"),
        ("Raccourcis", "Shortcuts", "Alt+H", "shortcuts"),
        ("À propos", "About", "F12", "about"),
        ("Diagnostics", "Diagnostics", "", "diagnostics")]),
]


def bindings(path: Path) -> dict[str, str]:
    """Merge keymap overrides and reject duplicate or unavailable shortcuts."""
    actions = {action: key for _, _, items in MENUS for _, _, key, action in items}
    if path.exists():
        custom = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(custom, dict):
            raise ValueError("keymap.json : objet attendu")
        for action, key in custom.items():
            if action not in actions or not isinstance(key, str):
                raise ValueError(f"Action ou raccourci invalide : {action}")
            actions[action] = key
    result = {}
    for action, key in actions.items():
        if not key:
            continue
        import re
        if not re.fullmatch(r"Ctrl\+[A-Z\\]|Alt\+[A-Za-z0-9/#]|F(?:[1-9]|1[0-2])", key):
            raise ValueError(f"Raccourci non supporté : {key}")
        if key in ("Ctrl+I", "Ctrl+H", "Ctrl+M", "Ctrl+J"):
            raise ValueError(f"Raccourci réservé au terminal : {key}")
        if key in result:
            raise ValueError(f"Conflit de raccourci : {key}")
        result[key] = action
    return result
