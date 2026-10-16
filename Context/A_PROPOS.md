# À PROPOS — Gunterdown

> Section « À propos » accessible depuis le TUI via `F12` ou le menu
> `Aide > À propos`. Présente l'auteur, les motivations, la licence, les
> crédits et l'historique du projet.

---

## 1. L'auteur

**Gunterdown** est conçu et développé par **Zeima**.

Zeima est un développeur passionné par les outils en mode texte, la
philosophie Unix et les éditeurs minimalistes. Le projet `Gunterdown` est né
de l'envie de combiner la simplicité d'usage de `nano` (raccourcis
visibles, prise en main immédiate) avec la richesse de `mcedit` (menus,
arborescence) tout en se concentrant sur un cas d'usage précis : la
rédaction d'articles Markdown structurés, multilingues et sans fioritures.

Le projet est open source et toute contribution est bienvenue. Vous
pouvez contacter l'auteur via le dépôt GitHub du projet
(`https://github.com/zeima/gunterdown`) pour :

- Signaler un bug ou proposer une amélioration (issues).
- Soumettre une pull request (voir `CONTRIBUER.md`).
- Discuter de la roadmap ou proposer un nouveau cas d'usage.
- Demander l'ajout d'une langue d'autocomplétion.

---

## 2. Motivations

Les éditeurs de texte en mode terminal sont nombreux : `nano`, `vi`,
`vim`, `ne`, `mcedit`, `micro`, `helix`, `kakoune`. Chacun a ses forces
et son public. `Gunterdown` ne cherche pas à les remplacer tous ; il se
positionne sur un créneau précis : la **rédaction d'articles Markdown
multilingues** dans un terminal, avec un template d'article pré-défini
et une autocomplétion qui suit la langue active du paragraphe en cours.

Trois frustrations récurrentes ont motivé la création de l'outil :

1. **Aucun éditeur TUI léger n'offre de template d'article prêt à
   l'emploi.** La plupart partent d'un buffer vide et obligent à
   réinventer la structure YAML/TOC à chaque fichier.
2. **L'autocomplétion multilingue est inexistante ou réduite à la
   langue du système.** Or un auteur technique écrit souvent en
   français, anglais et parfois japonais/chinois/coréen dans le même
   document. Aucun outil TUI existant ne gère ça bien.
3. **Les éditeurs TUI modernes (Helix, Kakoune) ont une courbe
   d'apprentissage abrupte.** `nano` est accessible mais limité ;
   `mcedit` est accessible mais vieux et lié à Midnight Commander.
   Il manquait un éditeur sur cette niche : moderne, accessible, avec
   des fonctionnalités rédaction orientées.

`Gunterdown` tente de combler ce manque. Le pari est que le ciblage d'un cas
d'usage précis (article Markdown multilingue) justifie un outil
dédié plutôt qu'une extension d'un éditeur existant.

---

## 3. Philosophie technique

Trois principes guident toutes les décisions techniques :

- **Zéro dépendance externe.** Tout repose sur la bibliothèque
  standard Python. Le paquet s'installe sans `pip install` et tourne
  sur n'importe quelle machine Python 3.9+ avec un terminal. Cette
  contrainte ralentit le développement mais garantit la portabilité.
- **Unix way.** L'outil fait une chose et le fait bien : éditer du
  Markdown. L'aperçu live est délégué à `pandoc` quand disponible,
  l'export EPUB/PDF aussi. L'éditeur ne réinvente pas un moteur de
  rendu HTML complet.
- **Lisibilité du code source.** Le projet est conçu pour être lu et
  compris par des contributeurs débutants. Pas de magie, pas de
  métaprogrammation, pas de framework. Du Python simple et direct.

---

## 4. Licence

Le code source de `Gunterdown` est distribué sous licence **MIT**, dont le
texte intégral est disponible dans le fichier `LICENSE` à la racine du
dépôt. Cette licence autorise la réutilisation, la modification, la
redistribution et l'usage commercial du code, à condition de préserver
la mention de copyright originale.

Les **dictionnaires d'autocomplétion** embarqués ne sont pas sous
licence MIT ; ils conservent leurs licences respectives :

| Dictionnaire | Source                              | Licence            |
|--------------|-------------------------------------|---------------------|
| `fr.json.gz` | Wiktextract (fr.wiktionary.org)    | CC BY-SA 4.0       |
| `en.json.gz` | Wiktextract (en.wiktionary.org)    | CC BY-SA 4.0       |
| `ja.json.gz` | JMDict (edrdg.org)                  | CC BY-SA 4.0       |
| `zh.json.gz` | CC-CEDICT                           | CC BY-SA 4.0       |
| `ko.json.gz` | KAIST Word Dictionary               | CC BY-SA 4.0       |

