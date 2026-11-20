"""Couche d'accès aux données SQLite pour BiblioIIT."""

import sqlite3
from datetime import date
from pathlib import Path

from modeles import Emprunt, Livre, RetardInfo

CATALOGUE_INITIAL = [
    ("L001", "L'Enfant noir", "Camara Laye", 1953),
    ("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968),
    ("L003", "Une si longue lettre", "Mariama Bâ", 1979),
    ("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000),
    ("L005", "Python Crash Course", "Eric Matthes", 2023),
    ("L006", "Clean Code", "Robert C. Martin", 2008),
]


class DepotSQLite:
    """Gère la persistance des livres et des emprunts dans SQLite."""

    def __init__(self, chemin_db: str | Path = "biblio.db") -> None:
        self.chemin_db = str(chemin_db)
        self._conn = sqlite3.connect(self.chemin_db)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._initialiser_schema()

    def _initialiser_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS livres (
                    code TEXT PRIMARY KEY,
                    titre TEXT NOT NULL,
                    auteur TEXT NOT NULL,
                    annee INTEGER NOT NULL
                );
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS emprunts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code_livre TEXT NOT NULL,
                    matricule_etudiant TEXT NOT NULL,
                    date_emprunt TEXT NOT NULL,
                    date_retour_prevue TEXT NOT NULL,
                    date_retour_reelle TEXT,
                    FOREIGN KEY (code_livre) REFERENCES livres(code)
                );
                """
            )

    def peupler_catalogue_initial(self) -> None:
        """Insère le catalogue de démonstration si la table des livres est vide."""
        cur = self._conn.execute("SELECT COUNT(*) FROM livres;")
        if cur.fetchone()[0] > 0:
            return
        with self._conn:
            self._conn.executemany(
                "INSERT INTO livres (code, titre, auteur, annee) VALUES (?, ?, ?, ?);",
                CATALOGUE_INITIAL,
            )

    def ajouter_livre(self, livre: Livre) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO livres (code, titre, auteur, annee) VALUES (?, ?, ?, ?);",
                (livre.code, livre.titre, livre.auteur, livre.annee),
            )

    def obtenir_livre(self, code: str) -> Livre | None:
        row = self._conn.execute(
            """
            SELECT l.code, l.titre, l.auteur, l.annee,
                   NOT EXISTS (
                       SELECT 1 FROM emprunts e
                       WHERE e.code_livre = l.code AND e.date_retour_reelle IS NULL
                   ) AS disponible
            FROM livres l
            WHERE l.code = ?;
            """,
            (code,),
        ).fetchone()
        if row is None:
            return None
        return Livre(
            code=row["code"],
            titre=row["titre"],
            auteur=row["auteur"],
            annee=row["annee"],
            disponible=bool(row["disponible"]),
        )

    def rechercher_livres(self, mot_cle: str) -> list[Livre]:
        motif = f"%{mot_cle.strip()}%"
        rows = self._conn.execute(
            """
            SELECT l.code, l.titre, l.auteur, l.annee,
                   NOT EXISTS (
                       SELECT 1 FROM emprunts e
                       WHERE e.code_livre = l.code AND e.date_retour_reelle IS NULL
                   ) AS disponible
            FROM livres l
            WHERE l.titre LIKE ? OR l.auteur LIKE ? OR l.code LIKE ?
            ORDER BY l.code;
            """,
            (motif, motif, motif),
        ).fetchall()
        return [
            Livre(
                code=r["code"],
                titre=r["titre"],
                auteur=r["auteur"],
                annee=r["annee"],
                disponible=bool(r["disponible"]),
            )
            for r in rows
        ]

    def compter_emprunts_actifs(self, matricule: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM emprunts WHERE matricule_etudiant = ? AND date_retour_reelle IS NULL;",
            (matricule,),
        ).fetchone()
        return int(row[0])

    def enregistrer_emprunt(self, emprunt: Emprunt) -> int:
        with self._conn:
            cur = self._conn.execute(
                """
                INSERT INTO emprunts (code_livre, matricule_etudiant, date_emprunt, date_retour_prevue, date_retour_reelle)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    emprunt.code_livre,
                    emprunt.matricule_etudiant,
                    emprunt.date_emprunt.isoformat(),
                    emprunt.date_retour_prevue.isoformat(),
                    emprunt.date_retour_reelle.isoformat() if emprunt.date_retour_reelle else None,
                ),
            )
            return int(cur.lastrowid)

    def obtenir_emprunt_actif(self, code_livre: str) -> Emprunt | None:
        row = self._conn.execute(
            """
            SELECT id, code_livre, matricule_etudiant, date_emprunt, date_retour_prevue, date_retour_reelle
            FROM emprunts
            WHERE code_livre = ? AND date_retour_reelle IS NULL;
            """,
            (code_livre,),
        ).fetchone()
        if row is None:
            return None
        return Emprunt(
            id=row["id"],
            code_livre=row["code_livre"],
            matricule_etudiant=row["matricule_etudiant"],
            date_emprunt=date.fromisoformat(row["date_emprunt"]),
            date_retour_prevue=date.fromisoformat(row["date_retour_prevue"]),
            date_retour_reelle=None,
        )

    def cloturer_emprunt(self, emprunt_id: int, date_retour_reelle: date) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE emprunts SET date_retour_reelle = ? WHERE id = ?;",
                (date_retour_reelle.isoformat(), emprunt_id),
            )

    def lister_emprunts_ouverts_avec_livres(self) -> list[tuple[Emprunt, str]]:
        rows = self._conn.execute(
            """
            SELECT e.id, e.code_livre, e.matricule_etudiant, e.date_emprunt, e.date_retour_prevue, l.titre
            FROM emprunts e
            JOIN livres l ON l.code = e.code_livre
            WHERE e.date_retour_reelle IS NULL
            ORDER BY e.date_retour_prevue ASC;
            """
        ).fetchall()
        resultat: list[tuple[Emprunt, str]] = []
        for r in rows:
            emprunt = Emprunt(
                id=r["id"],
                code_livre=r["code_livre"],
                matricule_etudiant=r["matricule_etudiant"],
                date_emprunt=date.fromisoformat(r["date_emprunt"]),
                date_retour_prevue=date.fromisoformat(r["date_retour_prevue"]),
                date_retour_reelle=None,
            )
            resultat.append((emprunt, r["titre"]))
        return resultat

    def fermer(self) -> None:
        self._conn.close()
