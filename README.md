# Gunterdown

Éditeur Markdown en terminal, écrit en Python standard avec `curses`.
Conçu par Zeima pour rédiger des articles en français, anglais et CJK.

## Démarrer

Python 3.9+ et un terminal UTF-8 sous Linux, macOS, BSD ou WSL :

```sh
./gunterdown mon_article.md
# ou
python3 bin/gunterdown.py mon_article.md
```

Aucun paquet Python n'est nécessaire pour exécuter l'application ou ses tests.
`Ctrl+S` enregistre, `Ctrl+X` quitte, `F1` ouvre le manuel, `F2` les menus.
Au premier document vierge, choisissez si vous souhaitez insérer un template.
Les fichiers ne sont écrits qu'à l'enregistrement.

```sh
./gunterdown --new article.md
./gunterdown --lang ja article.md
./gunterdown --no-lang ja,zh,ko --no-color article.md
./gunterdown --diagnostics
```

## Fonctionnalités livrées

- Édition Unicode, undo/redo, sélection continue avec Shift+flèches,
  copier/coller interne, indentation et retour à la ligne visuel.
- Menus clavier, arborescence, filtres regex, tri et opérations fichier.
- Buffers multiples accessibles avec `Alt+B`, protection des modifications,
  fichiers récents, sauvegarde atomique et récupération après incident.
- Coloration Markdown, templates d'article avec front-matter, sommaire,
  insertion de structures et vérification de liens internes/blocs ouverts.
- Autocomplétion FR/EN/JA/ZH/KO, détection par paragraphe, recherche binaire
  des préfixes et classement par fréquence.
- Recherche incrémentale, remplacement avec regex/casse et recherche dans
  les fichiers Markdown du dossier de travail.
- Export HTML autonome interne. Pandoc ajoute HTML/EPUB et l'import org/rst ;
  PDF nécessite aussi XeLaTeX. Aspell permet de lister les mots inconnus.

