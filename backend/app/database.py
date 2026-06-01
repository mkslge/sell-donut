from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any

from app.storage.azure_sql import AzureSqlClient
from app.storage.sqlite_store import initialize_sqlite_schema


class Database:
    """Database adapter used by repositories.

    This class stays intentionally small: it chooses the backend, exposes a
    query/execute surface, and delegates the actual SQL Server and SQLite
    mechanics to focused helpers in `app.storage`.
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
        self._azure_client: AzureSqlClient | None = (
            AzureSqlClient(connection_string) if connection_string else None
        )
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
    def azure_engine(self):
        if self.backend != "azure_sql" or self._azure_client is None:
            raise RuntimeError("Azure SQL engine is unavailable in SQLite mode.")
        return self._azure_client.engine

    def initialize(self) -> None:
        with self._lock:
            if self.backend == "azure_sql":
                self._initialize_azure_sql()
            else:
                initialize_sqlite_schema(self.connection)

    def _initialize_azure_sql(self) -> None:
        from app.storage.azure_schema import initialize_azure_sql_schema

        initialize_azure_sql_schema(self)

    def execute(self, query: str, parameters: tuple = ()) -> None:
        with self._lock:
            if self.backend == "azure_sql":
                with self.azure_engine.begin() as connection:
                    connection.exec_driver_sql(query, parameters)
                return

            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            self.connection.commit()
            cursor.close()

    def query(self, query: str, parameters: tuple = ()) -> list[dict[str, Any]]:
        with self._lock:
            if self.backend == "azure_sql":
                with self.azure_engine.connect() as connection:
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
        if self._azure_client is not None:
            self._azure_client.close()
            self._azure_client = None
