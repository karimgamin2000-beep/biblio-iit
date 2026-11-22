"""Tests de l'interface TUI Textual pour BiblioIIT."""

import unittest

from depot_sqlite import DepotSQLite
from tui import BiblioTUI


class TestBiblioTUI(unittest.IsolatedAsyncioTestCase):
    async def test_tui_affiche_catalogue_et_filtre(self) -> None:
        depot = DepotSQLite(":memory:")
        depot.peupler_catalogue_initial()
        app = BiblioTUI(depot=depot)
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                table = app.query_one("#table-catalogue")
                self.assertEqual(table.row_count, 6)

                search = app.query_one("#search-input")
                search.value = "Kourouma"
                await pilot.pause()
                self.assertEqual(table.row_count, 2)
        finally:
            depot.fermer()

    async def test_tui_emprunt_et_retour_rapide(self) -> None:
        depot = DepotSQLite(":memory:")
        depot.peupler_catalogue_initial()
        app = BiblioTUI(depot=depot)
        try:
            async with app.run_test() as pilot:
                await pilot.pause()
                app.query_one("TabbedContent").active = "tab-rapide"
                await pilot.pause()
                app.query_one("#quick-code").value = "L002"
                app.query_one("#quick-matricule").value = "E2026-001"
                await pilot.click("#btn-quick-emprunt")
                await pilot.pause()

                livre = depot.obtenir_livre("L002")
                self.assertIsNotNone(livre)
                self.assertFalse(livre.disponible)

                await pilot.click("#btn-quick-retour")
                await pilot.pause()
                livre_rendu = depot.obtenir_livre("L002")
                self.assertIsNotNone(livre_rendu)
                self.assertTrue(livre_rendu.disponible)
        finally:
            depot.fermer()


if __name__ == "__main__":
    unittest.main()
