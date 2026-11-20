# BiblioIIT — Gestion de bibliothèque en Python

Application console modulaire de gestion de bibliothèque universitaire développée en **Python** avec persistance **SQLite** (projet académique IIT — Séance 4).

Zéro dépendance externe requise : tout repose sur la bibliothèque standard Python (`sqlite3`, `dataclasses`, `datetime`, `unittest`).

---

## Fonctionnalités

- **Recherche de livres** par mot-clé (titre, auteur ou code) avec statut en temps réel (`Disponible` / `Emprunté`).
- **Emprunt encadré** : validation du code livre et du matricule étudiant, blocage des doubles emprunts, limite de 3 emprunts actifs par étudiant, calcul automatique de la date de retour à **14 jours**.
- **Retour de livres** : clôture de l'emprunt actif et remise en disponibilité immédiate.
- **Suivi des retards** : liste des emprunts dépassés avec calcul exact du nombre de jours de retard.
- **Catalogue de démonstration** : initialisé automatiquement au premier lancement (`biblio.db`).

---

## Architecture modulaire

| Module | Rôle |
| --- | --- |
| `modeles.py` | Dataclasses immuables `Livre`, `Emprunt`, `RetardInfo` |
| `regles.py` | Règles métier (durée de 14 jours, retards, validation des entrées) |
| `depot_sqlite.py` | Couche d'accès aux données SQLite et catalogue initial |
| `service.py` | Orchestration applicative (`BiblioService`, `ErreurBiblio`) |
| `console.py` | Interface interactive en ligne de commande |
| `tests/` | Suite de tests unitaires et d'intégration (`test_regles.py`, `test_service.py`) |

---

## Démarrage rapide

### Prérequis
- Python 3.10 ou supérieur

### Lancer l'application

```bash
git clone https://github.com/karimgamin2000-beep/biblio-iit.git
cd biblio-iit
python console.py
```

### Exemple d'utilisation

```text
=== BiblioIIT ===
1. Rechercher un livre   2. Emprunter
3. Rendre               4. Retards   0. Quitter
Votre choix : 1
Mot-clé : Kourouma
  L002  Les Soleils des indépendances — Ahmadou Kourouma (1968) [Disponible]
  L004  Allah n'est pas obligé — Ahmadou Kourouma (2000) [Disponible]
```

---

## Lancer les tests

```bash
python -m unittest discover -s tests -v
```

---

## Auteur

**KONATE ABDOUL KARIM** — Étudiant en Computer Science (IIT, Côte d'Ivoire)
- GitHub : [github.com/karimgamin2000-beep](https://github.com/karimgamin2000-beep)
- LinkedIn : [in/abdoul-karim-konate-15635b3b0](https://www.linkedin.com/in/abdoul-karim-konate-15635b3b0)
