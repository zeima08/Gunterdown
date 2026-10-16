# INSTALL — Guide d'installation de Gunterdown

> Procédure d'installation et de configuration de `Gunterdown` sur Linux, macOS,
> WSL et BSD. L'éditeur n'a **aucune dépendance Python externe** ; tout repose
> sur la bibliothèque standard et un terminal compatible `curses`.

---

## 1. Pré-requis système

### 1.1 Matériel et terminal

`Gunterdown` fonctionne dans n'importe quel terminal compatible avec l'API
`curses` (NCurses sous Linux/BSD, son équivalent BSD sous macOS). Aucune
interface graphique n'est nécessaire. La résolution minimale recommandée est
80 colonnes × 24 lignes, mais l'éditeur s'adapte jusqu'à 200 colonnes et
recommande un terminal de 120 × 40 pour profiter pleinement du panneau
arborescence et de la coloration Markdown. Le terminal doit gérer l'UTF-8
sans exception, faute de quoi les caractères CJK (japonais, chinois,
coréen) ne s'afficheront pas correctement.

Terminaux testés et recommandés :

- **Linux** : GNOME Terminal, Konsole, Alacritty, Kitty, Terminator, rxvt-unicode.
- **macOS** : Terminal.app, iTerm2, Alacritty, Kitty.
- **WSL** : Windows Terminal (recommandé), WSLtty, Alacritty sous Windows.
- **BSD** : xterm, urxvt, kitty.

Terminaux non recommandés : Windows CMD sans WSL, PowerShell ISE (pas de
support curses natif), et tout terminal ne gérant pas les séquences ANSI
complètes.

### 1.2 Polices CJK

Pour afficher correctement les idéogrammes japonais, chinois et coréens,
votre terminal doit avoir accès aux polices suivantes (déjà présentes sur la
plupart des distributions modernes) :

| Langue     | Police recommandée   | Paquet Debian/Ubuntu        |
|------------|----------------------|------------------------------|
| Japonais   | Noto Sans CJK JP    | `fonts-noto-cjk`             |
| Chinois    | Noto Sans CJK SC    | `fonts-noto-cjk`             |
| Coréen     | Noto Sans CJK KR    | `fonts-noto-cjk`             |

Sur macOS, ces polices sont installées par défaut depuis OS X 10.11. Sous
WSL, le terminal Windows Terminal utilise les polices Windows : installez
« Noto Sans CJK » depuis le Microsoft Store si l'affichage des caractères
CJK est tronqué.

### 1.3 Locale UTF-8

Vérifiez votre locale avant de lancer `Gunterdown` :

```bash
locale | grep -E "LANG|LC_CTYPE"
```

La sortie doit contenir `UTF-8` (par exemple `fr_FR.UTF-8` ou `en_US.UTF-8`).
Si ce n'est pas le cas, générez la locale puis rechargez-la :

```bash
sudo locale-gen fr_FR.UTF-8 en_US.UTF-8 ja_JP.UTF-8 zh_CN.UTF-8 ko_KR.UTF-8
sudo update-locale LANG=fr_FR.UTF-8
```

Sous macOS, la locale est gérée par le système dans
`Préférences Système > Langue et région` ; aucun réglage spécifique n'est
nécessaire si l'UTF-8 est déjà sélectionné (cas par défaut).

---

## 2. Pré-requis logiciels

### 2.1 Python

`Gunterdown` nécessite **Python 3.9 ou supérieur**. La version 3.9 est le
minimum imposé pour profiter des annotations de type étendues et de
`pathlib.Path.read_bytes()`. Python 3.10+ est recommandé pour
`match`/`case` utilisé dans le parser Markdown.

Vérifiez la version installée :

```bash
python3 --version
```

Si la version est inférieure à 3.9, installez une version plus récente
selon votre système :

```bash
# Debian/Ubuntu
sudo apt install python3 python3-dev

# macOS (Homebrew)
brew install python@3.11

# Arch Linux
sudo pacman -S python
```

### 2.2 Dépendances stdlib utilisées

Toutes les dépendances ci-dessous font partie de la bibliothèque standard
Python et ne nécessitent aucune installation supplémentaire :

| Module stdlib    | Rôle dans Gunterdown                          |
|------------------|------------------------------------------|
| `curses`         | Affichage TUI, gestion clavier, fenêtres  |
| `_curses`        | Liaison bas niveau (auto-chargée)         |
| `os`, `sys`      | Chemins, signaux, exit codes              |
| `pathlib`        | Manipulation sûre des chemins             |
| `re`             | Expressions régulières (parser Markdown)  |
| `json`           | Chargement des dictionnaires d'autocompl. |
| `gzip`           | Décompression des `.json.gz`              |
| `argparse`       | Ligne de commande                         |
| `locale`         | Détection locale UTF-8                    |
| `unicodedata`    | Détection de catégorie Unicode (CJK)     |
| `shutil`         | Copie, déplacement de fichiers            |
| `subprocess`     | Appel optionnel à `pandoc` (preview live) |

