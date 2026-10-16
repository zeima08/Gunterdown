# USAGE — Guide d'utilisation de Gunterdown

> Manuel utilisateur quotidien : lancement, menus, raccourcis clavier,
> template d'article, autocomplétion multilingue, panneau arborescence,
> recherche et remplacement, export. Public visé : utilisateurs et
> rédacteurs techniques.

---

## 1. Lancement

### 1.1 Syntaxe générale

```bash
gunterdown [options] [fichier]
```

Si aucun fichier n'est fourni, `Gunterdown` ouvre un nouveau buffer non
sauvegardé nommé `sans_titre.md`. Si le fichier passé n'existe pas, il est
créé à la première sauvegarde. Si un répertoire est passé, `Gunterdown` ouvre
l'éditeur avec le panneau arborescence positionné sur ce répertoire.

### 1.2 Options courantes

| Option              | Argument       | Description                                  |
|---------------------|----------------|----------------------------------------------|
| `-h, --help`        | —              | Affiche l'aide et quitte                     |
| `-V, --version`     | —              | Affiche la version et quitte                 |
| `--new FICHIER`     | chemin         | Crée un nouveau fichier avec template        |
| `-l, --lang`        | fr/en/ja/zh/ko | Force la langue d'autocomplétion au démarrage |
| `--no-lang`         | liste          | Désactive des langues (ex: `ja,zh,ko`)       |
| `-w, --workdir`     | chemin         | Dossier de travail (panneau arbo)             |
| `--no-color`        | —              | Désactive la couleur                          |
| `--no-tree`         | —              | Cache le panneau arborescence au démarrage    |
| `--diagnostics`     | —              | Affiche infos système et dictionnaires        |
| `--template FICHIER`| chemin         | Utilise un template alternatif                |

### 1.3 Exemples

```bash
# Ouvrir un fichier existant
gunterdown mon_article.md

# Créer un nouvel article avec template
gunterdown --new article.md

# Forcer l'autocomplétion en japonais
gunterdown -l ja article.md

# Ouvrir avec un dossier de travail précis
gunterdown -w ~/Projets/articles article.md

# Désactiver les dictionnaires CJK pour économiser la mémoire
gunterdown --no-lang ja,zh,ko article.md

# Mode sans couleur (utile dans un terminal SSH limité)
gunterdown --no-color article.md
```

---

## 2. Interface générale

L'écran se divise en cinq zones, de haut en bas :

1. **Barre de titre** (1 ligne) : nom du fichier, modifié (`*`), langue
   active d'autocomplétion, position du curseur (ligne, colonne).
2. **Barre de menus** (1 ligne) : `Fichier`, `Édition`, `Recherche`,
   `Article`, `Outils`, `Aide`. Navigation au clavier (voir § 3).
3. **Panneau arborescence** (30 % de largeur par défaut, à gauche) :
   dossiers et fichiers `.md` du dossier courant. Masquable avec `F9`.
4. **Zone d'édition** (reste de l'écran) : buffer courant, coloration
   Markdown, curseur, soft-wrap optionnel.
5. **Barre d'état** (1 ligne, en bas) : raccourcis contextuels
   (`^S Enregistrer`, `^X Quitter`, `F1 Aide`), compteur de mots.

Le panneau arborescence et la zone d'édition partagent le focus. La touche
`Tab` permet de basculer entre les deux. Le panneau actif est signalé par
une bordure de couleur d'accent (vert par défaut, configurable).

---

## 3. Menus

La barre de menus s'ouvre au clavier. Trois façons d'accéder à un menu :

- Appuyer sur `F2` puis naviguer avec `← →` et `↑ ↓`.
- Taper `Alt+lettre` où `lettre` est la lettre soulignée du menu
  (`Alt+F` = Fichier, `Alt+É` = Édition, `Alt+R` = Recherche, `Alt+A` =
  Article, `Alt+O` = Outils, `Alt+A` = Aide — conflit géré par ordre).
- Taper directement le raccourci d'action (les raccourcis sont listés
  dans chaque menu déroulant).

### 3.1 Menu Fichier