Les dictionnaires embarqués contiennent **225 615 entrées** : FR 49 418,
EN 48 635, JA 33 151, ZH 45 567, KO 48 844. Ils proviennent de
[FrequencyWords, Hermit Dave](https://github.com/hermitdave/FrequencyWords),
corpus OpenSubtitles 2018, avec un complément de vocabulaire original.
Les données adaptées sont sous **CC BY-SA 4.0**, le code reste sous MIT.
La provenance, la révision figée, les licences et les checksums sont livrés
avec les dictionnaires dans `src/gunterdown/data/dicts/`.

Un **popup près du curseur** propose au plus cinq mots, classés par fréquence :
à partir de 3 lettres latines, de 2 caractères japonais/coréens ou d'un caractère
chinois. En mode automatique, les préfixes latins courts peuvent proposer
FR et EN avec le code de langue affiché. Le japonais et le chinois fonctionnent
également à l'intérieur d'une phrase sans espaces. `↑` / `↓` ou `Shift+Tab` change la sélection,
`Tab` valide et `Échap` ferme le popup. `Entrée` continue à insérer une ligne.
La complétion conserve les majuscules et remplace le mot entier si le curseur
est au milieu. Une seule annulation suffit pour revenir au texte initial.

En FR/EN, des corrections de frappe sont aussi proposées (marquées `↺`) :
lettre oubliée, répétée, remplacée, inversion ou accent manquant. Par exemple,
`bonjoru` → `bonjour`. Les mots déjà connus ne sont pas corrigés. Ces listes
issues de sous-titres contiennent aussi des noms et des formes familières :
la correction reste une aide lexicale, sans analyse grammaticale. JA/ZH/KO
bénéficient de la complétion par préfixe, sans correction approximative.
Tout fonctionne **hors ligne**, sans transmission du texte saisi.

Pour récupérer à nouveau les sources à la même révision :
`python3 scripts/update-dicts.py` (réseau nécessaire seulement pour cette
commande de maintenance). `--source-dir DOSSIER` réutilise les fichiers bruts
en local. `scripts/import-dict.py` accepte aussi un JSON local avec sa notice
de licence, et `GUNTERDOWN_DICT_PATH` permet de changer de répertoire.

Les fenêtres scindées, onglets visuels et sélection rectangulaire ne sont pas
implémentés. L'aperçu F6 génère un HTML à ouvrir dans un navigateur et se met à
jour sur un nouvel appui sur F6. Les menus, les invites, les messages courants et le manuel intégré sont
proposés en français, anglais, japonais, chinois simplifié et coréen. Les
messages techniques provenant du système ou des outils externes restent dans
leur langue d'origine. Les clusters emoji complexes ne bénéficient
pas d'une segmentation en graphèmes ; la largeur CJK et les accents combinés
ordinaires sont pris en compte.

## Exécutable gunterdown

`./gunterdown article.md` lance le programme depuis ce dépôt.
Pour obtenir un fichier unique transportable :

```sh
make build
./dist/gunterdown article.md
```

Vous pouvez copier `dist/gunterdown` où vous le souhaitez : il embarque le
code, les lexiques et le manuel. Python 3.9+ avec `curses` doit être installé
sur la machine ; l'interpréteur Python n'est pas embarqué. Le fichier est une
archive Python exécutable, compatible Linux, macOS, BSD et WSL.

`./install.sh` installe la commande `gunterdown` dans `~/.local/bin`.
Le paquet Python et le wheel s'appellent également `gunterdown`. Le module Python est `gunterdown`. La configuration se trouve dans
`~/.config/gunterdown/` ; les variables d’environnement utilisent `GUNTERDOWN_*`.

## Installer et construire

```sh
./install.sh /chemin/vers/un/prefixe
# Par défaut : ~/.local (ajouter ~/.local/bin au PATH si nécessaire)
./install.sh

make build                         # wheel et source dans dist/, hors ligne
python3 -m pip install dist/gunterdown-0.7.0-py3-none-any.whl
make build-deb                     # nécessite dpkg-deb
```

L'installation par script est isolée dans `<prefixe>/share/gunterdown` et refuse
une installation déjà présente. Pour la supprimer :

```sh
<prefixe>/share/gunterdown/uninstall.sh <prefixe>
```

Le script demande confirmation et conserve la configuration utilisateur.
L'installation standard `pip install .` utilise setuptools pour la construction.
Aucune publication PyPI, AUR ou Homebrew n'est effectuée par ces commandes.

## Langues de l'interface et de rédaction

**Alt+U** ouvre le choix de langue de l'interface (aussi accessible dans
`Outils > Langue de l’interface` et dans les préférences). Le choix est appliqué
immédiatement et sauvegardé : Français, English, 日本語, 简体中文, 한국어.
**Alt+L** choisit séparément la langue d'autocomplétion ou le mode automatique.

```sh
./dist/gunterdown --ui-lang en --lang en article.md
./dist/gunterdown --ui-lang ja --lang ja article.md
./dist/gunterdown --ui-lang ko --lang ko article.md
./dist/gunterdown --ui-lang zh --lang zh article.md
# Menus français, complétion japonaise :
./dist/gunterdown --ui-lang fr --lang ja article.md
```

`--ui-lang` choisit l'interface ; `--lang` choisit la complétion. L'interface
se configure aussi avec `ui.language` dans `config.json` (fr/en/ja/zh/ko).
Le manuel F1 est disponible dans chaque langue. La largeur des menus et des
invites est calculée en cellules de terminal, y compris pour les textes CJK.

Pour JA/ZH/KO, saisissez les caractères natifs avec votre méthode de saisie
système. Gunterdown complète le texte Unicode déjà saisi ; il n'effectue pas
de conversion romaji/pinyin/clavier latin vers des caractères asiatiques.
La détection Han seul est ambiguë entre JA et ZH : Alt+L permet de la forcer.

## Configuration

Le fichier `~/.config/gunterdown/config.json` est créé à la première sortie normale.
`GUNTERDOWN_HOME` permet d'isoler toute la configuration, les logs et la récupération.
Exemple :

```json
{
  "ui": {"theme": "dark", "language": "fr", "tree_width": 30,
         "show_line_numbers": true, "tab_size": 4},
  "editor": {"soft_wrap": true, "default_lang": "fr",
             "autocompletion": true, "autocompletion_threshold": 3,
             "auto_save_interval": 0},
  "template": {"auto_insert": "ask", "path": "", "author": "Zeima"}
}
```

