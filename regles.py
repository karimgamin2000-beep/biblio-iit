"""Règles métier de gestion des emprunts et retards pour BiblioIIT."""

from datetime import date, timedelta

DUREE_EMPRUNT_JOURS = 14
MAX_EMPRUNTS_ACTIFS = 3


def calculer_date_retour(date_emprunt: date, duree_jours: int = DUREE_EMPRUNT_JOURS) -> date:
    """Calcule la date de retour prévue à partir de la date d'emprunt."""
    if duree_jours <= 0:
        raise ValueError("La durée d'emprunt doit être strictement positive.")
    return date_emprunt + timedelta(days=duree_jours)


def calculer_jours_retard(date_retour_prevue: date, date_reference: date) -> int:
    """Retourne le nombre de jours de retard (0 si à l'heure ou en avance)."""
    delta = (date_reference - date_retour_prevue).days
    return max(0, delta)


def est_en_retard(date_retour_prevue: date, date_reference: date) -> bool:
    """Indique si un emprunt non rendu est en retard à la date de référence."""
    return calculer_jours_retard(date_retour_prevue, date_reference) > 0


def valider_matricule(matricule: str) -> str:
    """Normalise et valide le format d'un matricule étudiant (ex: E2026-001)."""
    nettoye = matricule.strip().upper()
    if len(nettoye) < 3:
        raise ValueError("Matricule invalide : trop court.")
    return nettoye


def valider_code_livre(code: str) -> str:
    """Normalise et valide le code d'un livre (ex: L002)."""
    nettoye = code.strip().upper()
    if not nettoye:
        raise ValueError("Le code du livre ne peut pas être vide.")
    return nettoye
