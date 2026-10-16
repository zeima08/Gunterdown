# CONTRIBUER — Guide du contributeur Gunterdown

> Procédure pour contribuer au projet : environnement de développement,
> style de code, tests, packaging (PyPI, .deb, AUR, Homebrew) et
> licences des dictionnaires CJK. Public visé : développeurs et
> mainteneurs.

---

## 1. Environnement de développement

### 1.1 Pré-requis

- Python 3.9 minimum (3.11 recommandé).
- `git` pour le clonage et les pull requests.
- `make` pour automatiser les tâches courantes.
- `pandoc` (optionnel) pour tester l'aperçu live et l'export.
- `aspell` avec les paquets de langue FR/EN pour tester la
  vérification orthographique (`aspell-fr`, `aspell-en`).
- `pytest` (dépendance de développement) pour les tests unitaires.

### 1.2 Cloner et installer en mode dev

```bash
git clone https://github.com/zeima/gunterdown.git
cd gunterdown
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

L'option `.[dev]` installe les dépendances de développement listées
dans `pyproject.toml` :

- `pytest` ≥ 7.0 — tests unitaires
- `pytest-cov` — couverture
- `pexpect` — tests curses dans un pseudo-terminal
- `flake8` — style de code
- `black` — formatage automatique
- `mypy` — vérification statique des types
- `build` — construction des distributions
- `twine` — upload PyPI

### 1.3 Lancer Gunterdown depuis le code source

```bash
python3 bin/gunterdown.py --help
python3 bin/gunterdown.py article.md
```

Le script `bin/gunterdown` est un lanceur shell POSIX qui définit les
variables d'environnement nécessaires (`PYTHONPATH`,
`GUNTERDOWN_HOME=data`) puis appelle `python3 bin/gunterdown.py "$@"`. Utilisez
ce lanceur pendant le développement pour reproduire l'environnement
de production :

```bash
./bin/gunterdown article.md
```

### 1.4 Structure des répertoires (rappel)

Voir `README.md` § 4. Tous les fichiers sources Python vivent dans
`src/gunterdown/`. Les données (dictionnaires, templates) sont dans
`data/`. Les tests dans `tests/`. Les scripts de build dans
`scripts/`. Le lanceur dans `bin/`.

---

## 2. Style de code

### 2.1 Formatage

- **Indentation :** 4 espaces, jamais de tabulations.
- **Longueur de ligne :** 88 caractères maximum (config `black` par
  défaut).
- **Formatage automatique :** `black src/ tests/` avant chaque commit.
- **Tri des imports :** `isort src/ tests/` (config : `profile =
  "black"`).
- **Vérification statique :** `mypy src/` avec config stricte dans
  `pyproject.toml`.

### 2.2 Conventions de nommage

- Modules : `snake_case.py`.
- Classes : `PascalCase`.
- Fonctions et variables : `snake_case`.
- Constantes : `UPPER_SNAKE_CASE`.
- Méthodes privées : préfixe `_`.
- Variables non utilisées intentionnellement : préfixe `_`.

### 2.3 Type hints

Toutes les fonctions publiques doivent avoir des annotations de type
complètes (paramètres + retour). Les méthodes privées sont
recommandées de l'être aussi. Le `Any` est proscrit sauf cas
documenté.

### 2.4 Docstrings

Format **Google style** pour toutes les fonctions et classes
publiques :

```python
def detect_lang(paragraph: str, fallback: str = "fr") -> str:
    """Détecte la langue dominante d'un paragraphe.

    Args:
        paragraph: texte à analyser (paragraphe courant).
        fallback: langue à renvoyer si la détection échoue.

    Returns:
        Code ISO 639-1 de la langue détectée ("fr", "en", "ja",
        "zh" ou "ko").
    """
    ...
```

### 2.5 Linting automatique

Avant chaque commit, exécutez :

```bash
make lint    # flake8 + mypy + isort --check
make format  # black + isort (modifie les fichiers)
make test    # pytest + couverture
```

Le `Makefile` à la racine du dépôt contient toutes les cibles
courantes. La CI GitHub Actions refuse toute PR qui ne passe pas
`make lint && make test`.

---

## 3. Tests

### 3.1 Tests unitaires

Tous les modules logiques (parser, autocomplétion, détection de
langue, template, slug) doivent avoir une couverture minimale de 80 %.
Les tests se lancent avec :

```bash
make test
# ou directement
pytest tests/ -v --cov=src/gunterdown --cov-report=term-missing
```

### 3.2 Tests curses

Le rendu curses est testé via `pexpect` dans un pseudo-terminal. Le
pattern classique :

```python
import pexpect
def test_open_file(tmp_path):
    f = tmp_path / "article.md"
    f.write_text("# Test\n")
    child = pexpect.spawn("python3 bin/gunterdown.py str(f)")
    child.expect("Test")
    child.sendcontrol("x")
    child.expect(pexpect.EOF)
