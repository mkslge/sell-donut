from __future__ import annotations

from sqlite3 import Connection

from app.storage.sqlite_schema import (
    SQLITE_LOGGING_SQL,
    SQLITE_RATINGS_INDEX_SQL,
    SQLITE_RATINGS_MIGRATION_SQL,
    SQLITE_SCHEMA_SQL,
)


def initialize_sqlite_schema(connection: Connection) -> None:
    """Create the SQLite schema when the database is empty."""
    connection.executescript(SQLITE_SCHEMA_SQL)
    migrate_ratings_table_if_needed(connection)
    connection.commit()


def initialize_sqlite_logging(connection: Connection) -> None:
    """Create the single-row logging table and seed its counter row."""
    connection.executescript(SQLITE_LOGGING_SQL)
    connection.commit()


def migrate_ratings_table_if_needed(connection: Connection) -> None:
    """Upgrade old SQLite rating tables in place when the schema drifts."""
    table_info = connection.execute("PRAGMA table_info(ratings)").fetchall()
    if not table_info:
        return

    columns = {row[1] for row in table_info}
    create_sql_row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'ratings'"
    ).fetchone()
    create_sql = create_sql_row[0] if create_sql_row and create_sql_row[0] else ""
    needs_submitter_fingerprint = "submitterFingerprint" not in columns
    needs_mixed_verdict = "MIXED" not in create_sql

    if not needs_submitter_fingerprint and not needs_mixed_verdict:
        return

    submitter_select = (
        "''" if needs_submitter_fingerprint else "COALESCE(submitterFingerprint, '')"
    )

    connection.executescript(SQLITE_RATINGS_MIGRATION_SQL)
    connection.execute(
        f"""
        INSERT INTO ratings (
            id,
            seller_id,
            seller_username,
            normalized_username,
            verdict,
            item_type,
            item_name,
            quantity,
            price,
            currency,
            description,
            evidence_url,
            reporter_username,
            submitterFingerprint,
            created_at,
            updated_at
        )
        SELECT
            id,
            seller_id,
            seller_username,
            normalized_username,
            verdict,
            item_type,
            item_name,
            quantity,
            price,
            currency,
            description,
            evidence_url,
            reporter_username,
            {submitter_select},
            created_at,
            updated_at
        FROM ratings_old;
        """
    )
    connection.execute("DROP TABLE ratings_old")
    connection.executescript(SQLITE_RATINGS_INDEX_SQL)