### 2.3 Modules Python stdlib non inclus sous Windows

Sur Windows natif (sans WSL), le module `curses` n'est pas inclus dans la
bibliothèque standard. `Gunterdown` ne supporte pas Windows natif ; utilisez WSL
(Windows Subsystem for Linux) ou Cygwin. Sous WSL, l'installation est
identique à celle de Linux Debian/Ubuntu.

---

## 3. Installation

Trois méthodes d'installation sont officiellement supportées. Les paquets
binaires (`.deb`, AUR, Homebrew) sont prévus à partir de la version 0.6.0 ;
en attendant, l'installation par script et par `pip` sont les voies
recommandées.

### 3.1 Installation par script (recommandée pour usage personnel)

Téléchargez le dépôt et lancez le script d'installation fourni. Le script
vérifie la version de Python, place le lanceur shell dans `/usr/local/bin`
et copie le code Python dans `/opt/gunterdown` :

```bash
git clone https://github.com/zeima/gunterdown.git
cd gunterdown
sudo ./install.sh
```

Le script effectue les opérations suivantes :

1. Vérifie la version de Python (≥ 3.9).
2. Crée `/opt/gunterdown/` et y copie `src/` et `data/`.
3. Copie `bin/gunterdown` dans `/usr/local/bin/gunterdown` (droits `0755`).
4. Met à jour le shebang de `gunterdown` pour pointer vers le Python détecté.
5. Vérifie la locale UTF-8 et affiche un avertissement si nécessaire.
6. Affiche un message de confirmation avec la commande d'aide : `gunterdown --help`.

Pour désinstaller :

```bash
sudo /opt/gunterdown/uninstall.sh
```

### 3.2 Installation par pip (recommandée pour contributeurs)

Le paquet est publié sur PyPI à partir de la version 0.4.0. Pour les versions
de développement, installez depuis le dépôt :

```bash
git clone https://github.com/zeima/gunterdown.git
cd gunterdown
pip install --user .
```

Cette méthode installe l'exécutable `gunterdown` dans `~/.local/bin/`. Assurez-vous
que ce chemin figure dans votre `$PATH` :

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3.3 Installation manuelle (clonage du dépôt)

Si vous souhaitez exécuter `Gunterdown` sans l'installer, vous pouvez simplement
cloner le dépôt et appeler directement le script Python :

```bash
git clone https://github.com/zeima/gunterdown.git
cd gunterdown
python3 bin/gunterdown.py --help
```

Pour plus de commodité, ajoutez un alias dans votre `~/.bashrc` :

```bash
alias gunterdown="python3 /chemin/vers/gunterdown/bin/gunterdown.py"
```

### 3.4 Vérification de l'installation

Quel que soit le mode d'installation, vérifiez que `Gunterdown` répond :

```bash
gunterdown --version
gunterdown --help
```

La commande `--version` doit afficher la version installée, le chemin de
l'exécutable et la liste des dictionnaires disponibles. La commande
`--help` affiche les options de ligne de commande (fichier à ouvrir,
dossier de travail, langue forcée, mode sans couleur, etc.).

---

## 4. Dictionnaires d'autocomplétion

Les dictionnaires d'autocomplétion sont livrés dans `data/dicts/` au format
JSON compressé gzip. À l'initialisation, `Gunterdown` les décompresse en mémoire
et construit un index par préfixe pour la recherche rapide. Aucune
téléchargement complémentaire n'est nécessaire.

| Fichier             | Langue    | Source                              | Licence   |
|---------------------|-----------|-------------------------------------|-----------|
| `fr.json.gz`        | Français  | Wiktextract (fr.wiktionary.org)     | CC BY-SA  |
| `en.json.gz`        | Anglais   | Wiktextract (en.wiktionary.org)     | CC BY-SA  |
| `ja.json.gz`        | Japonais  | JMDict (edrdg.org)                  | CC BY-SA  |
| `zh.json.gz`        | Chinois   | CC-CEDICT                           | CC BY-SA  |
| `ko.json.gz`        | Coréen    | KAIST Word Dictionary               | CC BY-SA  |

Taille totale des dictionnaires compressés : environ 14 Mo. Taille en
mémoire après chargement : environ 90 Mo (acceptable sur une machine
moderne). L'utilisateur peut désactiver le chargement d'une langue avec
l'option `--no-lang` :