L'auto-save est désactivé par défaut. Les buffers modifiés sont copiés dans
`<GUNTERDOWN_HOME>/recover/` toutes les 30 secondes et sur exception interceptée.
Au prochain lancement du même fichier, la restauration est proposée. Une
coupure avant le premier checkpoint ne peut pas être récupérée. Les snapshots
sont supprimés après sauvegarde ou abandon explicite, et après 30 jours.

`--lang` prime sur `GUNTERDOWN_LANG` au démarrage ; `Alt+L` change le choix pendant
la session. `editor.default_lang` sert de repli pour les paragraphes ambigus.
`GUNTERDOWN_NO_COLOR=1` désactive les couleurs.

`keymap.json` dans le répertoire de configuration accepte par exemple
`{"save":"Alt+1"}`. Les conflits et les raccourcis non représentables sont
rejetés.

## Thèmes

**Alt+Y** ou `Outils > Thèmes` ouvre un sélecteur avec aperçu immédiat.
`↑` / `↓` change de thème, `Entrée` applique et sauvegarde, `Échap` restaure
le thème initial. Le changement concerne le fond, le texte, la coloration
Markdown, les sélections, les titres et la barre d’état.

| Identifiant | Thème |
| --- | --- |
| `dark` | Sombre classique |
| `light` | Clair papier |
| `solarized` | Solarized sombre |
| `nord` | Nord boréal |
| `dracula` | Dracula violet |
| `ocean` | Océan bleu |
| `contrast` | Contraste élevé |

```sh
./gunterdown --theme nord article.md
./dist/gunterdown --theme light article.md
```

Les palettes s’adaptent aux terminaux 256, 16 ou 8 couleurs. `--no-color`
permet de travailler en monochrome. Un thème personnalisé est un fichier
`~/.config/gunterdown/themes/mon_theme.json`, ou sous `<GUNTERDOWN_HOME>/themes/` :

```json
{"fg": 252, "bg": 234, "accent": 81, "heading": 117,
 "selection_fg": 234, "selection_bg": 81}
```

Les indices vont de 0 à 255 (palette xterm). Les champs omis héritent du thème
sombre. Autres champs : `code`, `link`, `comment`, `quote`, `yaml`, `gutter`,
`header_bg`. Les fichiers valides apparaissent dans le sélecteur. Vous pouvez
aussi les activer avec `--theme mon_theme` ou `ui.theme` dans la configuration.

## Raccourcis et divergences du cahier des charges

`Context/` conserve les six documents initiaux. Ils décrivent des ambitions,
des versions futures et quelques raccourcis contradictoires. Le manuel
[USAGE.md](USAGE.md) décrit l'application réellement livrée.

| Action | Raccourci retenu |
| --- | --- |
| Recherche | Ctrl+W |
| Fermer le buffer | Alt+X |
| Enregistrer sous | Alt+E |
| Image | Alt+I |
| Aide raccourcis | Alt+H |
| Changer de buffer | Alt+B |
| Ouvrir les menus | F2 |
| Suggestion / focus arborescence | Tab |

`Ctrl+I` et Tab, `Ctrl+H` et Backspace sont les mêmes codes sur de nombreux
terminaux. Les combinaisons Ctrl+Shift ne sont donc pas utilisées. Tab accepte
une suggestion si elle existe, indente une sélection, sinon passe dans l'arbre.
Dans le popup, ↑/↓ ou Shift+Tab fait défiler les suggestions ; hors popup,
Shift+Tab désindente. En mode sans arbre,
Tab insère des espaces lorsqu'aucune suggestion n'est disponible.

## Validation et structure

```sh
make lint        # syntaxe 3.9, ressources, checksums et raccourcis, hors ligne
make test        # tests unitaires et vrais parcours curses dans un PTY
make verify      # vérifications + tests + construction des distributions
```

`src/gunterdown/` contient les modules, les ressources installables et le manuel.
`bin/` contient les lanceurs, `scripts/` la construction et l'import de données,
`tests/` les tests et `.github/workflows/ci.yml` la matrice Python/Linux/macOS.
Les vérifications locales ne remplacent pas une exécution de cette matrice CI.
Le seuil de couverture de 80 % du cahier des charges n'est pas encore une
condition CI ; aucun taux de couverture n'est revendiqué.

Code : MIT ; dictionnaires adaptés : CC BY-SA 4.0. Voir [LICENSE](LICENSE) et
[THIRD_PARTY_LICENSES](THIRD_PARTY_LICENSES).
