from __future__ import annotations

import struct
from typing import Any

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


SQL_COPT_SS_ACCESS_TOKEN = 1256


class AzureSqlClient:
    """Create and manage the Azure SQL connection stack.

    This keeps transport details out of the main database adapter so the
    adapter only decides when to use Azure SQL, not how to build the driver.
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                "mssql+pyodbc://",
                creator=self._create_connection,
                pool_pre_ping=True,
                future=True,
            )
        return self._engine

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def _create_connection(self):
        auth_mode = self._connection_string_value("authentication")
        connection_string = self._build_odbc_connection_string(self.connection_string)

        if auth_mode and auth_mode.lower() in {
            "activedirectorydefault",
            "activedirectorymanagedidentity",
        }:
            token = self._acquire_access_token(auth_mode)
            return pyodbc.connect(
                connection_string,
                attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token},
            )

        return pyodbc.connect(connection_string)

    def _acquire_access_token(self, auth_mode: str) -> bytes:
        if auth_mode.lower() == "activedirectorymanagedidentity":
            credential = ManagedIdentityCredential()
        elif auth_mode.lower() == "activedirectorydefault":
            # For local development this intentionally mirrors `sqlcmd -G`:
            # use the account selected by `az login`.
            credential = AzureCliCredential()
        else:
            credential = DefaultAzureCredential()

        raw_token = credential.get_token("https://database.windows.net/.default").token
        token_bytes = raw_token.encode("utf-16-le")
        return struct.pack("=i", len(token_bytes)) + token_bytes

    def _connection_string_value(self, key: str) -> str | None:
        prefix = f"{key.lower()}="
        for raw_part in self.connection_string.split(";"):
            part = raw_part.strip()
            if not part:
                continue
            if part.lower().startswith(prefix):
                return part.split("=", 1)[1].strip().strip("{}")
        return None

    def _build_odbc_connection_string(self, connection_string: str) -> str:
        parts: list[str] = []
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
