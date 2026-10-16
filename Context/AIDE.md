# AIDE — Manuel intégré de Gunterdown

> Section Aide accessible depuis le TUI via `F1` ou le menu `Aide >
> Manuel`. Contient le manuel utilisateur, la FAQ, le dépannage, le
> glossaire et la liste complète des raccourcis clavier. Public visé :
> utilisateurs de tous niveaux.

---

## 1. Manuel rapide (démarrage en 5 minutes)

### 1.1 Démarrer

Une fois `Gunterdown` installé (voir `INSTALL.md`), lancez-le depuis un
terminal :

```bash
gunterdown mon_article.md
```

Si le fichier n'existe pas, il sera créé à la première sauvegarde. Si
vous ne précisez pas de fichier, `Gunterdown` ouvre un buffer vide nommé
`sans_titre.md`.

### 1.2 Écrire du texte

Tapez normalement. Le curseur se déplace avec les flèches du clavier.
La touche `Entrée` insère une nouvelle ligne. Le texte s'affiche avec
une coloration Markdown minimale (titres, listes, emphases).

### 1.3 Insérer le template d'article

Sur un nouveau fichier, appuyez sur `Alt+T` pour insérer le template
d'article complet. Un dialogue vous demandera le titre, les tags et
le résumé. Les autres variables (`{{AUTHOR}}`, `{{DATE}}`, `{{LANG}}`)
sont automatiquement remplies.

### 1.4 Sauvegarder et quitter

- `Ctrl+S` — Sauvegarder
- `Ctrl+X` — Quitter (avec confirmation si des modifications sont non
  sauvegardées)

### 1.5 Demander de l'aide

- `F1` — Manuel intégré (vous y êtes)
- `F12` — À propos
- `Ctrl+H` — Liste des raccourcis

---

## 2. FAQ — Questions fréquentes

### 2.1 Démarrage

**Q : `gunterdown` n'est pas reconnu dans mon terminal.**
**R :** Vérifiez que `/usr/local/bin` ou `~/.local/bin` figure dans
votre `$PATH`. Si vous avez installé via `pip install --user`,
ajoutez `export PATH="$HOME/.local/bin:$PATH"` à votre `~/.bashrc` ou
`~/.zshrc`.

**Q : Les caractères japonais/chinois/coréens s'affichent en `???`.**
**R :** Votre locale n'est probablement pas en UTF-8. Exécutez
`locale | grep -E "LANG|LC_CTYPE"` et, si la sortie ne contient pas
`UTF-8`, lancez `sudo dpkg-reconfigure locales` (Debian/Ubuntu) ou
`sudo locale-gen ja_JP.UTF-8 zh_CN.UTF-8 ko_KR.UTF-8` puis
`update-locale`. Voir `INSTALL.md` § 1.3.

**Q : Le terminal affiche des caractères bizarres à la place des
bordures curses.**
**R :** Le terminal n'interprète pas correctement les caractères
semi-graphiques. Définissez `TERM=xterm-256color` ou
`TERM=screen-256color` : `export TERM=xterm-256color`.

**Q : `Gunterdown` se lance mais l'écran est entièrement noir/blanc.**
**R :** Le terminal ne supporte pas les couleurs ou `TERM` est limité.
Définissez `TERM=xterm-256color` et vérifiez que votre terminal
supporte 256 couleurs (la plupart des terminaux modernes le font).
Vous pouvez aussi forcer le mode sans couleur avec `gunterdown --no-color`.

### 2.2 Édition

**Q : Comment insérer un caractère de tabulation réel ?**
**R :** Par défaut, `Tab` est utilisé pour l'autocomplétion. Pour
insérer une tabulation, utilisez `Ctrl+I` ou `Shift+Tab` si votre
terminal supporte cette séquence. Vous pouvez aussi désactiver
l'autocomplétion avec `Alt+D`, auquel cas `Tab` insère une tabulation
(vrai tabulateur ou espaces selon `tab_size` dans `config.json`).

**Q : Comment passer en mode colonnes (split) ?**
**R :** Le split horizontal/vertical est prévu pour la version 0.8.0
(voir `README.md` § 3). En attendant, vous pouvez ouvrir plusieurs
instances de `Gunterdown` dans un multiplexeur comme `tmux` ou `screen`.

**Q : Comment annuler une modification accidentelle ?**
**R :** `Ctrl+U` annule (undo), `Ctrl+Y` rétablit (redo). L'historique
est illimité pour la session courante (limité à 1000 entrées en
mémoire pour limiter la consommation).

