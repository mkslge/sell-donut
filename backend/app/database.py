import sqlite3
from pathlib import Path
from threading import Lock


class Database:
    """Small SQLite access wrapper used by repositories.

    The wrapper centralizes connection creation, schema initialization, commit
    behavior, and thread locking. That keeps repository code focused on SQL
    intent instead of connection lifecycle details.
    """

    def __init__(self, path: str | Path):
        """Create a lazy database handle.

        Preconditions:
        - `path` is a file path, not a directory.

        Postconditions:
        - The parent directory exists.
        - No SQLite connection is opened until `connection` is first accessed.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None
        self._lock = Lock()

    @property
    def connection(self) -> sqlite3.Connection:
        """Return the shared SQLite connection for this wrapper.

        Preconditions:
        - The process has permission to open the configured database file.

        Postconditions:
        - A connection exists with row results exposed as `sqlite3.Row`.
        - Foreign-key enforcement is enabled for this connection.

        Explanation:
        SQLite disables foreign-key checks by default, so enabling the pragma at
        connection creation is required for `ON DELETE CASCADE` to work.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.path,
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def initialize(self) -> None:
        """Create the required schema if it does not already exist.

        Preconditions:
        - `connection` can open the configured SQLite database.

        Postconditions:
        - `sellers` and `ratings` tables exist.
        - Lookup indexes for rating list queries exist.

        Explanation:
        This prototype intentionally uses idempotent DDL instead of migrations.
        That keeps local setup simple while preserving a clear future migration
        boundary when Alembic or another migration tool is introduced.
        """
        with self._lock:
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
                    verdict TEXT NOT NULL CHECK (verdict IN ('LEGIT', 'SCAMMER')),
                    item_type TEXT NOT NULL,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    currency TEXT,
                    description TEXT,
                    evidence_url TEXT,
                    reporter_username TEXT,
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
            self.connection.commit()

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Run a write statement and commit it.

        Preconditions:
        - `query` is a parameterized SQL statement.
        - Caller passes untrusted values via `parameters`, not string
          interpolation.

        Postconditions:
        - The SQL statement has executed inside the database lock.
        - The transaction is committed before the cursor is returned.
        """
        with self._lock:
            cursor = self.connection.execute(query, parameters)
            self.connection.commit()
            return cursor

    def query(self, query: str, parameters: tuple = ()) -> list[sqlite3.Row]:
        """Run a read statement and return all rows.

        Preconditions:
        - `query` is a parameterized SELECT-style SQL statement.
        - Caller passes untrusted values via `parameters`.

        Postconditions:
        - The SQL statement has executed inside the database lock.
        - Returned rows support dict-like column access.
        """
        with self._lock:
            return list(self.connection.execute(query, parameters))

    def close(self) -> None:
        """Close the SQLite connection if one was opened.

        Preconditions:
        - None; this method is safe to call repeatedly.

        Postconditions:
        - The underlying SQLite connection is closed.
        - Future access to `connection` opens a fresh connection.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
