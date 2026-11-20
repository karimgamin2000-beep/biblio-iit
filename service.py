"""Service applicatif orchestrant les règles métier et la base SQLite."""

from datetime import date

from depot_sqlite import DepotSQLite
from modeles import Emprunt, Livre, RetardInfo
from regles import (
    MAX_EMPRUNTS_ACTIFS,
    calculer_date_retour,
    calculer_jours_retard,
    valider_code_livre,
    valider_matricule,
)


class ErreurBiblio(Exception):
    """Erreur métier levée lors d'une opération invalide."""


class BiblioService:
    """Expose les cas d'usage de l'application console BiblioIIT."""

    def __init__(self, depot: DepotSQLite) -> None:
        self.depot = depot

    def rechercher_livres(self, mot_cle: str) -> list[Livre]:
        return self.depot.rechercher_livres(mot_cle)

    def emprunter(self, code_livre: str, matricule: str, date_emprunt: date | None = None) -> Emprunt:
        code = valider_code_livre(code_livre)
        mat = valider_matricule(matricule)
        aujourd_hui = date_emprunt or date.today()

        livre = self.depot.obtenir_livre(code)
        if livre is None:
            raise ErreurBiblio(f"Livre introuvable avec le code « {code} ».")

        if not livre.disponible:
            raise ErreurBiblio(f"Le livre « {livre.titre} » est déjà emprunté")

        if self.depot.compter_emprunts_actifs(mat) >= MAX_EMPRUNTS_ACTIFS:
            raise ErreurBiblio(
                f"L'étudiant {mat} a déjà atteint la limite de {MAX_EMPRUNTS_ACTIFS} emprunts actifs."
            )

        date_retour = calculer_date_retour(aujourd_hui)
        emprunt = Emprunt(
            id=None,
            code_livre=code,
            matricule_etudiant=mat,
            date_emprunt=aujourd_hui,
            date_retour_prevue=date_retour,
        )
        emprunt_id = self.depot.enregistrer_emprunt(emprunt)
        return Emprunt(
            id=emprunt_id,
            code_livre=emprunt.code_livre,
            matricule_etudiant=emprunt.matricule_etudiant,
            date_emprunt=emprunt.date_emprunt,
            date_retour_prevue=emprunt.date_retour_prevue,
        )

    def rendre(self, code_livre: str, date_retour: date | None = None) -> Livre:
        code = valider_code_livre(code_livre)
        aujourd_hui = date_retour or date.today()

        livre = self.depot.obtenir_livre(code)
        if livre is None:
            raise ErreurBiblio(f"Livre introuvable avec le code « {code} ».")

        emprunt = self.depot.obtenir_emprunt_actif(code)
        if emprunt is None or emprunt.id is None:
            raise ErreurBiblio(f"Le livre « {livre.titre} » n'est pas actuellement emprunté.")

        self.depot.cloturer_emprunt(emprunt.id, aujourd_hui)
        return livre

    def lister_retards(self, date_reference: date | None = None) -> list[RetardInfo]:
        aujourd_hui = date_reference or date.today()
        retards: list[RetardInfo] = []
        for emprunt, titre in self.depot.lister_emprunts_ouverts_avec_livres():
            jours = calculer_jours_retard(emprunt.date_retour_prevue, aujourd_hui)
            if jours > 0:
                retards.append(
                    RetardInfo(
                        code_livre=emprunt.code_livre,
                        titre_livre=titre,
                        matricule_etudiant=emprunt.matricule_etudiant,
                        date_retour_prevue=emprunt.date_retour_prevue,
                        jours_retard=jours,
                    )
                )
        return retards