**Q : Puis-je ouvrir plusieurs fichiers en même temps ?**
**R :** Pas encore dans la version courante. La version 0.8.0
introduira les onglets. En attendant, utilisez le panneau arborescence
pour basculer rapidement entre fichiers : `Tab` pour passer dans
l'arbo, `Entrée` pour ouvrir, `Tab` pour revenir à l'éditeur.

### 2.3 Autocomplétion

**Q : L'autocomplétion ne propose rien quand je tape en japonais.**
**R :** Vérifiez que le dictionnaire japonais est chargé :
`gunterdown --diagnostics` doit lister `ja` parmi les langues disponibles.
Si `ja` n'est pas listé, vérifiez que le fichier
`/opt/gunterdown/data/dicts/ja.json.gz` (ou
`~/.local/share/gunterdown/data/dicts/ja.json.gz` en cas d'installation
pip) existe. Vous pouvez aussi le désactiver explicitement avec
`--no-lang ja` puis le réactiver en enlevant l'option.

**Q : Comment forcer l'autocomplétion dans une langue précise ?**
**R :** Appuyez sur `Alt+L` puis choisissez la langue dans le menu
(`fr`, `en`, `ja`, `zh`, `ko` ou `auto`). Le choix est persistant
pour la session. Vous pouvez aussi préfixer votre commande de
lancement : `gunterdown -l ja article.md`.

**Q : L'autocomplétion est lente sur mon vieux netbook.**
**R :** Désactivez les langues que vous n'utilisez pas : `gunterdown
--no-lang ja,zh,ko article.md`. Vous pouvez aussi augmenter le seuil
de déclenchement dans `config.json` :
`editor.autocompletion_threshold = 5`. Enfin, désactivez totalement
l'autocomplétion avec `Alt+D`.

**Q : Comment désactiver définitivement l'autocomplétion ?**
**R :** Dans `config.json` : `editor.autocompletion = false`. Vous
pouvez aussi utiliser l'option `--no-lang fr,en,ja,zh,ko` qui
désactive tous les dictionnaires.

### 2.4 Arborescence

**Q : L'arborescence ne montre pas mon dossier habituel.**
**R :** Utilisez `-w` ou `--workdir` au lancement : `gunterdown -w
~/Projets/articles`. Sans cette option, `Gunterdown` utilise le dossier
courant. Vous pouvez aussi changer de dossier racine depuis le menu
`Outils > Changer le dossier de travail`.

**Q : Comment masquer les fichiers cachés (`.git`, `.config`, etc.) ?**
**R :** Par défaut ils sont masqués. Appuyez sur `.` dans le panneau
arbo pour les afficher/masquer. La préférence est sauvegardée dans
`config.json` → `ui.show_hidden_files`.

**Q : Mon dossier contient 10 000 fichiers et l'arborescence rame.**
**R :** `Gunterdown` filtre par défaut les fichiers non-`.md`/`.markdown`/
`.txt`. Si le dossier reste très gros, utilisez le filtre `f` pour
restreindre l'affichage par regex, ou déplacez-vous dans un
sous-dossier plus spécifique.

---

## 3. Raccourcis clavier — synthèse complète

### 3.1 Édition

| Raccourci     | Action                                |
|---------------|----------------------------------------|
| `↑ ↓ ← →`     | Déplacer le curseur                    |
| `Ctrl+↑ ↓`    | Saute au mot précédent/suivant         |
| `Home / End`  | Début/fin de ligne                     |
| `Ctrl+Home`   | Début du fichier                       |
| `Ctrl+End`    | Fin du fichier                         |
| `PageUp/Down` | Page précédente/suivante               |
| `Backspace`   | Supprimer caractère avant curseur     |
| `Delete`      | Supprimer caractère après curseur     |
| `Ctrl+K`      | Couper la ligne courante              |
| `Ctrl+U`      | Annuler (undo)                         |
| `Ctrl+Y`      | Rétablir (redo)                        |
| `Ctrl+A`      | Sélectionner tout                      |
| `Ctrl+C`      | Copier la sélection                    |
| `Ctrl+V`      | Coller                                 |
| `Tab`         | Autocompléter / indenter sélection    |
| `Shift+Tab`   | Suggestion suivante / désindenter      |

### 3.2 Fichier

| Raccourci       | Action                                |
|-----------------|----------------------------------------|
| `Ctrl+N`        | Nouveau buffer                         |
| `Ctrl+O`        | Ouvrir fichier                         |
| `Ctrl+S`        | Sauvegarder                            |
| `Ctrl+Shift+S`  | Enregistrer sous                       |
| `Ctrl+W`        | Fermer buffer                          |
| `Ctrl+X`        | Quitter                                |
| `Ctrl+E`        | Exporter                               |

### 3.3 Article (template Markdown)

| Raccourci     | Action                                |
|---------------|----------------------------------------|
| `Alt+T`       | Insérer le template complet           |
| `Alt+F`       | Insérer/éditer front-matter YAML     |
| `Alt+S`       | Générer la TOC                        |
| `Alt+N`       | Renuméroter les titres                |
| `Alt+2`       | Insérer `## `                         |
| `Alt+3`       | Insérer `### `                        |
| `Alt+C`       | Insérer bloc de code                 |
| `Alt+Q`       | Insérer citation                       |
| `Alt+M`       | Insérer tableau 3×3                   |
| `Alt+P`       | Insérer légende image                  |
| `Alt+V`       | Vérifier la syntaxe Markdown          |