| Action                | Raccourci  | Description                                |
|-----------------------|------------|--------------------------------------------|
| Nouveau               | `Ctrl+N`   | Crée un buffer vierge (template demandé)    |
| Ouvrir...             | `Ctrl+O`   | Ouvre un fichier via dialogue               |
| Ouvrir récent         | `Ctrl+R`   | Liste des 10 derniers fichiers             |
| Enregistrer           | `Ctrl+S`   | Sauvegarde le buffer courant                |
| Enregistrer sous...   | `Ctrl+Shift+S` | Sauvegarde sous un nouveau nom          |
| Enregistrer tout      | `Ctrl+Alt+S` | Sauvegarde tous les buffers modifiés      |
| Fermer                | `Ctrl+W`   | Ferme le buffer (confirmation si modifié)   |
| Importer...           | —          | Importe `.txt`, `.org`, `.rst` (via pandoc) |
| Exporter...           | `Ctrl+E`   | Export HTML/EPUB/PDF (via pandoc)           |
| Imprimer              | `Ctrl+P`   | Envoie vers `lpr` ou cmd d'impression       |
| Quitter               | `Ctrl+X`   | Quitte l'éditeur (confirmation si modifs)   |

### 3.2 Menu Édition

| Action                | Raccourci      | Description                                |
|-----------------------|----------------|--------------------------------------------|
| Annuler               | `Ctrl+U`       | Undo (historique illimité)                 |
| Rétablir              | `Ctrl+Y`       | Redo                                       |
| Couper                | `Ctrl+K`       | Coupe la ligne ou sélection courante       |
| Copier                | `Ctrl+C`       | Copie la sélection                          |
| Coller                | `Ctrl+V`       | Colle le presse-papiers                     |
| Sélectionner tout     | `Ctrl+A`       | Sélectionne tout le buffer                  |
| Indenter              | `Tab`          | Indente la sélection (4 espaces)           |
| Désindenter           | `Shift+Tab`    | Désindente la sélection                     |
| Commenter/décommenter | `Ctrl+/`       | Bascule les commentaires HTML `<!-- -->`    |
| Insérer date          | `F5`           | Insère la date au format ISO                |
| Insérer lien          | `Ctrl+L`       | Insère `[texte](url)` avec dialogue         |
| Insérer image         | `Ctrl+I`       | Insère `![alt](chemin)` avec dialogue       |

### 3.3 Menu Recherche

| Action                | Raccourci  | Description                                |
|-----------------------|------------|--------------------------------------------|
| Rechercher             | `Ctrl+W`   | Recherche incrémentale                     |
| Rechercher/suivant    | `Ctrl+D`   | Occurrence suivante                        |
| Rechercher/précédent  | `Ctrl+B`   | Occurrence précédente                      |
| Remplacer              | `Ctrl+\\`  | Recherche + remplacement                    |
| Atteindre ligne        | `Ctrl+G`   | Demande un numéro de ligne                 |
| Aller à la définition  | `F3`       | Saute vers un titre (H1-H3)                |

### 3.4 Menu Article

Ce menu est spécifique à `Gunterdown` : il regroupe les actions liées au
template d'article Markdown.

| Action                      | Raccourci    | Description                            |
|-----------------------------|--------------|----------------------------------------|
| Insérer le template complet | `Alt+T`      | Insère le squelette article.md         |
| Ajouter front-matter YAML   | `Alt+F`      | Insère/édite le bloc YAML d'en-tête    |
| Générer sommaire (TOC)      | `Alt+S`      | Insère une TOC à partir des H1-H3      |
| Renumber titres             | `Alt+N`      | Recalcule la numérotation des titres   |
| Insérer section H2          | `Alt+2`      | `## ` + placeholder                    |
| Insérer section H3          | `Alt+3`      | `### ` + placeholder                   |
| Insérer bloc de code        | `Alt+C`      | ```` ```lang ``` ````                  |
| Insérer citation            | `Alt+Q`      | `> ` + placeholder                     |
| Insérer tableau 3×3         | `Alt+M`      | Tableau GFM par défaut                  |
| Insérer légende image      | `Alt+P`      | `![alt](url) *Légende*`                |
| Vérifier le Markdown        | `Alt+V`      | Lance une vérification de syntaxe      |

### 3.5 Menu Outils

