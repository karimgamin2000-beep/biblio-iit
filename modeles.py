"""Modèles de données pour BiblioIIT."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Livre:
    """Représente un livre du catalogue de la bibliothèque."""

    code: str
    titre: str
    auteur: str
    annee: int
    disponible: bool = True


@dataclass(frozen=True)
class Emprunt:
    """Représente un emprunt effectué par un étudiant."""

    id: int | None
    code_livre: str
    matricule_etudiant: str
    date_emprunt: date
    date_retour_prevue: date
    date_retour_reelle: date | None = None


@dataclass(frozen=True)
class RetardInfo:
    """Détail d'un emprunt en retard."""

    code_livre: str
    titre_livre: str
    matricule_etudiant: str
    date_retour_prevue: date
    jours_retard: int
