Gunterdown — Terminal Markdown editor

Interface language: Tools > Interface language (Alt+U).
Completion language: Alt+L, or --lang en/ja/zh/ko/fr.
These two choices are independent. The interface language is saved.
Start directly with --ui-lang en, ja, zh, ko or fr.

A popup appears while typing: 3 Latin letters, 2 Japanese/Korean characters,
or 1 Chinese character. Use ↑/↓ or Shift+Tab to choose, Tab to accept,
and Esc to dismiss. Enter inserts a newline. Ctrl+Space forces suggestions.
The dictionary language is shown on suggestions from another language.
Japanese/Chinese completion also works within sentences without spaces.
Use your system IME to enter kana, Han characters or Hangul;
romaji, pinyin and Latin-to-Hangul conversion are not provided.

Ctrl+S saves; Ctrl+X quits; F2 opens menus; F9 toggles the file tree.
Shift+Left/Right selects text. Ctrl+U undoes, Ctrl+Y redoes.
Alt+B switches documents. Tab switches tree/editor when no suggestion exists.
An asterisk marks an unsaved document. Unsaved changes require confirmation.
Recovery snapshots are saved every 30 seconds under GUNTERDOWN_HOME/recover/.
All suggestions are processed offline. FR/EN typo suggestions are lexical,
not grammar correction; CJK completion matches native character prefixes.

Shortcuts (Esc returns to the editor):

File
  Ctrl+N       New
  Ctrl+O       Open…
  Ctrl+R       Recent files
  Ctrl+S       Save
  Alt+E        Save as…
  —            Save all
  Alt+X        Close
  —            Import
  Ctrl+E       Export
  Ctrl+P       Print
  Ctrl+X       Quit
Edit
  Ctrl+U       Undo
  Ctrl+Y       Redo
  Ctrl+K       Cut
  Ctrl+C       Copy
  Ctrl+V       Paste
  Ctrl+A       Select all
  —            Indent
  —            Unindent
  Alt+/        Toggle comment
  F5           Insert date
  Ctrl+L       Insert link
  Alt+I        Insert image
Search
  Ctrl+W       Find
  Ctrl+D       Next
  Ctrl+B       Previous
  Ctrl+\       Replace
  Ctrl+G       Go to line
  F3           Go to heading
  —            Find in files
Article
  Alt+T        Template
  Alt+F        Front matter
  Alt+S        Table of contents
  Alt+N        Renumber headings
  Alt+2        H2 heading
  Alt+3        H3 heading
  Alt+C        Code
  Alt+Q        Quote
  Alt+M        Table
  Alt+P        Image caption
  Alt+V        Check Markdown
Tools
  F6           HTML preview
  F7           Statistics
  F8           Spelling
  Alt+L        Completion language
  Alt+U        Interface language
  Alt+D        Completion
  Alt+Z        Focus mode
  Alt+W        Soft wrap
  Alt+#        Line numbers
  F9           File tree
  —            Change directory
  —            Preferences
Help
  F1           Manual
  Alt+H        Shortcuts
  F12          About
  —            Diagnostics

Themes: Alt+Y or Tools > Themes. ↑/↓ previews; Enter saves; Esc cancels.
Palettes: dark, light, solarized, nord, dracula, ocean, contrast.
Use --theme nord at startup. Custom palettes: GUNTERDOWN_HOME/themes/*.json.
