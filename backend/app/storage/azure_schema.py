from __future__ import annotations


def initialize_azure_sql_schema(database) -> None:
    """Create the Azure SQL schema and indexes if they do not already exist."""
    database.execute(
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
    database.execute(
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
    database.execute(
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
    database.execute(
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
    database.execute(
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

    database.execute(
        """
        IF OBJECT_ID('dbo.logging', 'U') IS NULL
        BEGIN 
            CREATE TABLE dbo.logging (
                id INT NOT NULL PRIMARY KEY CONSTRAINT CK_logging_single_row CHECK (id = 1),
                visit_count BIGINT NOT NULL CONSTRAINT DF_logging_visit_count DEFAULT (0)
            );

            INSERT INTO dbo.logging (id, visit_count)
            VALUES (1, 0);
        END
        ELSE IF NOT EXISTS (
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