| Action                | Raccourci  | Description                                |
|-----------------------|------------|--------------------------------------------|
| Aperçu live           | `F6`       | Rendu HTML via `pandoc` (si installé)       |
| Compter les mots      | `F7`       | Affiche statistiques (mots, caractères)     |
| Vérifier l'orthographe| `F8`       | Appelle `aspell` si disponible              |
| Forcer langue auto.   | `Alt+L`    | Force la langue d'autocomplétion            |
| Mode focus            | `Alt+Z`    | Cache tout sauf la zone d'édition           |
| Wrapping souple       | `Alt+W`    | Bascule le soft-wrap                        |
| Numéros de ligne      | `Alt+#`    | Bascule les numéros de ligne                |

### 3.6 Menu Aide

| Action                | Raccourci  | Description                                |
|-----------------------|------------|--------------------------------------------|
| Manuel                | `F1`       | Ouvre l'aide intégrée                      |
| Raccourcis            | `Ctrl+H`   | Liste des raccourcis                       |
| À propos              | `F12`      | Affiche la fenêtre « À propos »             |
| Diagnostics           | `Ctrl+?`   | Affiche infos système                      |

---

## 4. Template d'article

### 4.1 Présentation

Lorsque vous créez un nouveau fichier avec `gunterdown --new article.md` ou
`Ctrl+N`, l'éditeur propose d'insérer un template complet. Trois choix :

1. **Template complet** — front-matter YAML + structure d'article complète
2. **Template minimal** — uniquement front-matter + titre + résumé
3. **Aucun template** — buffer vide

Le template par défaut est configurable via `~/.config/gunterdown/templates/article.md`.
Voir `USAGE.md` § 4.3 pour les variables personnalisables.

### 4.2 Template complet par défaut

```markdown
---
title: "Titre de l'article"
author: "Auteur"
date: "2026-10-17"
lang: "fr"
slug: "titre-de-larticle"
tags: ["tag1", "tag2"]
summary: |
  Résumé en une ou deux phrases.
  Deuxième ligne du résumé si nécessaire.
status: "draft"
license: "CC BY-SA 4.0"
---

# Titre de l'article

> Résumé court affiché en haut de page, une à deux phrases, qui donne au
> lecteur l'envie de continuer. Doit contenir le sujet, l'angle et la
> promesse de l'article.

## Sommaire

1. [Introduction](#introduction)
2. [Contexte](#contexte)
3. [Développement](#developpement)
4. [Conclusion](#conclusion)
5. [Références](#references)

## Introduction

Paragraphe d'introduction. Trois à cinq phrases présentant le contexte,
la question traitée et la promesse de l'article.

## Contexte

Paragraphe de mise en perspective. Données chiffrées, citations, références
externes pour étayer le propos.

### Sous-section

Détails techniques ou anecdotes illustrant le contexte.

## Développement

Corps de l'article. Plusieurs sections et sous-sections.

### Argument 1

Premier argument avec exemples concrets.

### Argument 2

Deuxième argument avec contre-exemples et nuance.

## Conclusion

Synthèse et ouverture. Trois à cinq phrases récapitulant le propos et
ouvrant sur une question ou une perspective future.

## Références

- Auteur, *Titre*, Éditeur, année. URL consultée le AAAA-MM-JJ.
- Auteur, *Titre*, Éditeur, année.
```

### 4.3 Variables personnalisables

Le template accepte des variables substituées à l'insertion. La
substitution est demandée via un dialogue après insertion.

| Variable         | Substitution par défaut            | Personnalisable |
|------------------|-------------------------------------|-----------------|
| `{{TITLE}}`      | Demande à l'utilisateur             | Oui             |
| `{{AUTHOR}}`      | Lu depuis `config.json`             | Oui             |
| `{{DATE}}`       | Date du jour ISO (AAAA-MM-JJ)        | Oui             |
| `{{LANG}}`       | Locale du système                   | Oui             |
| `{{SLUG}}`       | Slug du titre (ASCII)               | Oui             |
| `{{TAGS}}`       | Demande à l'utilisateur             | Oui             |
| `{{SUMMARY}}`    | Laisser vide à remplir               | Oui             |

Pour créer votre propre template, copiez le fichier par défaut :

```bash
mkdir -p ~/.config/gunterdown/templates
cp /opt/gunterdown/data/templates/article.md ~/.config/gunterdown/templates/
```

Éditez-le à votre guise puis indiquez le chemin dans `config.json` :

