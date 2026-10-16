# Changements

## Nom du projet et thèmes

- Nom unique `gunterdown` pour le module Python, les lanceurs, les paquets,
  les variables GUNTERDOWN_* et le répertoire ~/.config/gunterdown/.
- Sources, documentation, manuels, scripts et données de distribution alignés.
- Sept palettes intégrales : dark, light, solarized, nord, dracula, ocean,
  contrast, avec adaptation 8/16/256 couleurs et possibilité monochrome.
- Alt+Y / Outils > Thèmes : aperçu, confirmation enregistrée, annulation
  restaurant la palette initiale. Thèmes personnels JSON et option --theme.

## Interfaces et complétion multilingues

- Menus, invites, messages courants, aide et raccourcis traduits en EN/JA/ZH/KO
  en plus du français ; chinois simplifié pour l'interface ZH.
- Alt+U / Outils > Langue de l’interface : choix appliqué et sauvegardé.
  Option --ui-lang indépendante de --lang et Alt+L pour la complétion.
- Seuils de complétion adaptés : ZH 1 caractère, JA/KO 2, latin 3 par défaut.
  Recherche de suffixes CJK pour les phrases sans espaces ; suggestions FR/EN
  combinées et identifiées pour les préfixes latins courts ambigus.
- Largeur des menus, alignement et position dans les invites calculés en
  cellules de terminal pour éviter les chevauchements CJK.
- Tests des catalogues et parcours clavier natifs pour les quatre langues.

## Popup et dictionnaires

- Popup de complétion au curseur, cinq choix maximum ; ↑/↓ ou Shift+Tab
  sélectionne, Tab valide, Échap ferme et Entrée insère une ligne.
- Correction FR/EN à une édition avec recherche d'accents ; validation
  explicite, conservation de casse, remplacement du mot entier et undo.
- 225615 entrées FrequencyWords / OpenSubtitles 2018 réparties sur FR/EN/JA/ZH/KO.
  Révision figée, transformation reproductible, provenance, checksums et
  notices CC BY-SA 4.0 embarqués ; complément de vocabulaire original.
- Traitement hors ligne ; aucune requête réseau depuis l'éditeur.

## Correction du rafraîchissement

- Menus et dialogues composés avec l'éditeur avant un unique affichage curses,
  sans afficher brièvement l'éditeur seul sous la fenêtre ouverte.
- Aucun rafraîchissement des fenêtres modales sur les timeouts clavier.
- Curseur masqué dans les menus/listes/aide et restauré dans les invites
  et l'éditeur pour éviter ses déplacements visibles entre les zones.
- Test dans un pseudo-terminal : stabilité au repos, navigation de menu,
  redimensionnement, recherche, aide et confirmation de fermeture.

## Nom du programme

- Le programme et sa commande s'appellent désormais `gunterdown`.
- Lanceur `./gunterdown`, exécutable transportable `dist/gunterdown` généré
  par `make build`, commande installée et distributions renommées.
- Le module Python et la configuration portent le même nom que le programme.

## 0.7.0 — 2026-10-16

Première version exécutable de Gunterdown.

- Édition Unicode, sélection continue, historique différentiel plafonné à
  1000 opérations, indentation, navigation, presse-papiers interne.
- Sauvegarde atomique avec conservation des permissions et contrôle des
  modifications externes ; sauvegarde sous un nouveau nom et buffers multiples.
- Coloration Markdown avec cache des lignes et propagation des états de bloc.
- Arborescence chargée à la demande, filtres regex, tri, fichiers cachés,
  création, renommage et suppression confirmée de fichiers/dossiers vides.
- Templates complet/minimal, métadonnées, sommaire et numérotation des titres.
- Détection FR/EN/JA/ZH/KO et petits lexiques originaux avec recherche binaire.
- Recherche incrémentale, remplacement, recherche dans les fichiers.
- HTML interne ; intégrations optionnelles pandoc, xelatex, aspell et lpr.
- Checkpoints de récupération, diagnostics et configuration JSON.
- Manuel intégré, menus FR/EN, personnalisation des raccourcis et thèmes.
- Distribution wheel/sdist hors ligne, installation isolée, paquet Debian.

Les corpus linguistiques complets, les fenêtres scindées, les onglets visuels,
la sélection rectangulaire et la publication AUR/Homebrew restent à réaliser.
L'aperçu HTML est régénéré sur F6, sans surveillance automatique du navigateur.
