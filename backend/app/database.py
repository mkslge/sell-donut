from __future__ import annotations

import sqlite3
import struct
from pathlib import Path
from threading import RLock
from typing import Any

import pyodbc
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


AZURE_SQL_ACCESS_TOKEN_ATTR = 1256


class Database:
    """Database wrapper used by repositories.

    SQLite is kept for local fallback and tests. Azure SQL uses a real
    SQLAlchemy engine backed by pyodbc so the application talks to the
    database through a standard Python driver stack.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        connection_string: str | None = None,
    ):
        self.path = Path(path) if path is not None else None
        self.connection_string = connection_string
        self.backend = "azure_sql" if connection_string else "sqlite"
        self._connection: Any | None = None
        self._engine: Engine | None = None
        self._lock = RLock()

        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def connection(self):
        if self.backend == "azure_sql":
            raise RuntimeError("Azure SQL mode does not expose a raw connection object.")

        if self._connection is None:
            self._connection = sqlite3.connect(
                self.path,
                check_same_thread=False,
            )
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    @property
    def engine(self) -> Engine:
        if self.backend != "azure_sql":
            raise RuntimeError("SQLite mode does not use a SQLAlchemy engine.")

        if self._engine is None:
            self._engine = create_engine(
                "mssql+pyodbc://",
                creator=self._create_azure_connection,
                pool_pre_ping=True,
                future=True,
            )
        return self._engine

    def initialize(self) -> None:
        with self._lock:
            if self.backend == "azure_sql":
                self._initialize_azure_sql()
            else:
                self._initialize_sqlite()

    def _initialize_sqlite(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sellers (
                id TEXT PRIMARY KEY,
                seller_username TEXT NOT NULL,
                normalized_username TEXT NOT NULL UNIQUE,
                minecraft_uuid TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ratings (
                id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                seller_username TEXT NOT NULL,
                normalized_username TEXT NOT NULL,
                verdict TEXT NOT NULL CHECK (verdict IN ('LEGIT', 'SCAMMER', 'MIXED')),
                item_type TEXT NOT NULL,
                item_name TEXT,
                quantity INTEGER,
                price REAL,
                currency TEXT,
                description TEXT,
                evidence_url TEXT,
                reporter_username TEXT,
                submitterFingerprint TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_ratings_normalized_username
            ON ratings(normalized_username);

            CREATE INDEX IF NOT EXISTS idx_ratings_created_at
            ON ratings(created_at);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_sellers_minecraft_uuid
            ON sellers(minecraft_uuid)
            WHERE minecraft_uuid IS NOT NULL;
            """
        )
        self._migrate_ratings_table_if_needed()
        self.connection.commit()

    def _migrate_ratings_table_if_needed(self) -> None:
        table_info = self.connection.execute("PRAGMA table_info(ratings)").fetchall()
        if not table_info:
            return

        columns = {row[1] for row in table_info}
        create_sql_row = self.connection.execute(
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

        self.connection.executescript(
            """
            ALTER TABLE ratings RENAME TO ratings_old;

            CREATE TABLE ratings (
                id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                seller_username TEXT NOT NULL,
                normalized_username TEXT NOT NULL,
                verdict TEXT NOT NULL CHECK (verdict IN ('LEGIT', 'SCAMMER', 'MIXED')),
                item_type TEXT NOT NULL,
                item_name TEXT,
                quantity INTEGER,
                price REAL,
                currency TEXT,
                description TEXT,
                evidence_url TEXT,
                reporter_username TEXT,
                submitterFingerprint TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
            );
            """
        )

        self.connection.execute(
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
        self.connection.execute("DROP TABLE ratings_old")
        self.connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_ratings_normalized_username
            ON ratings(normalized_username);

            CREATE INDEX IF NOT EXISTS idx_ratings_created_at
            ON ratings(created_at);
            """
        )

    def _initialize_azure_sql(self) -> None:
        self.execute(
            """
            IF OBJECT_ID('dbo.sellers', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.sellers (
                    id NVARCHAR(64) NOT NULL PRIMARY KEY,
                    seller_username NVARCHAR(16) NOT NULL,
                    normalized_username NVARCHAR(16) NOT NULL UNIQUE,
                    minecraft_uuid NVARCHAR(32) NULL,
                    created_at DATETIME2 NOT NULL,
                    updated_at DATETIME2 NOT NULL
                );
            END
            """
        )
        self.execute(
            """
            IF OBJECT_ID('dbo.ratings', 'U') IS NULL
            BEGIN
                CREATE TABLE dbo.ratings (
                    id NVARCHAR(64) NOT NULL PRIMARY KEY,
                    seller_id NVARCHAR(64) NOT NULL,
                    seller_username NVARCHAR(16) NOT NULL,
                    normalized_username NVARCHAR(16) NOT NULL,
                    verdict NVARCHAR(16) NOT NULL,
                    item_type NVARCHAR(60) NOT NULL,
                    item_name NVARCHAR(120) NULL,
                    quantity INT NULL,
                    price DECIMAL(18, 2) NULL,
                    currency NVARCHAR(32) NULL,
                    description NVARCHAR(1000) NOT NULL,
                    evidence_url NVARCHAR(2048) NULL,
                    reporter_username NVARCHAR(16) NULL,
                    submitterFingerprint NVARCHAR(256) NOT NULL CONSTRAINT DF_ratings_submitterFingerprint DEFAULT(''),
                    created_at DATETIME2 NOT NULL,
                    updated_at DATETIME2 NOT NULL,
                    CONSTRAINT FK_ratings_seller_id FOREIGN KEY (seller_id)
                        REFERENCES dbo.sellers(id) ON DELETE CASCADE,
                    CONSTRAINT CK_ratings_verdict CHECK (verdict IN ('LEGIT', 'SCAMMER', 'MIXED'))
                );
            END
            """
        )
        self.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.indexes
                WHERE name = 'idx_ratings_normalized_username'
                  AND object_id = OBJECT_ID('dbo.ratings')
            )
            BEGIN
                CREATE INDEX idx_ratings_normalized_username
                ON dbo.ratings(normalized_username);
            END
            """
        )
        self.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.indexes
                WHERE name = 'idx_ratings_created_at'
                  AND object_id = OBJECT_ID('dbo.ratings')
            )
            BEGIN
                CREATE INDEX idx_ratings_created_at
                ON dbo.ratings(created_at);
            END
            """
        )
        self.execute(
            """
            IF NOT EXISTS (
                SELECT 1
                FROM sys.indexes
                WHERE name = 'idx_sellers_minecraft_uuid'
                  AND object_id = OBJECT_ID('dbo.sellers')
            )
            BEGIN
                CREATE UNIQUE INDEX idx_sellers_minecraft_uuid
                ON dbo.sellers(minecraft_uuid)
                WHERE minecraft_uuid IS NOT NULL;
            END
            """
        )

    def execute(self, query: str, parameters: tuple = ()) -> None:
        with self._lock:
            if self.backend == "azure_sql":
                with self.engine.begin() as connection:
                    connection.exec_driver_sql(query, parameters)
                return

            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            self.connection.commit()
            cursor.close()

    def query(self, query: str, parameters: tuple = ()) -> list[dict[str, Any]]:
        with self._lock:
            if self.backend == "azure_sql":
                with self.engine.connect() as connection:
                    result = connection.exec_driver_sql(query, parameters)
                    return [dict(row) for row in result.mappings().all()]

            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            columns = [column[0] for column in cursor.description or []]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return rows

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def _create_azure_connection(self):
        """Open an Azure SQL connection with an Entra access token.

        Preconditions:
        - `self.connection_string` contains the Azure SQL server and database.
        - The local user has authenticated with `az login` or the app is
          running in an environment where `DefaultAzureCredential` can obtain a
          token.

        Postconditions:
        - Returns a live `pyodbc` connection ready for SQLAlchemy to use.
        """
        if not self.connection_string:
            raise RuntimeError("Azure SQL mode requires a connection string.")

        token = self._acquire_azure_sql_token()
        connection_string = self._build_odbc_connection_string(self.connection_string)
        return pyodbc.connect(
            connection_string,
            attrs_before={AZURE_SQL_ACCESS_TOKEN_ATTR: token},
        )

    def _acquire_azure_sql_token(self) -> bytes:
        """Acquire a database access token for Azure SQL.

        Preconditions:
        - The environment supports Entra authentication for the current user or
          managed identity.

        Postconditions:
        - Returns the token in the format expected by the SQL Server ODBC
          driver.
        """
        credential = self._select_credential()
        token = credential.get_token("https://database.windows.net/.default").token
        token_bytes = token.encode("utf-16-le")
        return struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    def _select_credential(self):
        auth_mode = self._connection_string_value("authentication") or ""
        if auth_mode.lower() == "activedirectorymanagedidentity":
            return ManagedIdentityCredential()
        return DefaultAzureCredential()

    def _connection_string_value(self, key: str) -> str | None:
        if not self.connection_string:
            return None

        prefix = f"{key.lower()}="
        for raw_part in self.connection_string.split(";"):
            part = raw_part.strip()
            if not part:
                continue
            if part.lower().startswith(prefix):
                return part.split("=", 1)[1].strip().strip("{}")
        return None

    def _build_odbc_connection_string(self, connection_string: str) -> str:
        """Normalize the ODBC string for pyodbc and strip unsupported auth keys."""
        parts = []
        has_driver = False
        for raw_part in connection_string.split(";"):
            part = raw_part.strip()
            if not part:
                continue

            key, sep, value = part.partition("=")
            if not sep:
                continue

            key_lower = key.strip().lower()
            if key_lower == "authentication":
                continue
            if key_lower == "driver":
                has_driver = True
            parts.append(f"{key.strip()}={value.strip()}")

        if not has_driver:
            parts.insert(0, "Driver={ODBC Driver 18 for SQL Server}")

        return ";".join(parts)
