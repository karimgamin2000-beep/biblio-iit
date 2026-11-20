"""Tests d'intégration pour DepotSQLite et BiblioService."""

import unittest
from datetime import date

from depot_sqlite import DepotSQLite
from service import BiblioService, ErreurBiblio


class TestBiblioService(unittest.TestCase):
    def setUp(self) -> None:
        self.depot = DepotSQLite(":memory:")
        self.depot.peupler_catalogue_initial()
        self.service = BiblioService(self.depot)

    def tearDown(self) -> None:
        self.depot.fermer()

    def test_rechercher_kourouma(self) -> None:
        resultats = self.service.rechercher_livres("Kourouma")
        codes = [livre.code for livre in resultats]
        self.assertEqual(codes, ["L002", "L004"])

    def test_emprunter_puis_refuser_double_emprunt(self) -> None:
        emprunt = self.service.emprunter("L002", "E2026-001", date(2026, 10, 1))
        self.assertEqual(emprunt.date_retour_prevue, date(2026, 10, 15))

        with self.assertRaises(ErreurBiblio) as ctx:
            self.service.emprunter("L002", "E2026-002", date(2026, 10, 2))
        self.assertIn("déjà emprunté", str(ctx.exception))

    def test_rendre_livre_et_reemprunter(self) -> None:
        self.service.emprunter("L002", "E2026-001", date(2026, 10, 1))
        livre = self.service.rendre("L002", date(2026, 10, 10))
        self.assertEqual(livre.code, "L002")
        nouvel_emprunt = self.service.emprunter("L002", "E2026-002", date(2026, 10, 11))
        self.assertEqual(nouvel_emprunt.matricule_etudiant, "E2026-002")

    def test_lister_retards(self) -> None:
        self.service.emprunter("L004", "E2026-001", date(2026, 10, 1))
        retards_avant = self.service.lister_retards(date(2026, 10, 15))
        self.assertEqual(retards_avant, [])

        retards_apres = self.service.lister_retards(date(2026, 10, 20))
        self.assertEqual(len(retards_apres), 1)
        self.assertEqual(retards_apres[0].jours_retard, 5)


if __name__ == "__main__":
    unittest.main()
