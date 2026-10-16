# ARCHITECTURE — Spécification technique de Gunterdown

> Document de conception interne. Décrit l'architecture des modules, le
> modèle de données, l'algorithme d'autocomplétion hybride multilingue,
> le panneau arborescence, le parser Markdown, la boucle d'événements
> curses et les choix techniques retenus. Public visé : contributeurs et
> mainteneurs.

---

## 1. Vue d'ensemble

`Gunterdown` est architecturé autour d'une boucle d'événements monoprocessus
pilotée par `curses`. Le cœur du projet est le **buffer** (modèle de
document texte) auquel sont rattachés : un curseur, une pile d'undo/redo,
un état de sélection et une position dans le fichier. Autour du buffer
gravitent des modules indépendants responsables chacun d'un aspect
précis de l'interface (arborescence, menus, autocomplétion, parsing
Markdown, template, i18n).

Tous les modules communiquent par appels de fonctions directs — pas de
file de messages, pas de threads. L'éditeur est volontairement
monothread pour garantir la simplicité de débogage et la portabilité
sur les terminaux les plus modestes. Le seul appel asynchrone est
l'invocation optionnelle de `pandoc` pour l'aperçu live, qui se fait via
`subprocess.run` bloquant avec timeout.

### 1.1 Diagramme d'architecture (texte)

```
┌──────────────────────────────────────────────────────────────┐
│                     main() / tui.py                          │
│         Boucle curses, dispatch des touches                  │
└───────────────────────┬──────────────────────────────────────┘
                        │
   ┌────────────────────┼────────────────────────┐
   │                    │                        │
   ▼                    ▼                        ▼
┌─────────┐      ┌─────────────┐          ┌──────────────┐
│ editor  │      │  treeview   │          │    menus     │
│ buffer  │      │  file tree  │          │  shortcuts   │
│ cursor  │      │  keyboard   │          │  callbacks   │
│ undo    │      └─────────────┘          └──────────────┘
│ redo    │
└────┬────┘
     │
     ├─────────────────┬──────────────────┐
     │                 │                  │
     ▼                 ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ markdown_   │  │ autocomplete │  │  template   │
│  parser     │  │   engine     │  │   article   │
│ highlighting│  │   multilang. │  │   YAML FM   │
│ structure   │  └──────┬───────┘  └──────────────┘
└─────────────┘         │
                        │
                        ▼
                ┌──────────────┐
                │ detect_lang  │
                │  Unicode +   │
                │  frequency   │
                └──────┬───────┘
                       │
                       ▼
              ┌──────────────────┐
              │  data/dicts/*.gz │
              │  FR EN JA ZH KO  │
              └──────────────────┘
```

### 1.2 Principes directeurs

- **Zéro dépendance externe.** Toute la logique métier repose sur la
  bibliothèque standard Python. Aucun package `pip` n'est requis.
- **Modularité stricte.** Chaque module vit dans son propre fichier et
  expose une API publique minimale documentée. Les modules ne
  s'importent jamais en cycle.
- **Pas de mutation globale.** Le buffer est passé en paramètre explicite
  à toutes les fonctions qui le manipulent. Aucune variable globale
  d'état n'existe en dehors de la configuration chargée au démarrage.
- **Échec précoce.** Les erreurs de configuration (fichier manquant,
  dictionnaire corrompu, locale non UTF-8) provoquent un arrêt propre
  avec un message clair plutôt qu'un comportement silencieux dégradé.
- **Idempotence des opérations fichier.** Sauvegarder un buffer non
  modifié n'écrit rien sur le disque. Les opérations de fichier
  utilisent `os.replace()` pour garantir l'atomicité.

---

## 2. Modules

### 2.1 `tui.py` — Boucle principale