```json
{
  "template": {
    "auto_insert": "ask",
    "path": "~/.config/gunterdown/templates/article.md"
  }
}
```

La clé `"auto_insert"` accepte `"ask"` (demande), `"always"` (toujours) ou
`"never"` (jamais).

---

## 5. Autocomplétion multilingue

### 5.1 Principe

L'autocomplétion propose des mots à mesure que vous tapez. Le dictionnaire
actif est choisi automatiquement par détection de langue sur le paragraphe
courant (voir `ARCHITECTURE.md` § 3 pour l'algorithme). Vous pouvez
forcer une langue manuellement avec `Alt+L`.

### 5.2 Raccourcis d'autocomplétion

| Raccourci     | Action                                            |
|---------------|---------------------------------------------------|
| `Tab`         | Accepte la suggestion principale                   |
| `Shift+Tab`   | Passe à la suggestion suivante                      |
| `Esc`         | Ferme le menu des suggestions                       |
| `Alt+L`       | Force la langue (dialogue : fr/en/ja/zh/ko/auto)    |
| `Alt+D`       | Désactive/active temporairement l'autocomplétion   |
| `Ctrl+Space`  | Force l'affichage du menu des suggestions          |

Le seuil de déclenchement par défaut est 3 caractères (configurable dans
`config.json` → `editor.autocompletion_threshold`). Au-dessous de ce
seuil, aucune suggestion n'apparaît, ce qui évite de polluer l'écran
pendant la frappe de mots courts.

### 5.3 Langues supportées

| Code | Langue    | Exemple suggestion        |
|------|-----------|---------------------------|
| `fr` | Français  | « bon » → « bonjour »     |
| `en` | Anglais   | « hel » → « hello »       |
| `ja` | Japonais  | « こん » → « こんにちは » |
| `zh` | Chinois   | « 你 » → « 你好 »          |
| `ko` | Coréen    | « 안녕 » → « 안녕하세요 »  |

La détection hybride combine :

1. **Détection par plage Unicode** — les caractères CJK déclenchent
   immédiatement le dictionnaire JA/ZH/KO selon la plage exacte.
2. **Détection par analyse de fréquence** — pour distinguer FR et EN,
   l'éditeur compte les mots communs dans le paragraphe et choisit la
   langue majoritaire.
3. **Détection par préférence utilisateur** — si `GUNTERDOWN_LANG` est défini
   ou si `--lang` est passé, ce choix prioritaire court-circuite la
   détection automatique.

Voir `ARCHITECTURE.md` § 3 pour l'algorithme complet et les seuils.

---

## 6. Panneau arborescence

### 6.1 Navigation

Le panneau arborescence affiche le contenu du dossier de travail. Seuls
les fichiers `.md`, `.markdown`, `.txt` et les dossiers sont listés par
défaut (filtre configurable via `config.json`).

| Touche        | Action                                              |
|---------------|-----------------------------------------------------|
| `Tab`         | Bascule focus entre arbo et zone d'édition          |
| `↑ ↓`         | Déplace la sélection                                 |
| `→`           | Ouvre le dossier sélectionné                        |
| `←`           | Remonte d'un niveau (parent)                         |
| `Entrée`      | Ouvre le fichier `.md` dans un nouveau buffer        |
| `n`           | Crée un nouveau fichier (template demandé)          |
| `d`           | Supprime (après confirmation)                       |
| `r`           | Renomme                                              |
| `m`           | Crée un nouveau dossier                              |
| `f`           | Filtre (regex sur les noms de fichiers)              |
| `.`           | Affiche/masque les fichiers cachés                  |
| `F9`          | Masque le panneau arborescence                       |

### 6.2 Marqueurs visuels

| Marqueur | Signification                                |
|----------|-----------------------------------------------|
| `/`      | Dossier                                       |
| `*`      | Fichier modifié (non sauvegardé)              |
| `#`      | Fichier en lecture seule                       |
| `@`      | Lien symbolique                                |
| `…`      | Dossier replié contenant des sous-éléments    |

### 6.3 Tri

Par défaut, l'arborescence est triée alphabétiquement avec les dossiers
en premier. Appuyer sur `s` ouvre un menu de tri :

1. Alphabétique A→Z
2. Alphabétique Z→A
3. Date de modification (récent en premier)
4. Taille (décroissante)

Le tri choisi est conservé pour la session et sauvegardé dans `config.json`.

---

## 7. Recherche et remplacement

### 7.1 Recherche incrémentale

`Ctrl+W` ouvre une invite en bas d'écran. Tapez votre recherche ; les
occurrences sont surlignées en temps réel et le curseur se positionne sur
la première occurrence. La recherche est insensible à la casse par défaut ;
préfixez par `\c` pour forcer la casse, ou activez la regex avec `\r`.

### 7.2 Remplacement

`Ctrl+\` ouvre une invite à deux champs : recherche et remplacement.
Options disponibles à l'écran :

- `c` — respecter la casse
- `r` — expression régulière
- `a` — remplacer toutes les occurrences
- `b` — limiter au bloc de section courant

### 7.3 Recherche multi-fichiers

Le menu `Recherche > Multi-fichiers` ouvre une vue spécifique qui
parcourt tous les `.md` du dossier de travail. Résultats affichés dans
le panneau arborescence ; `Entrée` ouvre le fichier à la ligne trouvée.

---

## 8. Export

Le menu `Fichier > Exporter` (`Ctrl+E`) propose trois formats :

- **HTML** : convertit le Markdown en HTML autonome via `pandoc` si
  installé, sinon via un convertisseur interne basique.
- **EPUB** : uniquement si `pandoc` est disponible.
- **PDF** : passe par `pandoc` + `xelatex` (recommandé pour le support
  CJK). Voir `INSTALL.md` § 1.2 pour les polices requises.

Si `pandoc` n'est pas installé, l'export HTML utilise un convertisseur
interne limité (titres, listes, emphases, liens, blocs de code). Les
tableaux GFM ne sont pas pris en charge par ce convertisseur de secours.

---

## 9. Personnalisation

### 9.1 Thèmes

Trois thèmes sont livrés : `dark` (par défaut), `light`, `solarized`. Le
thème se choisit dans `config.json` → `ui.theme` ou via le menu
`Outils > Préférences`. Vous pouvez créer un thème personnel dans
`~/.config/gunterdown/themes/mon_theme.json` en copiant un thème existant.

### 9.2 Raccourcis personnalisés

Le fichier `~/.config/gunterdown/keymap.json` permet de redéfinir tous les
raccourcis. Format :

```json
{
  "save": "Ctrl+S",
  "quit": "Ctrl+X",
  "open_tree": "F9",
  "force_lang": "Alt+L"
}
```

Les conflits sont détectés au démarrage et signalés par un avertissement.

---

## 10. Bonnes pratiques de rédaction

- **Un fichier = un article.** Gardez vos `.md` atomiques ; utilisez le
  front-matter pour les métadonnées plutôt que des dossiers imbriqués.
- **Section ≤ 200 mots.** Au-delà, scindez en sous-sections ; la
  génération automatique de TOC reste lisible.
- **Noms de fichiers en slug ASCII.** Le slug est généré automatiquement
  quand vous utilisez le template ; sinon, utilisez `kebab-case`.
- **Préfixe de version.** Pour les brouillons, préfixez par `draft_` ou
  utilisez le champ `status: "draft"` dans le front-matter.
- **Sauvegarde fréquente.** `Ctrl+S` à chaque fin de paragraphe ;
  l'auto-save toutes les 30 secondes est activable dans
  `config.json` → `editor.auto_save_interval`.

---

## English summary

`Gunterdown` is launched with `gunterdown [options] [file]`. The interface has five
zones: title bar, menu bar (File, Edit, Search, Article, Tools, Help),
file-tree panel, editing area, status bar. Keyboard shortcuts follow
the `nano` convention (`^S` save, `^X` quit, `F1` help, `F2` menu, `F12`
about). The built-in article template is inserted on file creation and
provides YAML front-matter, title, summary, table of contents, section
skeleton and references — fully customizable via `~/.config/gunterdown/
templates/article.md`. Multilingual autocompletion (FR/EN/JA/ZH/KO) is
hybrid: it auto-detects the active language using Unicode ranges and
word-frequency analysis, and can be manually overridden with `Alt+L`.
The file-tree panel supports navigation, creation, deletion, renaming
and filtering via keyboard shortcuts. Export to HTML/EPUB/PDF relies on
`pandoc` when available, with a fallback converter for basic HTML.
