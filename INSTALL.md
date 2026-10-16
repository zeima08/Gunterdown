# Installation

Les commandes maintenues et les prérequis sont dans [README.md](README.md).

Sans installation : `./gunterdown article.md` (Python 3.9+, curses, UTF-8).
Installation isolée : `./install.sh [préfixe]` (défaut `~/.local`).
Construction hors ligne : `make build` ; installation wheel :
`python3 -m pip install dist/gunterdown-0.7.0-py3-none-any.whl`.

Pandoc, XeLaTeX et Aspell sont facultatifs et ne sont pas installés par les
scripts. Les cinq dictionnaires FrequencyWords sont embarqués pour fonctionner hors ligne.
