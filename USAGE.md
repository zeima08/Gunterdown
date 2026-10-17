# Gunterdown — Manuel d’utilisation

Version **0.7.0**.

Dans l’application, appuyez sur **F1** pour consulter le manuel, sur **Alt+H**
pour afficher les raccourcis actifs ou sur **F2** pour ouvrir les menus.

## Sommaire

- [Démarrage](#démarrage)
- [Édition et fichiers](#édition-et-fichiers)
- [Menus et aide](#menus-et-aide)
- [Rédaction Markdown](#rédaction-markdown)
- [Recherche et navigation](#recherche-et-navigation)
- [Arborescence](#arborescence)
- [Langues et autocomplétion](#langues-et-autocomplétion)
- [Affichage et thèmes](#affichage-et-thèmes)
- [Aperçu, export et outils externes](#aperçu-export-et-outils-externes)
- [Configuration et récupération](#configuration-et-récupération)
- [Limites et dépannage](#limites-et-dépannage)

## Démarrage

```sh
gunterdown [options] [fichier ou dossier]
```

### Options de lancement

| Option | Utilisation |
| --- | --- |
| `--new FICHIER` | article avec template (refuse un fichier existant) |
| `-w DOSSIER` | racine de l'arborescence |
| `-l fr\|en\|ja\|zh\|ko\|auto` | langue d'autocomplétion |
| `--ui-lang fr\|en\|ja\|zh\|ko` | langue de l'interface (indépendante) |
| `--no-lang ja,zh,ko` | désactiver des dictionnaires |
| `--no-tree, --no-color` | présentation compacte / monochrome |
| `--template FICHIER` | template alternatif |
| `--diagnostics, --version, --help` | informations sans interface |
| `--theme NOM` | Choisir le thème au lancement. |

### Premier lancement

Un menu propose trois choix (↑↓ puis Entrée ; Échap pour lancer directement) :

- Configurer : langue de l’interface, langue du document et dictionnaire,
  puis insertion du modèle d’article (demander, toujours ou jamais).
- Configuration rapide : enregistrer les réglages par défaut.
- Lancer directement : ouvrir l’éditeur et configurer plus tard.

La langue du document sert de référence à la détection automatique ;
les dictionnaires intégrés restent disponibles, selon les options --no-lang.
Retrouvez ce menu dans F2 > Outils > Préférences > Configurer.
Les lancements suivants ouvrent directement l’éditeur une fois la configuration
enregistrée. --new conserve sa demande explicite de modèle.

## Édition et fichiers

| Raccourci | Action |
| --- | --- |
| `Ctrl+S` | enregistrer |
| `Ctrl+X` | quitter |
| `Ctrl+N` | nouveau document |
| `Ctrl+O` | ouvrir |
| `Ctrl+R` | récents |
| `Alt+E` | enregistrer sous |
| `Alt+X` | fermer le document |
| `Alt+B` | choisir parmi les buffers ouverts |
| `Ctrl+U` / `Ctrl+Y` | annuler / rétablir (1000 opérations) |
| `Ctrl+A` | sélectionner tout |
| `Shift+Gauche/Droite` | étendre la sélection |
| `Ctrl+K` | couper la sélection ou la ligne |
| `Ctrl+C` / `Ctrl+V` | copier / coller (presse-papiers interne à Gunterdown) |
| `Home/End` | début/fin de ligne |
| `Ctrl+Home/End` | début/fin du document |
| `Ctrl+Gauche/Droite` | mot précédent/suivant, si le terminal les transmet |
| `PageUp/PageDown` | déplacement par page |
| `Tab` | accepter suggestion, indenter sélection, sinon focus arbre |
| `Shift+Tab` | suggestion suivante, sinon désindenter |
| `Ctrl+Space` | forcer suggestions |
| `Échap` | fermer suggestions/sélection |

Sans arbre, Tab insère des espaces si aucune suggestion n'est affichée.

## Menus et aide

| Raccourci | Action |
| --- | --- |
| `F2` | menus |
| `Gauche/Droite` | changer de menu |
| `Haut/Bas` | action |
| `Entrée` | valider |
| `Échap` | annuler ou revenir |
| `F1` | manuel |
| `Alt+H` | raccourcis actifs |
| `F12` | à propos |

Les listes et le manuel se parcourent aussi avec PageUp/PageDown.
Une fermeture d'un buffer modifié propose enregistrer/abandonner/annuler.
Les conflits de modifications sur disque demandent confirmation.

## Rédaction Markdown

| Raccourci | Action |
| --- | --- |
| `Alt+T` | template complet, avec titre, tags et résumé |
| `Alt+F` | remplacer/ajouter le front-matter (les métadonnées sont régénérées) |
| `Alt+S` | créer/actualiser le sommaire entre marqueurs TOC |
| `Alt+N` | renuméroter les titres ATX |
| `Alt+2` / `Alt+3` | titre H2/H3 |
| `Alt+C` | code |
| `Alt+Q` | citation |
| `Alt+M` | tableau |
| `Ctrl+L` | lien |
| `Alt+I` | image |
| `Alt+P` | légende image |
| `Alt+V` | vérifier blocs non fermés et ancres internes |
| `F5` | date ISO |
| `F7` | statistiques |

Ctrl+N propose complet / minimal / vide.

### Variables des templates

Les templates acceptent `{{TITLE}}`, `{{AUTHOR}}`, `{{DATE}}`, `{{LANG}}`,
`{{SLUG}}`, `{{TAGS}}`, `{{SUMMARY}}`, `{{TAGS_YAML}}`, `{{SUMMARY_YAML}}`.
Dans le template fourni, les métadonnées sont échappées en YAML.

## Recherche et navigation

| Raccourci | Action |
| --- | --- |
| `Ctrl+W` | recherche incrémentale, insensible à la casse |
| `Ctrl+D` / `Ctrl+B` | occurrence suivante / précédente, avec retour au début |
| `Ctrl+\` | remplacer ; choix toutes/première/section courante |
| `Ctrl+G` | atteindre ligne |
| `F3` | aller à un titre |

### Modes de recherche et remplacement

Préfixe `\r` : regex ; `\c` : sensible à la casse ; les deux se combinent
En regex, le remplacement accepte les groupes `\1`, `\2`, etc.

### Recherche dans plusieurs fichiers

Menu Recherche > Multi-fichiers : fichiers .md/.markdown sous la racine,
dossiers cachés et liens symboliques exclus, 1000 résultats maximum.

## Arborescence

| Raccourci | Action |
| --- | --- |
| `F9` | afficher/masquer |
| `Tab` | basculer le focus |
| `Haut/Bas` | sélection |
| `Droite/Entrée` | déplier/replier un dossier |
| `Gauche` | replier ou changer la racine vers le parent |
| `Entrée sur fichier` | ouvrir sans perdre les autres buffers |
| `n` | nouveau fichier |
| `m` | nouveau dossier |
| `r` | renommer |
| `d` | supprimer après confirmation (dossier vide uniquement) |
| `f` | filtre regex |
| `filtre vide` | annuler |
| `s` | tri |
| `.` | afficher/masquer les fichiers cachés |

Fermer un buffer avant de supprimer son fichier.
Seuls dossiers, .md, .markdown et .txt sont proposés.
Les répertoires symboliques ne sont pas suivis pour éviter les cycles.

## Langues et autocomplétion

Alt+L : choisir langue ou auto ; Alt+D : activer/désactiver complétion

### Utiliser les suggestions

La détection automatique est heuristique : forcer la langue si nécessaire.
Popup dès 3 lettres latines, 2 caractères JA/KO ou 1 caractère ZH.
↑/↓ ou Shift+Tab : choisir ; Tab : valider.
JA/ZH : complétion aussi dans les phrases sans espaces.
FR/EN : suggestions des deux langues si le préfixe latin est ambigu.
Pour saisir les caractères CJK, utiliser la méthode de saisie du système.
Gunterdown ne convertit pas le romaji ou le pinyin.
Échap : fermer ; Entrée garde son rôle de nouvelle ligne.

### Dictionnaires et correction

225615 entrées FR/EN/JA/ZH/KO issues de FrequencyWords / OpenSubtitles 2018.
Dictionnaires adaptés sous CC BY-SA 4.0 ; provenance et licence embarquées.
Correction FR/EN marquée ↺ : faute simple, accent, inversion de lettres.
Exemple : bonjoru → bonjour. Aucune modification sans validation avec Tab.
JA/ZH/KO : complétion par préfixe ; aucune correction grammaticale.
Données de sous-titres : noms, formes familières et erreurs possibles.
Aucun texte envoyé sur le réseau ; les dictionnaires sont embarqués.
Au-delà de 200000 caractères, la complétion est suspendue ; Alt+D permet
de la réactiver (éventuellement deux appuis si elle était active).

### Langue de l’interface

Alt+U : langue de l'interface ; choix sauvegardé immédiatement.
Interface et manuel FR/EN/JA/ZH/KO, indépendants de la complétion.

## Affichage et thèmes

Alt+Z : mode focus ; Alt+W : retour visuel ; Alt+# : numéros de ligne

### Choisir un thème

Alt+Y ou Outils > Thèmes : aperçu immédiat des 7 palettes.
↑/↓ : prévisualiser ; Entrée : appliquer et sauvegarder ; Échap : annuler.
dark, light, solarized, nord, dracula, ocean, contrast.
--theme NOM : choisir au lancement ; palettes adaptées à 8/16/256 couleurs.
Thèmes personnels : `GUNTERDOWN_HOME/themes/nom.json` (indices 0 à 255).

Menu Outils > Préférences : thèmes, langue de l'interface
Menu Outils > Changer dossier : modifier la racine de l'arbre

## Aperçu, export et outils externes

| Raccourci | Action |
| --- | --- |
| `F6` | régénérer un aperçu HTML temporaire, à ouvrir dans un navigateur |
| `Ctrl+E` | exporter HTML (interne), EPUB (pandoc), PDF (pandoc + xelatex) |
| `F8` | liste des mots inconnus via aspell (fr/en) |
| `Ctrl+P` | impression du texte via lpr, après confirmation |

Les fichiers d'aperçu sont supprimés à la fermeture de l'application.
Le convertisseur HTML interne gère titres/listes/emphases/liens/code,
mais pas les tableaux GFM ni l'ensemble des extensions Markdown.

Menu Fichier > Importer : txt ; org/rst via pandoc

## Configuration et récupération

### Fichiers et variables d’environnement

- `~/.config/gunterdown/config.json` ; GUNTERDOWN_HOME pour un autre répertoire
- `keymap.json` : par exemple {"save":"Alt+1"} ; conflits rejetés
- `GUNTERDOWN_DICT_PATH` : répertoire de lexiques `*.json.gz`
- `GUNTERDOWN_LANG` : langue initiale ; --lang prioritaire ; Alt+L pour changer
- `GUNTERDOWN_NO_COLOR=1` : monochrome

### Enregistrement automatique et templates

- `editor.auto_save_interval` : secondes, 0 pour désactiver (par défaut)
- `template.auto_insert` : ask, always, never ; `template.path` : template

### Récupérer un document

Les fichiers de configuration, diagnostics, crash.log et recover/ sont
tous conservés sous GUNTERDOWN_HOME. Le journal ne contient pas le document.
Checkpoints toutes les 30 secondes et sur exception interceptée.
Restaurer : rouvrir le même fichier et accepter la proposition.
Sauvegarde/abandon explicite supprime la copie ; purge après 30 jours.

## Limites et dépannage

Python 3.9+, UTF-8, Unix/macOS/BSD/WSL, curses nécessaire.
Messages techniques des outils externes conservés dans leur langue d’origine.
Pas de split, onglets visuels, sélection rectangulaire, synchronisation
du presse-papiers système ou surveillance automatique d'aperçu.
Les déplacements opèrent par point de code, pas par cluster de graphèmes.
En cas de problème, lancez `gunterdown --diagnostics` et consultez le
[README](README.md).
