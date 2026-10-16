Gunterdown — Manuel de la version 0.7.0

DÉMARRAGE
  gunterdown [options] [fichier ou dossier]
  --new FICHIER : article avec template (refuse un fichier existant)
  -w DOSSIER : racine de l'arborescence
  -l fr|en|ja|zh|ko|auto : langue d'autocomplétion
  --ui-lang fr|en|ja|zh|ko : langue de l'interface (indépendante)
  --no-lang ja,zh,ko : désactiver des dictionnaires
  --no-tree, --no-color : présentation compacte / monochrome
  --template FICHIER : template alternatif
  --diagnostics, --version, --help : informations sans interface

ÉDITION ET FICHIERS
  Ctrl+S : enregistrer ; Ctrl+X : quitter
  Ctrl+N : nouveau document ; Ctrl+O : ouvrir ; Ctrl+R : récents
  Alt+E : enregistrer sous ; Alt+X : fermer le document
  Alt+B : choisir parmi les buffers ouverts
  Ctrl+U / Ctrl+Y : annuler / rétablir (1000 opérations)
  Ctrl+A : sélectionner tout ; Shift+Gauche/Droite : étendre la sélection
  Ctrl+K : couper la sélection ou la ligne
  Ctrl+C / Ctrl+V : copier / coller (presse-papiers interne à Gunterdown)
  Home/End : début/fin de ligne ; Ctrl+Home/End : début/fin du document
  Ctrl+Gauche/Droite : mot précédent/suivant, si le terminal les transmet
  PageUp/PageDown : déplacement par page
  Tab : accepter suggestion, indenter sélection, sinon focus arbre
  Shift+Tab : suggestion suivante, sinon désindenter
  Ctrl+Space : forcer suggestions ; Échap : fermer suggestions/sélection
  Sans arbre, Tab insère des espaces si aucune suggestion n'est affichée.

MENUS ET AIDE
  F2 : menus ; Gauche/Droite : changer de menu ; Haut/Bas : action
  Entrée : valider ; Échap : annuler ou revenir
  F1 : manuel ; Alt+H : raccourcis actifs ; F12 : à propos
  Les listes et le manuel se parcourent aussi avec PageUp/PageDown.
  Une fermeture d'un buffer modifié propose enregistrer/abandonner/annuler.
  Les conflits de modifications sur disque demandent confirmation.

ARTICLE
  Alt+T : template complet, avec titre, tags et résumé
  Ctrl+N propose complet / minimal / vide
  Alt+F : remplacer/ajouter le front-matter (les métadonnées sont régénérées)
  Alt+S : créer/actualiser le sommaire entre marqueurs TOC
  Alt+N : renuméroter les titres ATX
  Alt+2 / Alt+3 : titre H2/H3
  Alt+C : code ; Alt+Q : citation ; Alt+M : tableau
  Ctrl+L : lien ; Alt+I : image ; Alt+P : légende image
  Alt+V : vérifier blocs non fermés et ancres internes
  F5 : date ISO ; F7 : statistiques
  Les templates acceptent {{TITLE}}, {{AUTHOR}}, {{DATE}}, {{LANG}},
  {{SLUG}}, {{TAGS}}, {{SUMMARY}}, {{TAGS_YAML}}, {{SUMMARY_YAML}}.
  Dans le template fourni, les métadonnées sont échappées en YAML.

RECHERCHE
  Ctrl+W : recherche incrémentale, insensible à la casse
  Préfixe \r : regex ; \c : sensible à la casse ; les deux se combinent
  Ctrl+D / Ctrl+B : occurrence suivante / précédente, avec retour au début
  Ctrl+\ : remplacer ; choix toutes/première/section courante
  En regex, le remplacement accepte les groupes \1, \2, etc.
  Ctrl+G : atteindre ligne ; F3 : aller à un titre
  Menu Recherche > Multi-fichiers : fichiers .md/.markdown sous la racine,
  dossiers cachés et liens symboliques exclus, 1000 résultats maximum.

ARBORESCENCE
  F9 : afficher/masquer ; Tab : basculer le focus
  Haut/Bas : sélection ; Droite/Entrée : déplier/replier un dossier
  Gauche : replier ou changer la racine vers le parent
  Entrée sur fichier : ouvrir sans perdre les autres buffers
  n : nouveau fichier ; m : nouveau dossier ; r : renommer
  d : supprimer après confirmation (dossier vide uniquement)
  Fermer un buffer avant de supprimer son fichier.
  f : filtre regex ; filtre vide : annuler ; s : tri
  . : afficher/masquer les fichiers cachés
  Seuls dossiers, .md, .markdown et .txt sont proposés.
  Les répertoires symboliques ne sont pas suivis pour éviter les cycles.

