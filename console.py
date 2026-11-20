"""Interface console interactive pour BiblioIIT."""

from pathlib import Path

from depot_sqlite import DepotSQLite
from regles import valider_code_livre, valider_matricule
from service import BiblioService, ErreurBiblio


def afficher_menu() -> None:
    print("\n=== BiblioIIT ===")
    print("1. Rechercher un livre   2. Emprunter")
    print("3. Rendre               4. Retards   0. Quitter")


def action_rechercher(service: BiblioService) -> None:
    mot_cle = input("Mot-clé : ")
    livres = service.rechercher_livres(mot_cle)
    if not livres:
        print("Aucun livre trouvé.")
        return
    for livre in livres:
        statut = "Disponible" if livre.disponible else "Emprunté"
        print(f"  {livre.code}  {livre.titre} — {livre.auteur} ({livre.annee}) [{statut}]")


def action_emprunter(service: BiblioService) -> None:
    code = input("Code du livre : ")
    matricule = input("Matricule : ")
    try:
        valider_code_livre(code)
        valider_matricule(matricule)
        emprunt = service.emprunter(code, matricule)
        print(f"Emprunt enregistré. Retour prévu le {emprunt.date_retour_prevue.strftime('%d/%m/%Y')}.")
    except (ErreurBiblio, ValueError) as exc:
        print(f"Impossible : {exc}")


def action_rendre(service: BiblioService) -> None:
    code = input("Code du livre : ")
    try:
        livre = service.rendre(code)
        print(f"Retour enregistré pour « {livre.titre} ».")
    except (ErreurBiblio, ValueError) as exc:
        print(f"Impossible : {exc}")


def action_retards(service: BiblioService) -> None:
    retards = service.lister_retards()
    if not retards:
        print("Aucun emprunt en retard.")
        return
    for r in retards:
        print(
            f"  {r.code_livre} « {r.titre_livre} » | {r.matricule_etudiant} "
            f"| Prévu le {r.date_retour_prevue.strftime('%d/%m/%Y')} ({r.jours_retard} j de retard)"
        )


def main() -> None:
    chemin_db = Path(__file__).resolve().parent / "biblio.db"
    depot = DepotSQLite(chemin_db)
    depot.peupler_catalogue_initial()
    service = BiblioService(depot)

    try:
        while True:
            afficher_menu()
            choix = input("Votre choix : ").strip()
            if choix == "1":
                action_rechercher(service)
            elif choix == "2":
                action_emprunter(service)
            elif choix == "3":
                action_rendre(service)
            elif choix == "4":
                action_retards(service)
            elif choix == "0":
                print("À bientôt sur BiblioIIT !")
                break
            else:
                print("Choix invalide. Veuillez saisir 0, 1, 2, 3 ou 4.")
    finally:
        depot.fermer()


if __name__ == "__main__":
    main()