### 3.4 Recherche

| Raccourci     | Action                                |
|---------------|----------------------------------------|
| `Ctrl+W`      | Recherche incrémentale (⚠ conflit)    |
| `Ctrl+D`      | Occurrence suivante                    |
| `Ctrl+B`      | Occurrence précédente                  |
| `Ctrl+\`      | Remplacer                              |
| `Ctrl+G`      | Aller à une ligne                       |
| `F3`          | Aller à la définition de titre         |

### 3.5 Outils et Aide

| Raccourci     | Action                                |
|---------------|----------------------------------------|
| `F1`          | Manuel (AIDE.md)                       |
| `F2`          | Ouvrir la barre de menus                |
| `F5`          | Insérer la date                        |
| `F6`          | Aperçu live (pandoc)                   |
| `F7`          | Compter les mots                       |
| `F8`          | Vérifier l'orthographe (aspell)         |
| `F9`          | Masquer/afficher l'arborescence         |
| `F12`         | À propos                                |
| `Alt+L`       | Forcer la langue d'autocomplétion      |
| `Alt+D`       | Bascule l'autocomplétion                |
| `Alt+Z`       | Mode focus (cache tout sauf l'éditeur) |
| `Alt+W`       | Bascule le soft-wrap                    |
| `Ctrl+H`      | Liste des raccourcis                    |
| `Ctrl+?`      | Diagnostics système                    |

### 3.6 Arborescence (focus sur panneau arbo)

| Raccourci | Action                              |
|-----------|--------------------------------------|
| `Tab`     | Basculer vers l'éditeur             |
| `↑ ↓`     | Déplacer la sélection               |
| `→`       | Ouvrir le dossier                   |
| `←`       | Remonter au parent                  |
| `Entrée`  | Ouvrir le fichier                   |
| `n`       | Nouveau fichier                     |
| `d`       | Supprimer                           |
| `r`       | Renommer                            |
| `m`       | Nouveau dossier                     |
| `f`       | Filtrer                             |
| `s`       | Trier                               |
| `.`       | Afficher/masquer les cachés         |

---

## 4. Dépannage — Troubleshooting

### 4.1 Crash au démarrage

Si `Gunterdown` crash au démarrage, lancez-le avec l'option
`--diagnostics` pour obtenir un état du système :

```bash
gunterdown --diagnostics
```

Cela affiche : version Python, locale, taille du terminal, dictionnaires
trouvés, configuration chargée, droits sur le dossier de travail. Le
rapport est également copié dans `~/.gunterdown/diagnostics.log`.

### 4.2 Crash pendant l'édition

En cas de crash, `Gunterdown` tente de sauvegarder le buffer courant dans
`~/.gunterdown/recover/` sous un nom de la forme
`<fichier>.<timestamp>.recover`. Au prochain lancement, si un fichier
de récupération est trouvé pour le fichier ouvert, un dialogue
propose de le restaurer. Les fichiers de récupération sont conservés
30 jours puis purgés.

La pile d'appels est enregistrée dans `~/.gunterdown/crash.log`. Pour
signaler un crash, joignez ce fichier à votre ticket (en supprimant
toute information personnelle du buffer).

### 4.3 Lenteur

| Symptôme                        | Solution                                    |
|---------------------------------|---------------------------------------------|
| Démarrage > 3 secondes          | Désactiver des langues : `--no-lang ja,zh,ko` |
| Saisie lente                    | Désactiver l'autocomplétion : `Alt+D`        |
| Scrolling saccadé                | Augmenter le seuil d'autocompl. à 5+        |
| Coloration désynchronisée        | Forcer un re-parse : `Alt+R` (re-render)    |
| Fichier de 10 000+ lignes lent   | Désactiver le panneau arbo : `F9`           |

### 4.4 Caractères CJK invisibles

1. Vérifiez votre police : le terminal doit avoir accès à une police
   Noto Sans CJK ou équivalente (`sudo apt install fonts-noto-cjk`
   sous Debian/Ubuntu).
2. Vérifiez votre locale : `locale | grep LANG` doit contenir `UTF-8`.
3. Vérifiez votre `TERM` : `echo $TERM` doit être `xterm-256color` ou
   équivalent.
4. Si le problème persiste, lancez `gunterdown --diagnostics` et regardez
   le test de rendu CJK : si les caractères ne s'affichent pas dans
   le test, le problème vient du terminal, pas de `Gunterdown`.

### 4.5 Pandoc absent

L'aperçu live (`F6`) et l'export HTML/EPUB/PDF nécessitent `pandoc`.
Si `pandoc` n'est pas installé, ces fonctionnalités sont
silencieusement désactivées et le menu `Fichier > Exporter` n'affiche
que l'export HTML basique (convertisseur interne limité).

Pour installer `pandoc` :

```bash
# Debian/Ubuntu
sudo apt install pandoc