OUTILS
  Alt+L : choisir langue ou auto ; Alt+D : activer/désactiver complétion
  La détection automatique est heuristique : forcer la langue si nécessaire.
  Popup dès 3 lettres latines, 2 caractères JA/KO ou 1 caractère ZH.
  ↑/↓ ou Shift+Tab : choisir ; Tab : valider.
  JA/ZH : complétion aussi dans les phrases sans espaces.
  FR/EN : suggestions des deux langues si le préfixe latin est ambigu.
  Pour saisir les caractères CJK, utiliser la méthode de saisie du système.
  Gunterdown ne convertit pas le romaji ou le pinyin.
  Échap : fermer ; Entrée garde son rôle de nouvelle ligne.
  225615 entrées FR/EN/JA/ZH/KO issues de FrequencyWords / OpenSubtitles 2018.
  Dictionnaires adaptés sous CC BY-SA 4.0 ; provenance et licence embarquées.
  Correction FR/EN marquée ↺ : faute simple, accent, inversion de lettres.
  Exemple : bonjoru → bonjour. Aucune modification sans validation avec Tab.
  JA/ZH/KO : complétion par préfixe ; aucune correction grammaticale.
  Données de sous-titres : noms, formes familières et erreurs possibles.
  Aucun texte envoyé sur le réseau ; les dictionnaires sont embarqués.
  Au-delà de 200000 caractères, la complétion est suspendue ; Alt+D permet
  de la réactiver (éventuellement deux appuis si elle était active).
  Alt+Z : mode focus ; Alt+W : retour visuel ; Alt+# : numéros de ligne
  F6 : régénérer un aperçu HTML temporaire, à ouvrir dans un navigateur
  Ctrl+E : exporter HTML (interne), EPUB (pandoc), PDF (pandoc + xelatex)
  Les fichiers d'aperçu sont supprimés à la fermeture de l'application.
  Le convertisseur HTML interne gère titres/listes/emphases/liens/code,
  mais pas les tableaux GFM ni l'ensemble des extensions Markdown.
  F8 : liste des mots inconnus via aspell (fr/en)
  Ctrl+P : impression du texte via lpr, après confirmation
  Menu Fichier > Importer : txt ; org/rst via pandoc
  Alt+U : langue de l'interface ; choix sauvegardé immédiatement.
  Interface et manuel FR/EN/JA/ZH/KO, indépendants de la complétion.
  Alt+Y ou Outils > Thèmes : aperçu immédiat des 7 palettes.
  ↑/↓ : prévisualiser ; Entrée : appliquer et sauvegarder ; Échap : annuler.
  dark, light, solarized, nord, dracula, ocean, contrast.
  --theme NOM : choisir au lancement ; palettes adaptées à 8/16/256 couleurs.
  Thèmes personnels : GUNTERDOWN_HOME/themes/nom.json (indices 0 à 255).
  Menu Outils > Préférences : thèmes, langue de l'interface
  Menu Outils > Changer dossier : modifier la racine de l'arbre

CONFIGURATION ET RÉCUPÉRATION
  ~/.config/gunterdown/config.json ; GUNTERDOWN_HOME pour un autre répertoire
  keymap.json : par exemple {"save":"Alt+1"} ; conflits rejetés
  GUNTERDOWN_DICT_PATH : répertoire de lexiques *.json.gz
  GUNTERDOWN_LANG : langue initiale ; --lang prioritaire ; Alt+L pour changer
  GUNTERDOWN_NO_COLOR=1 : monochrome
  editor.auto_save_interval : secondes, 0 pour désactiver (par défaut)
  template.auto_insert : ask, always, never ; template.path : template
  Les fichiers de configuration, diagnostics, crash.log et recover/ sont
  tous conservés sous GUNTERDOWN_HOME. Le journal ne contient pas le document.
  Checkpoints toutes les 30 secondes et sur exception interceptée.
  Restaurer : rouvrir le même fichier et accepter la proposition.
  Sauvegarde/abandon explicite supprime la copie ; purge après 30 jours.

LIMITES
  Python 3.9+, UTF-8, Unix/macOS/BSD/WSL, curses nécessaire.
  Messages techniques des outils externes conservés dans leur langue d’origine.
  Pas de split, onglets visuels, sélection rectangulaire, synchronisation
  du presse-papiers système ou surveillance automatique d'aperçu.
  Les déplacements opèrent par point de code, pas par cluster de graphèmes.
  En cas de problème : gunterdown --diagnostics et consulter README.md.