```bash
gunterdown --no-lang ja,zh,ko article.md
```

Voir `CONTRIBUER.md` § 6 pour les détails de licence et la procédure de mise
à jour des dictionnaires.

---

## 5. Configuration post-installation

### 5.1 Fichier de configuration utilisateur

`Gunterdown` lit son fichier de configuration depuis `~/.config/gunterdown/config.json`
(créé automatiquement au premier lancement). Format :

```json
{
  "ui": {
    "theme": "dark",
    "tree_width": 30,
    "show_line_numbers": true,
    "tab_size": 4
  },
  "editor": {
    "auto_indent": true,
    "soft_wrap": true,
    "default_lang": "fr",
    "autocompletion": true,
    "autocompletion_threshold": 3
  },
  "template": {
    "auto_insert": "ask",
    "path": "~/.config/gunterdown/templates/article.md"
  }
}
```

Aucune de ces valeurs n'est obligatoire. Les valeurs par défaut sont
suffisantes pour démarrer ; les utilisateurs avancés peuvent les ajuster.

### 5.2 Variables d'environnement

| Variable           | Rôle                                         | Défaut        |
|--------------------|-----------------------------------------------|---------------|
| `GUNTERDOWN_HOME`       | Chemin du dossier de configuration            | `~/.config/gunterdown` |
| `GUNTERDOWN_DICT_PATH`  | Chemin alternatif pour les dictionnaires      | `/opt/gunterdown/data/dicts` |
| `GUNTERDOWN_NO_COLOR`   | Désactive la couleur (`1` pour désactiver)    | non défini    |
| `GUNTERDOWN_LANG`        | Force la langue d'autocomplétion par défaut   | `fr`          |
| `EDITOR`           | Éditeur externe de secours (menu Outils)      | `vi`          |

### 5.3 Test rapide

Pour vérifier que l'autocomplétion multilingue fonctionne, lancez :

```bash
gunterdown --new test.md
```

Tapez quelques mots en français, appuyez sur `Tab` pour déclencher
l'autocomplétion, puis tapez quelques mots en anglais et observez le
changement automatique de dictionnaire. Répétez l'expérience avec des
caractères japonais, chinois et coréens : le dictionnaire actif doit
changer en conséquence. Voir `USAGE.md` § 5 pour le détail des raccourcis.

---

## 6. Dépannage d'installation

| Symptôme                                | Cause probable                       | Solution                                              |
|-----------------------------------------|--------------------------------------|-------------------------------------------------------|
| `ModuleNotFoundError: No module 'curses'` | Windows natif                       | Installer WSL puis refaire l'installation             |
| Caractères CJK = `???`                  | Locale non UTF-8                     | `sudo locale-gen` + `update-locale` (voir § 1.3)      |
| Caractères CJK non affichés             | Police CJK absente                   | `sudo apt install fonts-noto-cjk`                     |
| `gunterdown: command not found`              | `~/.local/bin` pas dans `$PATH`      | Ajouter `export PATH="$HOME/.local/bin:$PATH"` au rc  |
| Crash `curses.error: setupterm`         | Variable `TERM` mal définie          | `export TERM=xterm-256color`                          |
| Aucune couleur                          | Variable `TERM` limitée              | `export TERM=xterm-256color` ou `screen-256color`     |
| Lenteur au démarrage                    | Dictionnaires trop volumineux        | `gunterdown --no-lang ja,zh,ko` ou réduire `dicts/`        |

Pour tout autre problème, voir `AIDE.md` § 5 (Troubleshooting) et ouvrir un
ticket sur le dépôt GitHub du projet en joignant la sortie de
`gunterdown --version` et `gunterdown --diagnostics`.

---

## English summary

`Gunterdown` requires only Python 3.9+ and a UTF-8 terminal with `curses`
support (NCurses on Linux/BSD, native on macOS). There are zero external
Python dependencies. Installation is supported via a shell script
(recommended for end users), via `pip` (recommended for contributors) or
manually by cloning the repository. CJK fonts (`fonts-noto-cjk`) and a
UTF-8 locale are required for Japanese/Chinese/Korean autocompletion.
The compressed dictionaries (≈14 MB total, ≈90 MB in RAM) ship in the
package and load automatically at startup; individual languages can be
disabled with `--no-lang`. The user config lives at
`~/.config/gunterdown/config.json` and several environment variables
(`GUNTERDOWN_HOME`, `GUNTERDOWN_LANG`, `GUNTERDOWN_NO_COLOR`, etc.) allow further
customization. See `USAGE.md` for daily usage and `AIDE.md` for
troubleshooting.
