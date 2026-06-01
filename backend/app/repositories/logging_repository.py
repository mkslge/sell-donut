from __future__ import annotations

from app.database import Database


class LoggingRepository:
    """Persistence boundary for the site visit counter."""

    def __init__(self, database: Database):
        self.database = database

    def initialize(self) -> None:
        """Ensure the logging table exists and has one counter row."""
        if self._needs_migration():
            self._migrate_legacy_table()

        if self.database.backend == "azure_sql":
            self.database.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM dbo.logging
                    WHERE id = 1
                )
                BEGIN
                    INSERT INTO dbo.logging (id, visit_count)
                    VALUES (1, 0);
                END
                """
            )
            return

        self.database.execute(
            """
            INSERT OR IGNORE INTO logging (id, visit_count)
            VALUES (1, 0)
            """
        )

    def _needs_migration(self) -> bool:
        """Return whether the old stubbed logging table shape still exists."""
        if self.database.backend == "azure_sql":
            rows = self.database.query(
                """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_NAME = 'logging'
                """
            )
            columns = {str(row["COLUMN_NAME"]) for row in rows}
            return "visits" in columns and "visit_count" not in columns

        rows = self.database.query("PRAGMA table_info(logging)")
        columns = {str(row["name"]) for row in rows} if rows else set()
        return "visits" in columns and "visit_count" not in columns

    def _migrate_legacy_table(self) -> None:
        """Rename the old logging table shape into the new single-row counter."""
        if self.database.backend == "azure_sql":
            self.database.execute("EXEC sp_rename 'dbo.logging', 'logging_old';")
            self.database.execute(
                """
                CREATE TABLE dbo.logging (
                    id INT NOT NULL PRIMARY KEY CONSTRAINT CK_logging_single_row CHECK (id = 1),
                    visit_count BIGINT NOT NULL CONSTRAINT DF_logging_visit_count DEFAULT (0)
                );
                """
            )
            self.database.execute(
                """
                INSERT INTO dbo.logging (id, visit_count)
                SELECT 1, COALESCE(MAX(visits), 0)
                FROM dbo.logging_old;
                """
            )
            self.database.execute("DROP TABLE dbo.logging_old;")
            return

        self.database.execute("ALTER TABLE logging RENAME TO logging_old")
        self.database.execute(
            """
            CREATE TABLE logging (
                id INTEGER NOT NULL PRIMARY KEY CHECK (id = 1),
                visit_count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.database.execute(
            """
            INSERT INTO logging (id, visit_count)
            SELECT 1, COALESCE(MAX(visits), 0)
            FROM logging_old
            """
        )
        self.database.execute("DROP TABLE logging_old")

    def increment_visits(self) -> int:
        """Increment the counter and return the updated visit total."""
        if self.database.backend == "azure_sql":
            self.database.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM dbo.logging
                    WHERE id = 1
                )
                BEGIN
                    INSERT INTO dbo.logging (id, visit_count)
                    VALUES (1, 0);
                END

                UPDATE dbo.logging
                SET visit_count = visit_count + 1
                WHERE id = 1;
                """
            )
        else:
            self.database.execute(
                """
                INSERT OR IGNORE INTO logging (id, visit_count)
                VALUES (1, 0)
                """
            )
            self.database.execute(
                """
                UPDATE logging
                SET visit_count = visit_count + 1
                WHERE id = 1
                """
            )

        return self.get_visit_count()

    def get_visit_count(self) -> int:
        """Return the current visit counter value."""
        if self.database.backend == "azure_sql":
            rows = self.database.query(
                """
                SELECT TOP 1 visit_count
                FROM dbo.logging
                WHERE id = 1
                """
            )
        else:
            rows = self.database.query(
                """
                SELECT visit_count
                FROM logging
                WHERE id = 1
                LIMIT 1
                """
            )

        if not rows:
            return 0
        return int(rows[0]["visit_count"])
