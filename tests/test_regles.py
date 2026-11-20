"""Tests unitaires pour regles.py."""

import unittest
from datetime import date

from regles import (
    calculer_date_retour,
    calculer_jours_retard,
    est_en_retard,
    valider_code_livre,
    valider_matricule,
)


class TestRegles(unittest.TestCase):
    def test_calculer_date_retour_par_defaut(self) -> None:
        self.assertEqual(calculer_date_retour(date(2026, 10, 1)), date(2026, 10, 15))

    def test_calculer_date_retour_duree_invalide(self) -> None:
        with self.assertRaises(ValueError):
            calculer_date_retour(date(2026, 10, 1), 0)

    def test_jours_retard_et_est_en_retard(self) -> None:
        prevue = date(2026, 10, 15)
        self.assertEqual(calculer_jours_retard(prevue, date(2026, 10, 15)), 0)
        self.assertFalse(est_en_retard(prevue, date(2026, 10, 15)))
        self.assertEqual(calculer_jours_retard(prevue, date(2026, 10, 18)), 3)
        self.assertTrue(est_en_retard(prevue, date(2026, 10, 18)))

    def test_validation_matricule_et_code(self) -> None:
        self.assertEqual(valider_matricule(" e2026-001 "), "E2026-001")
        self.assertEqual(valider_code_livre(" l002 "), "L002")
        with self.assertRaises(ValueError):
            valider_matricule("ab")
        with self.assertRaises(ValueError):
            valider_code_livre("   ")


if __name__ == "__main__":
    unittest.main()