Responsabilités : initialisation curses (`curses.initscr`,
`curses.noecho`, `curses.cbreak`, `curses.raw`, `curses.start_color`,
`curses.use_default_colors`), création des fenêtres (barre de titre,
barre de menus, panneau arbo, zone d'édition, barre d'état), boucle
d'événements, dispatch des touches vers le module concerné selon le
focus actif, gestion propre de la sortie (`curses.endwin` même en cas
d'exception, via `atexit` et un wrapper `try/finally`).

### 2.2 `editor.py` — Buffer et édition

Représentation interne : liste de lignes (chaînes Python), ce qui
évite les réallocations fréquentes des chaînes immuables. Le curseur
est représenté par deux entiers `row` et `col`. La sélection par deux
paires `(row, col)` de début et fin. La pile d'undo est une liste de
snapshots différentiels (insert/delete + position), plafonnée à 1000
entrées par défaut pour limiter la mémoire.

Opérations supportées : insertion caractère, suppression avant/arrière,
coupe de ligne, indentation, déplacement curseur (flèches, mot,
début/fin de ligne, page), sélection rectangulaire et continue, copier,
coller, undo/redo. Le buffer émet un événement `modified` qui
déclenche la mise à jour de l'astérisque dans la barre de titre et
l'horodatage de dernière modification pour l'auto-save optionnel.

### 2.3 `markdown_parser.py` — Parsing et coloration

Le parser est une machine à états réduite qui reconnaît :

- Les titres ATX (`#` à `######`) et Setext (`===`, `---`)
- Les emphases `*italic*` et `**gras**`
- Le code inline (`` `code` ``) et les blocs délimités par ```` ``` ````
- Les listes ordonnées et non ordonnées
- Les citations `>`
- Les liens `[texte](url)` et images `![alt](url)`
- Les tables GFM (lignes séparées par `|` avec séparateur `---`)
- Le front-matter YAML délimité par `---` en début de fichier
- Les commentaires HTML `<!-- -->`

Le parser produit une liste de tokens qui est consommée par le moteur
de rendu curses. Chaque token porte un style (`color_pair` curses) et
une zone d'application (ligne, colonne début, colonne fin). Le parser
est incrémental : à chaque frappe, seules les lignes modifiées sont
re-parsées. Un cache de tokens par ligne est maintenu dans le buffer.

### 2.4 `treeview.py` — Panneau arborescence

Détail complet en § 4.

### 2.5 `menus.py` — Barre de menus et raccourcis

Définition déclarative des menus sous forme de dictionnaire Python
imbriqué. Chaque entrée a un libellé, un raccourci (forme `Ctrl+X`,
`Alt+L`, `F1`, etc.) et une fonction callback appelée au déclenchement.
Les raccourcis sont résolus par `curses.keyname` ou par comparaison de
`ord(c)` avec les modificateurs `Ctrl` (0x01 à 0x1A) et `Alt` (bit
0x80). Les conflits sont détectés au chargement via une analyse
statique du fichier `keymap.json`.

### 2.6 `autocomplete.py` — Moteur d'autocomplétion

Détail complet en § 3.

### 2.7 `detect_lang.py` — Détection de langue

Détail complet en § 3.3.

### 2.8 `template.py` — Template d'article

Responsabilités : chargement du template Markdown depuis
`data/templates/article.md` ou un chemin personnalisé ; substitution
des variables `{{TITLE}}`, `{{AUTHOR}}`, `{{DATE}}`, `{{LANG}}`,
`{{SLUG}}`, `{{TAGS}}`, `{{SUMMARY}}` ; insertion dans le buffer
courant à la position du curseur ou à la position 0 pour un nouveau
fichier. La fonction de slugification normalise le titre en ASCII
selon la table Unicode (via `unicodedata.normalize('NFKD', ...)` puis
suppression des combining marks).

### 2.9 `i18n.py` — Traductions de l'UI

Format : dictionnaire Python simple `{ "key": "traduction" }`. Langues
disponibles pour l'UI : `fr` (par défaut), `en`. Les chaînes de
l'interface utilisateur (menus, invites, messages d'erreur) sont
sélectionnées selon la locale du système ou `GUNTERDOWN_LANG`. Les
dictionnaires d'autocomplétion (FR/EN/JA/ZH/KO) ne sont PAS l'i18n
de l'UI — ils sont dédiés à la complétion des mots.

---

## 3. Autocomplétion hybride multilingue

### 3.1 Vue d'ensemble du mécanisme

L'autocomplétion suit trois étapes, exécutées à chaque appui de touche
qui modifie le buffer :

1. **Détection de langue active** — `detect_lang.detect(paragraph)` →
   code ISO 639-1 (`fr`, `en`, `ja`, `zh`, `ko`).
2. **Indexation du dictionnaire correspondant** — le dictionnaire est
   déjà en mémoire ; on récupère l'index par préfixe trié.
3. **Recherche du préfixe** — extraction du mot en cours à gauche du
   curseur, recherche dichotomique dans l'index, affichage des 5
   premières suggestions.

### 3.2 Dictionnaires

Les dictionnaires sont stockés dans `data/dicts/*.json.gz` au format
JSON trié par mot. Chaque entrée a la forme :

```json
{
  "word": "bonjour",
  "freq": 1234,
  "pos": ["interj", "nom"]
}
```

La fréquence sert au tri des suggestions : à préfixe égal, les mots les
plus fréquents sont proposés en premier. La catégorie grammaticale
(`pos`) est affichée dans le menu des suggestions pour aider
l'utilisateur (par exemple `(n.)` pour un nom, `(v.)` pour un verbe).

Au chargement, le moteur :

1. Ouvre le `.gz`, décompresse en mémoire.
2. Parse le JSON en une liste Python de dictionnaires.
3. Trie la liste par mot (tri lexicographique Unicode).
4. Construit un index par préfixe de 1 à 4 caractères (mapping
   `prefix → [indices...]`). Les préfixes plus longs sont cherchés par
   dichotomie directe sur la liste triée.

Mémoire typique : 90 Mo pour les 5 dictionnaires complets. L'utilisateur
peut exclure des langues via `--no-lang` pour réduire l'empreinte.

### 3.3 Algorithme de détection de langue

La détection est **hybride** dans le sens où elle combine plusieurs
signaux indépendants :

#### Étape A — Plage Unicode

Pour chaque caractère du paragraphe courant, on examine sa catégorie
via `unicodedata.category(c)` et son point de code. Les plages
suivantes déclenchent immédiatement une langue CJK :

| Plage (hex)         | Langue  |
|---------------------|---------|
| 0x3040–0x309F       | `ja` (hiragana) |
| 0x30A0–0x30FF       | `ja` (katakana) |
| 0x4E00–0x9FFF       | `zh` ou `ja` (kanji/hanzi) — ambigu, résolu par étape B |
| 0x3400–0x4DBF       | `zh` ou `ja` (CJK ext A) — ambigu |
| 0xAC00–0xD7AF       | `ko` (hangul) |
| 0xFF00–0xFFEF       | hérité CJK — typiquement `ja` ou `zh` |

Si ≥ 30 % des caractères du paragraphe tombent dans une plage
uniquement coréenne (hangul), la langue est `ko`. Si 100 % sont en
hiragana/katakana, langue `ja`. Pour les caractères `0x4E00–0x9FFF`
(hanzi/kanji communs à JA et ZH), on passe à l'étape B.

#### Étape B — Heuristique CJK

Pour distinguer JA et ZH sur les caractères communs (hanzi/kanji),
deux heuristiques sont combinées :

1. **Présence de kana.** Si le paragraphe contient au moins un
   hiragana ou katakana, c'est du japonais.
2. **Fréquence des caractères.** Une liste des 50 caractères les plus
   fréquents en chinois moderne (Rank Frequency Chinese) est comparée
   à la liste des 50 caractères les plus fréquents en japonais
   (Jōyō kanji frequency). On compte le nombre de hits dans chaque
   liste ; la langue majoritaire l'emporte.

Cette heuristique est fiable à 95 % sur des paragraphes d'au moins 50
caractères. Pour les paragraphes plus courts, le moteur conserve la
langue précédente et marque le paragraphe comme "incertain".

#### Étape C — Détection FR/EN

Pour les paragraphes composés exclusivement de caractères latins,
le moteur distingue français et anglais par deux méthodes :

1. **Mots-outils.** Une liste de 30 mots très fréquents par langue est
   comparée au paragraphe. Les mots français ("le", "la", "les", "et",
   "de", "un", "une", "des", "que", "qui", "dans", "pour", "avec",
   "sur", "par", "pas", "ne", "ce", "se", "son", "sa", "ses", "mon",
   "ma", "mes", "nous", "vous", "ils", "elles", "est") et anglais
   ("the", "and", "of", "to", "a", "an", "in", "for", "with", "on",
   "by", "not", "is", "this", "that", "his", "her", "their", "my",
   "your", "we", "you", "they", "are", "be", "have", "has", "from",
   "as") sont comptés. La langue majoritaire l'emporte.
2. **Accents.** Si le paragraphe contient des caractères accentués
   typiques du français (à, â, ç, é, è, ê, ë, î, ï, ô, û, ù) et
   aucun diacritique allemand/espagnol typique (ä, ö, ü, ß, ñ, ¿),
   la langue est française. Sinon, anglais par défaut.

Si le paragraphe contient moins de 10 mots-outils identifiables, la
langue précédente est conservée.

#### Étape D — Surcharge utilisateur

La langue détectée peut être surchargée par :

- L'option `--lang` en ligne de commande (priorité 1).
- La variable d'environnement `GUNTERDOWN_LANG` (priorité 2).
- La touche `Alt+L` pendant l'édition (priorité 3, persistante pour la
  session).
- Le champ `editor.default_lang` dans `config.json` (priorité 4, valeur
  par défaut au démarrage).

En l'absence de surcharge, l'algorithme ci-dessus s'applique paragraphe
par paragraphe, ce qui permet de mélanger plusieurs langues dans le
même document (par exemple un article en français avec des citations
en japonais — chaque paragraphe se voit attribuer la langue
correspondante).

### 3.4 Performances

- Détection de langue : < 1 ms par paragraphe de 200 caractères.
- Recherche de suggestions : < 0.5 ms pour un préfixe de 4 caractères,
  index en mémoire.
- Affichage du menu : < 2 ms (5 chaînes affichées en bas d'écran).

L'autocomplétion est désactivée automatiquement sur les fichiers de
plus de 200 000 caractères (recommandation : passer en mode sans
complétion pour économiser le CPU). L'utilisateur peut la réactiver
manuellement avec `Alt+D`.

---

## 4. Panneau arborescence

### 4.1 Représentation interne

L'arborescence est représentée par une classe `TreeNode` :

```python
@dataclass
class TreeNode:
    path: Path
    is_dir: bool
    children: list[TreeNode] = field(default_factory=list)
    expanded: bool = False
    has_md: bool = False  # contient au moins un .md (récursif)
```

Le panneau maintient :

- `root` : le `TreeNode` racine (dossier de travail).
- `visible_nodes` : liste aplatie des nœuds visibles (selon l'état
  déplié/replié), recalculée à chaque mutation.
- `cursor_index` : index dans `visible_nodes` du nœud sélectionné.

### 4.2 Chargement

Au démarrage, `treeview.build(workdir)` parcourt le dossier de travail
récursivement et construit l'arbre. Par défaut, seuls les dossiers et
les fichiers `.md`/`.markdown`/`.txt` sont retenus. Les dossiers vides
de `.md` sont repliés par défaut pour réduire la noise visuelle. Un
cache de `mtime` par dossier permet de ne recharger que les
sous-arbres modifiés au prochain appel.

### 4.3 Rendu curses

Le rendu utilise une `curses.newwin` ou une sous-fenêtre (`subwin`)
de la largeur configurée. Chaque ligne visible est affichée avec :

- Indentation proportionnelle à la profondeur (2 espaces par niveau).
- Marqueur de dossier `/` ou de fichier selon l'extension.
- Couleur distincte pour dossier (cyan), fichier `.md` (vert), fichier
  modifié (vert gras + `*`), fichier en lecture seule (rouge + `#`).
- Surbrillance de la ligne sélectionnée (couleur de fond différente).

### 4.4 Navigation

Voir `USAGE.md` § 6 pour la liste des raccourcis utilisateur. En
interne, chaque action appelle une méthode de `TreeView` :

- `move_up()`, `move_down()` : déplacent `cursor_index`.
- `toggle_expand()` : inverse `expanded` et recalcule `visible_nodes`.
- `open_node()` : si dossier, déplie ; si fichier, émet un événement
  `file_opened(path)` capté par `tui.py` qui crée un nouveau buffer.
- `create_node()`, `delete_node()`, `rename_node()` : opérations
  disque via `pathlib` + confirmation curses.

### 4.5 Filtrage

Le filtre (touche `f`) accepte une regex Python valide et la compile
avec `re.compile(pattern)`. Les nœuds dont le nom ne matche pas sont
masqués ; les dossiers ancêtres d'un nœud matché restent visibles. Un
appui sur `f` avec une chaîne vide désactive le filtre.

### 4.6 Tri

Le tri par défaut est alphabétique avec dossiers en premier,
insensible à la casse et aux diacritiques. La fonction de tri
normalise via `unicodedata.normalize('NFKD', name.lower())` puis
supprime les combining marks pour éviter que « É » vienne après « Z ».

---

## 5. Parser Markdown — implémentation

### 5.1 Stratégie incrémentale

Le parser ne re-traite pas tout le buffer à chaque frappe. Il maintient
un cache `line_tokens: dict[int, list[Token]]` dans le buffer. À
chaque modification :

1. Identifier la ligne modifiée.
2. Re-parser cette ligne et la suivante si elle est la continuation
   d'un bloc (par exemple, une liste multi-lignes).
3. Si la modification change la structure d'un bloc (passage de
   paragraphe à liste, par ex.), re-parser tout le bloc concerné.

Cette stratégie donne une réactivité correcte même sur des fichiers
de 10 000 lignes. Au pire cas (modification du front-matter YAML qui
affecte la structure entière), un re-parse complet reste sous 50 ms
pour 10 000 lignes.

### 5.2 Tokens

Les tokens sont des `dataclass` immuables :

```python
@dataclass(frozen=True)
class Token:
    kind: str           # "h1", "h2", "bold", "italic", "code",
                        # "code_block", "list", "link", "image",
                        # "quote", "table", "hr", "yaml_fm",
                        # "comment"
    start: int          # colonne de début (incluse)
    end: int            # colonne de fin (exclue)
    payload: dict       # données spécifiques (url, alt, lang, ...)
```

Le moteur de rendu curse associe à chaque `kind` une `curses.color_pair`
définie dans le thème courant.

### 5.3 Gestion des blocs multi-lignes

Les blocs de code (` ``` `), les citations (`>`) et les tables GFM
peuvent s'étendre sur plusieurs lignes. Le parser maintient un état
`block_stack` qui mémorise les blocs ouverts. À chaque nouvelle ligne,
le parser essaie de fermer les blocs dont la signature de fin est
détectée. En cas d'incertitude, il conserve l'état précédent (réduit
les faux négatifs au prix de faux positifs occasionnels — acceptable
pour la coloration, qui n'a pas besoin d'être parfaite).

---

## 6. Boucle d'événements

### 6.1 Schéma

```python
def main_loop(stdscr):
    while True:
        ch = stdscr.getch()
        if ch == -1:
            continue
        if focus == Focus.TREE:
            treeview.dispatch(ch)
        elif focus == Focus.EDITOR:
            editor.dispatch(ch)
        elif focus == Focus.MENU:
            menus.dispatch(ch)
        redraw(stdscr)
```

`getch()` est bloquant par défaut, mais `stdscr.timeout(50)` est
utilisé pour permettre à un thread d'auto-save périodique (lancé via
`threading.Timer`) d'interagir avec le buffer via un lock. En pratique,
l'auto-save est désactivé par défaut ; quand activé, il utilise une
approche "dirty flag polling" plutôt qu'un thread.

### 6.2 Résolution des touches

`curses.keyname(ch)` retourne une chaîne comme `"^S"`, `"KEY_UP"`,
`"^[L"` (Alt+L), etc. Le dispatcher normalise cette chaîne en
`Ctrl+S`, `Up`, `Alt+L` et la compare au `keymap` actuel. Les touches
non reconnues sont ignorées silencieusement, à l'exception de celles
qui dépassent 32 bits (caractères CJK via IME), qui sont insérées
directement dans le buffer.

### 6.3 Caractères multi-octets

`curses` sous Python 3 retourne directement le codepoint Unicode pour
les caractères larges, ce qui simplifie l'insertion des CJK. Le buffer
stocke les caractères comme des `str` Python (donc des points de
code), pas comme des octets. La fonction `len(ligne)` compte les
caractères Unicode (et non les octets UTF-8), ce qui correspond à
l'affichage curseur attendu pour les langues CJK.

---

## 7. Gestion des erreurs

| Erreur                                    | Comportement                                          |
|-------------------------------------------|-----------------------------------------------------|
| Locale non UTF-8                          | Avertissement + refus de démarrer                    |
| Dictionnaire manquant                      | Avertissement + autocompl. désactivée pour la langue |
| Fichier trop gros (> 5 Mo)                 | Confirmation demandée à l'ouverture                 |
| Permissions insuffisantes en écriture     | Erreur curses affichée, sauvegarde refusée          |
| `pandoc` absent                            | Aperçu live et export EPUB/PDF désactivés            |
| Crash interne                              | Dump de l'exception dans `~/.gunterdown/crash.log` + écran d'erreur |
| Terminal trop petit (< 80×24)             | Avertissement + passage en mode "compact"            |

Le fichier `~/.gunterdown/crash.log` est tronqué à 1 Mo pour éviter la
croissance infinie. Chaque entrée contient l'horodatage, la version
de `Gunterdown`, la pile d'appels et le buffer courant (longueur et 100
premiers caractères).

---

## 8. Tests

Tests unitaires avec `pytest` (dépendance de développement uniquement)
dans `tests/`. Les tests curses utilisent le pattern "double test" :
une couche de logique pure (sans curses) testée avec `pytest`, et une
couche de rendu testée via `curses.wrapper` dans un pseudo-terminal
`pexpect`. Couverture cible : 80 % pour la logique, 60 % pour le
rendu curses (difficile à tester exhaustivement).

Voir `CONTRIBUER.md` § 3 pour la procédure complète.

---

## English summary

`Gunterdown` is a single-process, single-thread curses application. Its core
is the `Buffer` model (list of lines, cursor, undo/redo stack, dirty
flag). Surrounding modules — `editor`, `treeview`, `menus`,
`markdown_parser`, `autocomplete`, `detect_lang`, `template`, `i18n` —
are independent and communicate via direct function calls. The
multilingual autocompletion is hybrid: language is detected per
paragraph using Unicode ranges for CJK, frequency-based heuristics to
disambiguate JA vs ZH, and a stopword-list approach to distinguish FR
from EN. The user can override detection with `--lang`, `GUNTERDOWN_LANG`,
`Alt+L` or `config.json`. Dictionaries are compressed JSON, loaded
into memory at startup and indexed by prefix for O(log n) lookup. The
Markdown parser is incremental: only the modified line (and its
containing block) is re-parsed on each keystroke, keeping response
time under 50 ms for files up to 10 000 lines. The file-tree panel
uses a `TreeNode` recursive structure with on-demand loading via
`mtime` caching. All filesystem writes are atomic (`os.replace`).
The main event loop blocks on `getch`, dispatches to the active focus
(editor / tree / menu), and redraws in a single pass.
