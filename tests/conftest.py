"""Hermetic test corpus; the private production database is never required."""

import sqlite3

import pytest

from ohada_mcp.accounting_api import syscohada_client
from ohada_mcp.client import corpus_client


@pytest.fixture(autouse=True)
def isolated_test_corpus(tmp_path, monkeypatch):
    db_path = tmp_path / "sample_corpus.sqlite"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            document_id TEXT NOT NULL,
            text_content TEXT NOT NULL,
            parent_section TEXT DEFAULT '',
            hierarchy_path TEXT DEFAULT '',
            metadata_json TEXT DEFAULT '{}',
            owner_id TEXT,
            team_id TEXT,
            visibility TEXT DEFAULT 'private'
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            text_content,
            content='chunks',
            content_rowid='id'
        );
        """
    )
    connection.executemany(
        "INSERT INTO documents(id, name) VALUES (?, ?)",
        [
            ("audcg", "AUDCG-2010_fr.pdf"),
            ("auscgie", "AUSCGIE-2014_fr.pdf"),
            ("syscohada", "audcif_jo-ohada-15-02-2017.pdf"),
        ],
    )
    connection.executemany(
        """
        INSERT INTO chunks(
            id, document_id, hierarchy_path, text_content,
            metadata_json, visibility
        ) VALUES (?, ?, ?, ?, ?, 'public')
        """,
        [
            (
                100,
                "syscohada",
                "Classe 1 > Compte 14 — Subventions d'investissement > Commentaires",
                (
                    "[Compte 14] Le compte 14 enregistre les subventions "
                    "d'investissement accordées à l'entité."
                ),
                (
                    '{"document_type":"syscohada","authority_level":'
                    '"official_normative_and_technical","page_start":298,'
                    '"page_end":298,"class_code":"1","class_label":"Classe 1",'
                    '"account_code":"14","account_label":"Subventions '
                    'd\'investissement","account_subsection":"Commentaires",'
                    '"is_table":false}'
                ),
            ),
            (
                101,
                "syscohada",
                "Classe 1 > Compte 14 — Subventions d'investissement > Fonctionnement",
                (
                    "[Compte 14] Le compte 14 est crédité du montant de la "
                    "subvention acquise par le débit du compte approprié."
                ),
                (
                    '{"document_type":"syscohada","authority_level":'
                    '"official_normative_and_technical","page_start":299,'
                    '"page_end":299,"class_code":"1","class_label":"Classe 1",'
                    '"account_code":"14","account_label":"Subventions '
                    'd\'investissement","account_subsection":"Fonctionnement",'
                    '"is_table":false}'
                ),
            ),
        ],
    )
    connection.executemany(
        """
        INSERT INTO chunks(id, document_id, hierarchy_path, text_content)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                1,
                "audcg",
                "Prescription > Article 16",
                (
                    "[Prescription > Article 16]\nLes obligations nées à l'occasion de leur "
                    "commerce entre commerçants se prescrivent par cinq ans."
                ),
            ),
            (
                2,
                "auscgie",
                "Amortissement du capital > Article 655-1",
                (
                    "[Amortissement du capital > Article 655-1]\nLe capital peut faire "
                    "l'objet d'un amortissement conformément au présent Acte uniforme."
                ),
            ),
            (
                3,
                "auscgie",
                "Révocation > Article 326",
                (
                    "[Révocation > Article 326]\nLe gérant est révocable par la juridiction "
                    "compétente, pour juste motif, à la demande de tout associé."
                ),
            ),
        ],
    )
    connection.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild')")
    connection.commit()
    connection.close()

    monkeypatch.setattr(corpus_client, "db_path", db_path)
    monkeypatch.setattr(syscohada_client, "db_path", db_path)
    yield db_path
