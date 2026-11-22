# BiblioIIT — Gestion de bibliothèque (TUI & Console Python)

Application console avec interface **TUI (Textual)** et persistance **SQLite** pour la gestion d'une bibliothèque universitaire (projet académique IIT).

---

## Fonctionnalités

- **Interface TUI moderne (`textual`)** :
  - **Barre de statistiques en direct** : Total des livres, Disponibles, Empruntés, Retards.
  - **Onglet Catalogue & Recherche** : filtrage instantané par titre, auteur ou code, tableau interactif (`DataTable`), emprunt via fenêtre modale ou retour en un clic.
  - **Onglet Emprunts & Retards** : suivi des emprunts actifs, dates de retour prévues et calcul automatique des jours de retard.
  - **Onglet Action rapide** : formulaire direct d'emprunt et de retour par code livre et matricule.
  - **Raccourcis clavier** : `q` (Quitter), `r` (Rafraîchir), `f` (Rechercher).
- **Mode CLI classique conservé** : disponible via `python console.py --cli`.
- **Règles métier** : durée d'emprunt de 14 jours, blocage des doubles emprunts, limite de 3 emprunts actifs par étudiant.

---

## Architecture modulaire

| Module | Rôle |
| --- | --- |
| `tui.py` | Interface console TUI (`BiblioTUI`, `EmpruntModal`) avec Textual |
| `console.py` | Point d'entrée (lance le TUI par défaut, ou le menu texte avec `--cli`) |
| `modeles.py` | Dataclasses immuables `Livre`, `Emprunt`, `RetardInfo` |
| `regles.py` | Règles métier (durée de 14 jours, retards, validation des entrées) |
| `depot_sqlite.py` | Couche d'accès aux données SQLite et catalogue initial |
| `service.py` | Orchestration applicative (`BiblioService`, `ErreurBiblio`) |
| `tests/` | Tests unitaires, d'intégration et TUI (`test_regles.py`, `test_service.py`, `test_tui.py`) |

---

## Installation et lancement

```bash
git clone https://github.com/karimgamin2000-beep/biblio-iit.git
cd biblio-iit
python -m venv .venv
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
python console.py
```

Pour lancer le menu texte classique sans TUI :

```bash
python console.py --cli
```

---

## Lancer les tests

```bash
pytest -v
# ou :
python -m unittest discover -s tests -v
```

---

## Auteur

**KONATE ABDOUL KARIM** — Étudiant en Computer Science (IIT, Côte d'Ivoire)
- GitHub : [github.com/karimgamin2000-beep](https://github.com/karimgamin2000-beep)
- LinkedIn : [in/abdoul-karim-konate-15635b3b0](https://www.linkedin.com/in/abdoul-karim-konate-15635b3b0)