```

Ces tests sont plus lents et marqués avec `@pytest.mark.slow`. Ils ne
tournent pas par défaut : `pytest -m "not slow"` pour les exclure,
`pytest -m slow` pour les lancer uniquement.

### 3.3 Tests de non-régression

Chaque bug fixé doit être accompagné d'un test de non-régression dans
`tests/regression/`. Le test reproduit le bug initial et vérifie
qu'il ne réapparaît pas. Le format du nom de fichier est
`test_issue_NNNN.py` où `NNNN` est le numéro du ticket GitHub.

### 3.4 Couverture

La couverture est mesurée avec `pytest-cov`. Le seuil minimum est
configuré dans `pyproject.toml` :

```toml
[tool.coverage.run]
source = ["src/gunterdown"]
omit = ["*/tests/*"]

[tool.coverage.report]
fail_under = 80
```

Une PR qui fait baisser la couverture sous 80 % est refusée par la CI,
sauf si la baisse est justifiée dans la description de la PR.

---

## 4. Workflow de contribution

### 4.1 Ouvrir une PR

1. Forkez le dépôt sur GitHub.
2. Créez une branche : `git checkout -b feature/mon-nom-feature`.
3. Codez, testez, documentez.
4. `make lint && make test` doivent passer.
5. Commitez avec des messages au format
   `type(scope): description` (Conventional Commits). Exemples :
   `feat(autocomplete): add Korean prefix index`,
   `fix(treeview): crash on hidden files`,
   `docs(readme): clarify install on macOS`.
6. Poussez et ouvrez une PR vers `main`.

### 4.2 Revue

Les PR sont revues par au moins un mainteneur. Les critères :

- Code lisible, sans magie inutile.
- Tests présents et passent.
- Couverture maintenue ou augmentée.
- Documentation à jour (README, USAGE, AIDE si concerné).
- Messages de commit clairs.
- Pas de dépendance externe nouvelle sans justification solide.

### 4.3 Branches et releases

- `main` — branche stable, jamais de commit direct.
- `develop` — intégration des features pour la prochaine release.
- `feature/*` — branches de feature.
- `fix/*` — branches de bug fix.
- `release/x.y.z` — préparation d'une release.

Les releases suivent le versionnage sémantique. Chaque release est
taguée `vx.y.z` et accompagnée d'une entry dans `CHANGES.md`.

---

## 5. Packaging

`Gunterdown` est distribué via plusieurs canaux. Chacun a sa procédure de
build, automatisée dans `scripts/`.

### 5.1 PyPI (wheel + sdist)

```bash
make build-pypi    # crée dist/gunterdown-x.y.z-py3-none-any.whl et .tar.gz
make upload-pypi   # twine upload dist/*  (nécessite .pypirc)
```

Le fichier `pyproject.toml` déclare la configuration `setuptools` :

```toml
[project]
name = "gunterdown"
version = "0.1.0"
description = "Éditeur Markdown TUI multilingue en Python pur (curses)"
authors = [{name = "Zeima"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "pexpect", "flake8",
       "black", "isort", "mypy", "build", "twine"]

[project.scripts]
gunterdown = "gunterdown.tui:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
gunterdown = ["data/dicts/*.gz", "data/templates/*.md"]
```

### 5.2 Paquet Debian (.deb)

```bash
make build-deb    # crée dist/gunterdown_x.y.z-1_all.deb
```

Le script `scripts/build-deb.sh` :

1. Génère le wheel via `pip wheel`.
2. Crée une arborescence Debian
   (`DEBIAN/control`, `DEBIAN/postinst`, `DEBIAN/prerm`).
3. Copie le wheel dans `/usr/lib/python3/dist-packages/`.
4. Crée le lanceur shell dans `/usr/bin/gunterdown`.
5. Inclut la page de manuel `gunterdown.1.gz` dans `/usr/share/man/man1/`.
6. Construit le `.deb` avec `dpkg-deb --build`.

Le fichier `control` :

```
Package: gunterdown
Version: 0.1.0-1
Architecture: all
Maintainer: Zeima <zeima@example.com>
Depends: python3 (>= 3.9), fonts-noto-cjk
Section: editors
Priority: optional
Description: Éditeur Markdown TUI multilingue en Python pur
 Gunterdown est un éditeur de texte en mode terminal dédié à la rédaction
 d'articles Markdown, avec autocomplétion FR/EN/JA/ZH/KO, panneau
 d'arborescence et template d'article pré-défini. Aucune dépendance
 Python externe.
```

### 5.3 AUR (Arch User Repository)

Le paquet AUR est géré via un `PKGBUILD` dans `dist/arch/`. La
procédure de mise à jour :

```bash
make build-aur    # génère le .src.tar.gz
# puis upload manuel sur https://aur.archlinux.org
```

Le `PKGBUILD` minimal :

```bash
# Maintainer: Zeima <zeima@example.com>
pkgname=gunterdown
pkgver=0.1.0
pkgrel=1
pkgdesc="Éditeur Markdown TUI multilingue en Python pur (curses)"
arch=('any')
url="https://github.com/zeima/gunterdown"
license=('MIT')
depends=('python>=3.9' 'fonts-noto-cjk')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python setup.py build
}

package() {
    cd "$pkgname-$pkgver"
    python setup.py install --root="$pkgdir/" --optimize=1
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
```

### 5.4 Homebrew (macOS)

Le tap Homebrew est `zeima/tap`. La formule Ruby
`dist/homebrew/gunterdown.rb` :

```ruby
class Gunterdown < Formula
  desc "Éditeur Markdown TUI multilingue en Python pur"
  homepage "https://github.com/zeima/gunterdown"
  url "https://github.com/zeima/gunterdown/archive/v0.1.0.tar.gz"
  sha256 "..."
  license "MIT"
  depends_on "python@3.11"

  def install
    system "python3", "-m", "pip", "install", "--prefix=#{prefix}", "."
  end

  test do
    system "#{bin}/gunterdown", "--version"
  end
end
```

Publication via `brew tap zeima/tap` puis `brew install gunterdown`.

### 5.5 Man page

La page de manuel `man/gunterdown.1` est générée à partir d'un source
roff et compressée en `gunterdown.1.gz` à l'installation. Format roff
classique, voir `man/gunterdown.1.md` pour le source en Markdown
(généré avec `pandoc -s -t man man/gunterdown.1.md -o man/gunterdown.1`).

### 5.6 Vérification des paquets

Avant chaque release, le script `scripts/verify-packages.sh`
vérifie que :

- Le wheel s'installe dans un venv propre et que `gunterdown --version`
  fonctionne.
- Le `.deb` s'installe dans un conteneur Debian et que `gunterdown --version`
  fonctionne.
- Le `PKGBUILD` build dans un chroot Arch Linux et que
  `gunterdown --version` fonctionne.
- La formule Homebrew s'installe sur un runner macOS et que
  `gunterdown --version` fonctionne.

Cette vérification est automatisée dans GitHub Actions
(`.github/workflows/release.yml`).

---

## 6. Licences des dictionnaires CJK

Les dictionnaires embarqués dans `data/dicts/` proviennent de sources
libres dont les licences doivent être préservées dans toute
redistribution. Le projet conserve un fichier `THIRD_PARTY_LICENSES`
à la racine du dépôt qui reproduit intégralement chaque licence.

### 6.1 Dictionnaire français — Wiktextract (fr.wiktionary.org)

- **Source :** Wiktextract (https://wiktextract.toolforge.org/)
- **Licence :** CC BY-SA 4.0
- **Mention obligatoire :** « Contient des données issues du
  Wiktionnaire français, distribué sous licence CC BY-SA 4.0. »
- **URL de la licence :** https://creativecommons.org/licenses/by-sa/4.0/

### 6.2 Dictionnaire anglais — Wiktextract (en.wiktionary.org)

- **Source :** Wiktextract (https://wiktextract.toolforge.org/)
- **Licence :** CC BY-SA 4.0
- **Mention obligatoire :** « Contient des données issues du
  Wiktionnaire anglais, distribué sous licence CC BY-SA 4.0. »
- **URL de la licence :** https://creativecommons.org/licenses/by-sa/4.0/

### 6.3 Dictionnaire japonais — JMDict

- **Source :** Electronic Dictionary Research and Development Group
  (https://www.edrdg.org/jmdict/)
- **Licence :** CC BY-SA 4.0
- **Mention obligatoire :** « JMDict fichier © Electronic Dictionary
  Research and Development Group, distribué sous licence CC BY-SA
  4.0. »
- **URL de la licence :** https://creativecommons.org/licenses/by-sa/4.0/

### 6.4 Dictionnaire chinois — CC-CEDICT

- **Source :** MDBG (https://www.mdbg.net/chinese/dictionary?page=cc-cedict)
- **Licence :** CC BY-SA 4.0
- **Mention obligatoire :** « Contient des données issues de
  CC-CEDICT, distribué sous licence CC BY-SA 4.0. »
- **URL de la licence :** https://creativecommons.org/licenses/by-sa/4.0/

### 6.5 Dictionnaire coréen — KAIST Word Dictionary

- **Source :** KAIST Word Dictionary (https://wordrow.co.kr/)
- **Licence :** CC BY-SA 4.0
- **Mention obligatoire :** « Contient des données issues du KAIST
  Word Dictionary, distribué sous licence CC BY-SA 4.0. »
- **URL de la licence :** https://creativecommons.org/licenses/by-sa/4.0/

### 6.6 Mise à jour des dictionnaires

La procédure de mise à jour est automatisée dans
`scripts/update-dicts.sh`. Le script :

1. Télécharge les sources brutes depuis les URLs officielles.
2. Les convertit au format JSON attendu par `Gunterdown`
   (`{"word": "...", "freq": 1234, "pos": [...]}`).
3. Les trie par mot.
4. Les compresse en `.json.gz` dans `data/dicts/`.
5. Met à jour `THIRD_PARTY_LICENSES` si une licence a changé.
6. Met à jour le checksum SHA-256 de chaque dictionnaire dans
   `data/dicts/SHA256SUMS`.

Cette procédure est lancée avant chaque release. Les nouvelles
versions des dictionnaires sont mentionnées dans `CHANGES.md`.

### 6.7 Polices Noto CJK

L'affichage des caractères CJK n'est pas lié aux dictionnaires : il
dépend des polices installées sur le système de l'utilisateur. Le
paquet `fonts-noto-cjk` (Debian/Ubuntu) ou équivalent est recommandé
dans les dépendances du paquet Debian. Voir `INSTALL.md` § 1.2 pour
le détail.

Les polices Noto CJK sont distribuées sous licence **SIL Open Font
License 1.1** (https://scripts.sil.org/OFL). Cette licence autorise
l'usage, la copie, la modification et la redistribution gratuite, à
condition de préserver la mention de copyright. Le projet `Gunterdown`
n'embarque pas les polices (elles sont déjà installées sur la
plupart des systèmes) mais documente leur nécessité.

---

## 7. Code of Conduct

Le projet `Gunterdown` adhère au **Contributor Covenant 2.1**
(https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
Toute interaction dans le dépôt (issues, PR, discussions, commits)
doit respecter ce code. Les violations peuvent être signalées
confidentiellement à l'auteur via GitHub.

En résumé :

- Soyez accueillant et inclusif.
- Respectez les viewpoints et expériences différents.
- Acceptez les critiques constructives avec grâce.
- Pas de harcèlement, de troll ou de comportement toxique.

---

## 8. Crédits contributeurs

La liste complète des contributeurs est disponible dans le fichier
`AUTHORS` à la racine du dépôt. Pour y figurer, ajoutez votre nom
(pseudo ou nom réel) à votre première PR, dans la section
correspondante du fichier.

---

## English summary

Contributors should fork the repository, create a feature branch,
develop with `black`, `isort`, `flake8`, `mypy` and `pytest` (80 %
minimum coverage), and open a PR to `main` following Conventional
Commits. The project provides Makefile targets for lint, format,
test, build (PyPI wheel, `.deb`, AUR `PKGBUILD`, Homebrew formula)
and dictionary updates. All CJK dictionaries are CC BY-SA 4.0 and
their notices are reproduced in `THIRD_PARTY_LICENSES`; an
`scripts/update-dicts.sh` script keeps them current and updates
`SHA256SUMS`. The Noto CJK fonts (SIL OFL 1.1) are recommended as a
runtime dependency. The project adheres to the Contributor Covenant
2.1 code of conduct. Authors are listed in `AUTHORS`.