Le détail de chaque licence et les mentions de copyright à reproduire
dans toute redistribution sont dans `CONTRIBUER.md` § 6.

---

## 5. Crédits

`Gunterdown` n'aurait pas été possible sans les ressources libres suivantes :

- **Wiktionnaire français et anglais** (éditions Wiktextract) — base
  des dictionnaires d'autocomplétion latins.
- **JMDict** (Electronic Dictionary Research and Development Group,
  Japon) — base du dictionnaire japonais.
- **CC-CEDICT** (maintenu par MDBG Ltd, Hong Kong) — base du
  dictionnaire chinois-anglais.
- **KAIST Word Dictionary** (Korea Advanced Institute of Science and
  Technology) — base du dictionnaire coréen.
- **Pandoc** (John MacFarlane) — utilisé pour l'aperçu live et
  l'export HTML/EPUB/PDF si disponible sur le système.
- **NCurses** (Free Software Foundation) — base de l'interface TUI.
- **Python Software Foundation** — pour le langage et la bibliothèque
  standard.
- Les éditeurs `nano` (Chris Allegretta et contributeurs) et `mcedit`
  (les équipes Midnight Commander) qui ont inspiré l'ergonomie
  générale de `Gunterdown`.

Merci également à toutes les personnes qui ont testé les versions
préliminaires et fait remonter leurs remarques.

---

## 6. Historique

| Version | Date       | Jalon principal                                        |
|---------|------------|--------------------------------------------------------|
| 0.1.0   | 2026       | Présent document (spécification + cahier des charges)  |
| 0.2.0   | à venir    | Édition basique, save/exit, ouverture de fichiers       |
| 0.3.0   | à venir    | Coloration Markdown + panneau arborescence             |
| 0.4.0   | à venir    | Autocomplétion FR/EN                                    |
| 0.5.0   | à venir    | Autocomplétion JA/ZH/KO + détection hybride             |
| 0.6.0   | à venir    | Template d'article + front-matter YAML                 |
| 0.7.0   | à venir    | Aperçu live via pandoc                                 |
| 0.8.0   | à venir    | Multi-fenêtres et onglets                              |
| 1.0.0   | à venir    | Stable, paquets binaires (.deb, AUR, Homebrew)         |

L'historique complet des changements est disponible dans le fichier
`CHANGES.md` à la racine du dépôt.

---

## 7. Contact et liens

| Ressource              | URL                                                    |
|------------------------|--------------------------------------------------------|
| Dépôt principal         | `https://github.com/zeima/gunterdown`                       |
| Suivi de bugs          | `https://github.com/zeima/gunterdown/issues`                |
| Discussions             | `https://github.com/zeima/gunterdown/discussions`           |
| Page PyPI              | `https://pypi.org/project/gunterdown/` (à partir de 0.4.0) |
| Documentation en ligne  | `https://github.com/zeima/gunterdown/blob/main/README.md`   |

Pour toute question, préférez ouvrir un ticket (issue) sur GitHub
plutôt que d'écrire directement à l'auteur. Cela permet à la
communauté de bénéficier de la réponse et à l'auteur de garder une
trace publique des échanges.

---

## 8. Citation recommandée

Si vous citez `Gunterdown` dans un article ou un travail académique :

> Zeima. *Gunterdown — Éditeur Markdown pour Terminal* (logiciel libre,
> licence MIT), version X.Y.Z, 2026. URL : https://github.com/zeima/gunterdown

Remplacez `X.Y.Z` par la version que vous utilisez (visible via
`gunterdown --version`).

---

## English summary

`Gunterdown` is developed by Zeima, an open-source enthusiast focused on
minimalist terminal tools. The project was created to fill a gap in
the TUI editor landscape: a lightweight, dependency-free editor
specifically for writing multilingual Markdown articles, with a
built-in article template and per-paragraph language detection for
autocompletion (FR / EN / JA / ZH / KO). The editor is released under
the MIT license, while the bundled dictionaries retain their
upstream licenses (CC BY-SA 4.0). The project depends on
Wiktionnaire, JMDict, CC-CEDICT and KAIST dictionaries, on Pandoc
for live preview and export, and on NCurses for the terminal
interface. The author thanks the `nano` and `mcedit` projects for
their ergonomic inspiration. For bug reports, feature requests or
contributions, see `CONTRIBUER.md` and the GitHub repository.