# macOS
brew install pandoc

# Arch Linux
sudo pacman -S pandoc
```

Pour l'export PDF, installez en plus `texlive-xetex` (ou
`texlive-full`) car `Gunterdown` utilise `xelatex` qui supporte les
caractères CJK nativement.

---

## 5. Glossaire

| Terme             | Définition                                                 |
|-------------------|------------------------------------------------------------|
| TUI               | Text User Interface — interface en mode texte              |
| Buffer            | Zone mémoire contenant le texte en cours d'édition         |
| Front-matter      | Bloc YAML en tête de fichier Markdown délimité par `---`   |
| TOC               | Table of Contents — sommaire                                |
| Slug              | Version ASCII normalisée d'un titre, utilisée dans les URLs |
| Soft-wrap         | Retour à la ligne affiché mais non inséré dans le fichier   |
| Hard-wrap         | Retour à la ligne inséré dans le fichier                    |
| CJK               | Chinese / Japanese / Korean — familles de caractères      |
| IME               | Input Method Editor — méthode de saisie pour CJK           |
| Hanzi / Kanji     | Caractères d'origine chinoise utilisés en ZH / JA          |
| Kana              | Syllabaires japonais (hiragana et katakana)                |
| Hangul            | Alphabet coréen                                             |
| GFM               | GitHub Flavored Markdown — extensions Markdown de GitHub  |
| YAML              | YAML Ain't Markup Language — format sériel lisible        |
| Curses            | Bibliothèque d'interface texte pour terminaux Unix         |

---

## 6. Où trouver plus d'aide

- **README.md** — vue d'ensemble du projet.
- **INSTALL.md** — procédure d'installation détaillée.
- **USAGE.md** — guide utilisateur complet.
- **ARCHITECTURE.md** — documentation technique (contributeurs).
- **A_PROPOS.md** — auteur et crédits.
- **CONTRIBUER.md** — guide du contributeur, packaging, licences.
- **Tickets GitHub** : `https://github.com/zeima/gunterdown/issues`
- **Discussions GitHub** : `https://github.com/zeima/gunterdown/discussions`

---

## English summary

This file is the in-TUI manual accessed via `F1`. It covers a 5-minute
quick start, a detailed FAQ covering startup issues, editing,
autocomplete, and the file-tree panel, a full keyboard shortcut
reference (editing, file, article template, search, tools, tree
panel), a troubleshooting section (crash recovery via
`~/.gunterdown/recover/`, diagnostics, slow editor, missing CJK glyphs,
missing pandoc), and a glossary of TUI/Markdown/CJK terminology.
Recovery files are kept for 30 days; crash logs go to
`~/.gunterdown/crash.log`. For further help, users are directed to the
other Markdown files in the project and to the GitHub issue tracker.
