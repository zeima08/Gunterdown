# Architecture livrée

Le point d'entrée `gunterdown.tui:main` valide la configuration et les options,
charge les lexiques puis lance `curses.wrapper(Application.run)`. L'application
utilise une seule boucle monothread, avec polling de 100 ms pour l'auto-save
et les checkpoints de récupération. Les outils externes ont un timeout.

- `editor.py` : lignes Unicode, curseur, sélection continue et historique
  différentiel limité à 1000 remplacements. Sauvegarde atomique, détection de
  modifications externes, refus du remplacement accidentel en interface.
- `markdown_parser.py` : tokens par ligne ; cache texte/état/lookahead et
  propagation des états front-matter, clôture de code et commentaires.
- `treeview.py` : chargement des dossiers développés à la demande, cache par
  mtime et filtre descendant conservant les ancêtres. Aucun suivi de dossier
  symbolique. Le filtrage est borné à 64 niveaux.
- `autocomplete.py` : validation des JSON gzip, tableaux triés, recherche des
  bornes du préfixe par dichotomie puis classement par fréquence. Pas d'index
  de préfixes redondant pour limiter l'empreinte mémoire. Les mots FR/EN
  sont aussi indexés sans accents ; les variantes à une édition sont cherchées
  dans cet index sans balayage du corpus. Classement borné avec heapq.
  Le popup se compose dans la même frame curses, sous le curseur ou au-dessus
  si l'espace manque ; sélection et validation ne rafraîchissent qu'une frame.
- `detect_lang.py` : heuristiques Unicode CJK, kana/hangul, caractères Han et
  mots-outils FR/EN ; repli sur la langue précédente si texte ambigu. Pour
  les préfixes latins courts ambigus, la complétion cherche dans FR et EN.
  Les préfixes CJK courts ont un seuil adapté (ZH 1, JA/KO 2), avec recherche
  des suffixes pour les phrases japonaises/chinoises sans espaces.
- `template.py` : templates, scalaires YAML échappés, titres/ancres uniques,
  TOC entre marqueurs et numérotation ATX.
- `menus.py`, `i18n.py` : menus déclaratifs, touches normalisées, conflits
  détectés ; catalogues FR/EN/JA/ZH/KO, champs de format vérifiés par les tests,
  largeur en cellules pour les menus/invites et manuels natifs embarqués.
  `ui.language` et `--ui-lang` restent indépendants de la langue du document.
- `config.py`, `recovery.py` : configuration, remplacement atomique, snapshots
  de récupération et journal d'exception sans contenu du document.
- `export.py` : HTML de secours échappé ; outils facultatifs via subprocess
  sans shell. Export publié seulement après conversion réussie.

Le rendu prend en compte les cellules doubles CJK, les accents combinés et
l'expansion des tabulations. Le modèle conserve des positions en points de
code. Les clusters emoji complexes ne sont pas segmentés.

Les différences et fonctions différées figurent dans README.md et CHANGES.md.

`themes.py` contient les sept palettes et la conversion xterm vers ANSI.
Le sélecteur applique un aperçu sans écrire la préférence avant validation ;
une annulation restaure la palette initiale. Les thèmes JSON sont validés
au chargement et partagent le même format que les palettes intégrées.
