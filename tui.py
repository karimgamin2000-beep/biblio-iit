"""Interface console TUI (Textual) pour BiblioIIT."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from depot_sqlite import DepotSQLite
from regles import calculer_jours_retard
from service import BiblioService, ErreurBiblio


class EmpruntModal(ModalScreen[str | None]):
    """Fenêtre modale pour saisir le matricule étudiant lors d'un emprunt."""

    CSS = """
    EmpruntModal {
        align: center middle;
    }
    #modal-box {
        width: 54;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    #modal-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #modal-buttons {
        margin-top: 1;
        height: auto;
        align-horizontal: right;
    }
    #modal-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, code_livre: str, titre_livre: str) -> None:
        super().__init__()
        self.code_livre = code_livre
        self.titre_livre = titre_livre

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label(f"Emprunter [{self.code_livre}] {self.titre_livre}", id="modal-title")
            yield Label("Matricule étudiant (ex: E2026-001) :")
            yield Input(placeholder="E2026-001", id="modal-matricule")
            with Horizontal(id="modal-buttons"):
                yield Button("Annuler", id="btn-annuler", variant="default")
                yield Button("Valider", id="btn-valider", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#modal-matricule", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-valider":
            val = self.query_one("#modal-matricule", Input).value.strip()
            self.dismiss(val if val else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        self.dismiss(val if val else None)


class BiblioTUI(App[None]):
    """Application TUI moderne de gestion de bibliothèque pour BiblioIIT."""

    TITLE = "BiblioIIT — Gestion de Bibliothèque"
    SUB_TITLE = "Interface Console TUI (Python + SQLite + Textual)"

    CSS = """
    #stats-bar {
        height: 3;
        padding: 0 1;
        margin: 1 1 0 1;
        border: round $primary;
        background: $panel;
        content-align: center middle;
    }
    .stat-item {
        width: 1fr;
        content-align: center middle;
        text-style: bold;
    }
    #search-row {
        height: auto;
        margin-bottom: 1;
    }
    #search-input {
        width: 1fr;
    }
    #btn-reset-search {
        margin-left: 1;
    }
    .actions-row {
        height: auto;
        margin-top: 1;
    }
    .actions-row Button {
        margin-right: 1;
    }
    DataTable {
        height: 1fr;
        min-height: 10;
    }
    #quick-form {
        padding: 1 2;
        max-width: 72;
    }
    #quick-form Label {
        margin-top: 1;
    }
    #quick-form Input {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quitter"),
        Binding("r", "refresh_all", "Rafraîchir"),
        Binding("f", "focus_search", "Rechercher"),
    ]

    def __init__(self, depot: DepotSQLite | None = None) -> None:
        super().__init__()
        if depot is None:
            chemin_db = Path(__file__).resolve().parent / "biblio.db"
            self.depot = DepotSQLite(chemin_db)
            self.depot.peupler_catalogue_initial()
            self._owns_depot = True
        else:
            self.depot = depot
            self._owns_depot = False
        self.service = BiblioService(self.depot)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="stats-bar"):
            yield Static("", id="stat-total", classes="stat-item")
            yield Static("", id="stat-dispo", classes="stat-item")
            yield Static("", id="stat-emprunt", classes="stat-item")
            yield Static("", id="stat-retard", classes="stat-item")

        with TabbedContent(initial="tab-catalogue"):
            with TabPane("Catalogue & Recherche", id="tab-catalogue"):
                with Horizontal(id="search-row"):
                    yield Input(placeholder="Rechercher par titre, auteur ou code (ex: Kourouma)...", id="search-input")
                    yield Button("Effacer", id="btn-reset-search", variant="default")
                yield DataTable(id="table-catalogue", cursor_type="row")
                with Horizontal(classes="actions-row"):
                    yield Button("Emprunter la sélection", id="btn-emprunter-sel", variant="primary")
                    yield Button("Rendre la sélection", id="btn-rendre-sel", variant="success")
                    yield Button("Rafraîchir", id="btn-refresh", variant="default")

            with TabPane("Emprunts & Retards", id="tab-emprunts"):
                yield DataTable(id="table-emprunts", cursor_type="row")
                with Horizontal(classes="actions-row"):
                    yield Button("Rendre l'emprunt sélectionné", id="btn-rendre-emprunt", variant="success")

            with TabPane("Action rapide", id="tab-rapide"):
                with Vertical(id="quick-form"):
                    yield Label("Code du livre (ex: L002) :")
                    yield Input(placeholder="L002", id="quick-code")
                    yield Label("Matricule étudiant (ex: E2026-001) :")
                    yield Input(placeholder="E2026-001", id="quick-matricule")
                    with Horizontal(classes="actions-row"):
                        yield Button("Confirmer l'emprunt", id="btn-quick-emprunt", variant="primary")
                        yield Button("Confirmer le retour", id="btn-quick-retour", variant="success")

        yield Footer()

    def on_mount(self) -> None:
        cat_table = self.query_one("#table-catalogue", DataTable)
        cat_table.add_columns("Code", "Titre", "Auteur", "Année", "Statut")

        emp_table = self.query_one("#table-emprunts", DataTable)
        emp_table.add_columns("Code", "Titre", "Matricule", "Emprunté le", "Retour prévu", "Retard")

        self.refresh_data()

    def on_unmount(self) -> None:
        if self._owns_depot:
            self.depot.fermer()

    def refresh_data(self, filtre: str | None = None) -> None:
        if filtre is None:
            filtre = self.query_one("#search-input", Input).value
        livres = self.service.rechercher_livres(filtre)
        tous_livres = self.service.rechercher_livres("")

        cat_table = self.query_one("#table-catalogue", DataTable)
        cat_table.clear()
        for livre in livres:
            statut = "Disponible" if livre.disponible else "Emprunté"
            cat_table.add_row(livre.code, livre.titre, livre.auteur, str(livre.annee), statut, key=livre.code)

        from datetime import date
        aujourd_hui = date.today()
        ouverts = self.depot.lister_emprunts_ouverts_avec_livres()
        emp_table = self.query_one("#table-emprunts", DataTable)
        emp_table.clear()
        retards_count = 0
        for emp, titre in ouverts:
            j = calculer_jours_retard(emp.date_retour_prevue, aujourd_hui)
            if j > 0:
                retards_count += 1
            retard_txt = f"{j} j" if j > 0 else "À l'heure"
            emp_table.add_row(
                emp.code_livre,
                titre,
                emp.matricule_etudiant,
                emp.date_emprunt.strftime("%d/%m/%Y"),
                emp.date_retour_prevue.strftime("%d/%m/%Y"),
                retard_txt,
                key=emp.code_livre,
            )

        total = len(tous_livres)
        dispos = sum(1 for l in tous_livres if l.disponible)
        empruntes = total - dispos
        self.query_one("#stat-total", Static).update(f"Total : {total}")
        self.query_one("#stat-dispo", Static).update(f"Disponibles : {dispos}")
        self.query_one("#stat-emprunt", Static).update(f"Empruntés : {empruntes}")
        self.query_one("#stat-retard", Static).update(f"Retards : {retards_count}")

    def action_refresh_all(self) -> None:
        self.refresh_data()
        self.notify("Catalogue et emprunts actualisés.")

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.refresh_data(event.value)

    def _selected_code_from_table(self, table_id: str) -> str | None:
        table = self.query_one(f"#{table_id}", DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            return None
        row_key = table.coordinate_to_cell_key((table.cursor_row, 0)).row_key
        return str(row_key.value) if row_key is not None else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-reset-search":
            inp = self.query_one("#search-input", Input)
            inp.value = ""
            self.refresh_data("")
        elif bid == "btn-refresh":
            self.action_refresh_all()
        elif bid == "btn-emprunter-sel":
            code = self._selected_code_from_table("table-catalogue")
            if not code:
                self.notify("Sélectionnez un livre dans le tableau.", severity="warning")
                return
            livre = self.depot.obtenir_livre(code)
            if livre is None:
                return
            if not livre.disponible:
                self.notify(f"Le livre « {livre.titre} » est déjà emprunté.", severity="error")
                return

            def _on_matricule(matricule: str | None) -> None:
                if not matricule:
                    return
                try:
                    emp = self.service.emprunter(code, matricule)
                    self.refresh_data()
                    self.notify(
                        f"Emprunt enregistré ({code} → {emp.matricule_etudiant}). Retour prévu le {emp.date_retour_prevue.strftime('%d/%m/%Y')}."
                    )
                except (ErreurBiblio, ValueError) as exc:
                    self.notify(str(exc), severity="error")

            self.push_screen(EmpruntModal(livre.code, livre.titre), _on_matricule)
        elif bid == "btn-rendre-sel":
            code = self._selected_code_from_table("table-catalogue")
            self._rendre_par_code(code)
        elif bid == "btn-rendre-emprunt":
            code = self._selected_code_from_table("table-emprunts")
            self._rendre_par_code(code)
        elif bid == "btn-quick-emprunt":
            code = self.query_one("#quick-code", Input).value
            mat = self.query_one("#quick-matricule", Input).value
            try:
                emp = self.service.emprunter(code, mat)
                self.refresh_data()
                self.notify(
                    f"Emprunt enregistré ({emp.code_livre}). Retour prévu le {emp.date_retour_prevue.strftime('%d/%m/%Y')}."
                )
            except (ErreurBiblio, ValueError) as exc:
                self.notify(str(exc), severity="error")
        elif bid == "btn-quick-retour":
            code = self.query_one("#quick-code", Input).value
            self._rendre_par_code(code)

    def _rendre_par_code(self, code: str | None) -> None:
        if not code:
            self.notify("Sélectionnez ou saisissez un code de livre.", severity="warning")
            return
        try:
            livre = self.service.rendre(code)
            self.refresh_data()
            self.notify(f"Retour enregistré pour « {livre.titre} ».")
        except (ErreurBiblio, ValueError) as exc:
            self.notify(str(exc), severity="error")


def lancer_tui() -> None:
    app = BiblioTUI()
    app.run()


if __name__ == "__main__":
    lancer_tui()
