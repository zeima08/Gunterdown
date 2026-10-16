# Contribuer

Les sources sont dans `src/gunterdown`, les données installables dans
`src/gunterdown/data`, et les tests dans `tests`.

```sh
make lint
make test
make build
```

Ces commandes fonctionnent avec la bibliothèque standard Python uniquement.
Les tests sont aussi compatibles avec pytest ; les tests curses utilisent
`pty`, `select`, `subprocess` et un répertoire temporaire isolé pour GUNTERDOWN_HOME.
La CI teste Linux/macOS et Python 3.9/3.12/3.14. Elle construit le wheel puis
vérifie l'installation et le point d'entrée dans un venv propre.

Le contrôle `make lint` porte sur la syntaxe Python 3.9, les raccourcis et
l'intégrité des données. Les outils de style facultatifs s'installent avec
`pip install -e '.[dev]'` ; `make format` applique Black et isort.
La couverture n'est pas actuellement mesurée ni imposée en CI.

Import de dictionnaires : préparer une liste JSON avec des entrées
`{"word":"bonjour","freq":100,"pos":["interj"]}`, puis :

```sh
python3 scripts/import-dict.py fr source.json --license provenance.txt --output /chemin/dicts
GUNTERDOWN_DICT_PATH=/chemin/dicts ./gunterdown
```

La notice doit préciser la provenance, l'attribution et la licence du corpus.
Le script valide les entrées et produit gzip, notice et SHA256SUMS. Il ne
récupère aucun corpus en ligne. Les dictionnaires livrés se régénèrent avec
`python3 scripts/update-dicts.py`, depuis une révision figée de FrequencyWords.
`--source-dir DOSSIER` permet une conversion hors ligne des fichiers bruts.
Les ajouts de vocabulaire originaux sont dans `SUPPLEMENT.json`. Préserver
CC-BY-SA-4.0.txt, SOURCES.json et les notices par langue lors de la distribution.
`seed-dicts.py` est l'ancien générateur de démonstration et n'est plus utilisé
pour construire les distributions.

Les paquets Debian sont construits avec `make build-deb`. Les versions AUR,
Homebrew et la publication automatique sont différées : elles nécessitent
une version publiée, ses sommes de contrôle et une validation sur les
plateformes concernées. Aucune commande ne publie automatiquement.
