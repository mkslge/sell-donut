from datetime import UTC, datetime, timedelta
from typing import Any

from app.database import Database
from app.models.rating import Rating, Verdict, new_id, now_utc
from app.schemas.rating_schemas import RatingCreate


class RatingRepository:
    """Persistence boundary for seller and rating records.

    Repository methods assume service-layer validation has already happened.
    They are responsible for database shape, SQL statements, and translating
    rows into domain models.
    """

    def __init__(self, database: Database):
        """Create a repository backed by the provided database wrapper.

        Preconditions:
        - `database.initialize()` will be called before request handling.

        Postconditions:
        - Repository methods will use the provided database connection.
        """
        self.database = database

    def create_rating(
        self,
        seller_username: str,
        normalized_username: str,
        minecraft_uuid: str,
        payload: RatingCreate,
        submitter_fingerprint: str,
    ) -> Rating:
        """Persist one rating and return the stored domain model.

        Preconditions:
        - `seller_username` has already passed Minecraft username validation.
        - `normalized_username` is the lowercase lookup key for that username.
        - `minecraft_uuid` came from Mojang's profile API.
        - `payload` has already passed API validation.
        - `submitter_fingerprint` identifies the submitting client for rate
          limiting.

        Postconditions:
        - A seller row exists for `minecraft_uuid`.
        - A rating row is inserted and linked to that seller.
        - The returned `Rating` matches the persisted values.

        Explanation:
        Creating a rating also upserts the seller. The seller is keyed by Mojang
        UUID rather than username so historical ratings follow account name
        changes.
        """
        timestamp = now_utc()
        seller_id = self._ensure_seller(
            seller_username=seller_username,
            normalized_username=normalized_username,
            minecraft_uuid=minecraft_uuid,
            timestamp=timestamp,
        )
        rating = Rating(
            id=new_id(),
            seller_username=seller_username,
            normalized_username=normalized_username,
            verdict=payload.outcome,
            item_type=payload.trade_category.strip().upper(),
            item_name=payload.trade_description,
            quantity=payload.quantity,
            price=payload.price,
            currency=payload.currency,
            description=payload.review_text,
            evidence_url=str(payload.evidence_url) if payload.evidence_url else None,
            reporter_username=payload.reporter_username,
            created_at=timestamp,
            updated_at=timestamp,
        )

        self.database.execute(
            """
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rating.id,
                seller_id,
                rating.seller_username,
                rating.normalized_username,
                rating.verdict.value,
                rating.item_type,
                rating.item_name,
                rating.quantity,
                rating.price,
                rating.currency,
                rating.description,
                rating.evidence_url,
                rating.reporter_username,
                submitter_fingerprint,
                rating.created_at.isoformat(),
                rating.updated_at.isoformat(),
            ),
        )
        return rating

    def has_recent_submission(self, submitter_fingerprint: str, minutes: int = 1) -> bool:
        """Return whether a fingerprint has submitted a rating recently."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        rows = self.database.query(
            """
            SELECT id
            FROM ratings
            WHERE submitterFingerprint = ?
              AND created_at >= ?
            """,
            (submitter_fingerprint, cutoff.isoformat()),
        )
        return bool(rows)

    def list_recent_ratings(self, limit: int = 8) -> list[Rating]:
        """Return the newest ratings across all sellers."""
        if self.database.backend == "azure_sql":
            rows = self.database.query(
                f"""
                SELECT TOP ({limit}) *
                FROM ratings
                ORDER BY created_at DESC
                """
            )
        else:
            rows = self.database.query(
                """
                SELECT *
                FROM ratings
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        return [self._row_to_rating(row) for row in rows]

    def count_ratings(self) -> int:
        """Return the total number of stored ratings."""
        rows = self.database.query(
            """
            SELECT COUNT(*) AS total_ratings
            FROM ratings
            """
        )
        if not rows:
            return 0
        return int(rows[0]["total_ratings"])

    def leaderboard(self, limit: int = 10) -> dict[str, list[dict[str, Any]]]:
        """Return top sellers by scam and legit report counts."""
        safe_limit = max(1, min(limit, 50))
        return {
            "scam": self._leaderboard_for_count("scam_count", safe_limit),
            "legit": self._leaderboard_for_count("legit_count", safe_limit),
        }

    def list_ratings(self, seller_id: str) -> list[Rating]:
        """Return all ratings for a seller id, newest first.

        Preconditions:
        - `seller_id` came from a seller row.

        Postconditions:
        - Returns an empty list if no ratings exist.
        - Every row is converted to a `Rating` domain object.
        """
        rows = self.database.query(
            """
            SELECT *
            FROM ratings
            WHERE seller_id = ?
            ORDER BY created_at DESC
            """,
            (seller_id,),
        )
        return [self._row_to_rating(row) for row in rows]

    def get_seller_by_uuid(self, minecraft_uuid: str) -> dict[str, Any] | None:
        """Return the seller row for a Mojang UUID.

        Preconditions:
        - `minecraft_uuid` came from Mojang's profile API.

        Postconditions:
        - Returns the seller row when the UUID has stored ratings.
        - Returns `None` when this account has no stored seller row.
        """
        if self.database.backend == "azure_sql":
            rows = self.database.query(
                """
                SELECT TOP 1 *
                FROM sellers
                WHERE minecraft_uuid = ?
                """,
                (minecraft_uuid,),
            )
        else:
            rows = self.database.query(
                """
                SELECT *
                FROM sellers
                WHERE minecraft_uuid = ?
                LIMIT 1
                """,
                (minecraft_uuid,),
            )
        if not rows:
            return None
        return rows[0]

    def _leaderboard_for_count(
        self,
        count_column: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        if count_column not in {"scam_count", "legit_count"}:
            raise ValueError("Unsupported leaderboard count column.")

        if self.database.backend == "azure_sql":
            rows = self.database.query(
                f"""
                SELECT TOP ({limit}) *
                FROM (
                    SELECT
                        s.seller_username,
                        s.normalized_username,
                        s.minecraft_uuid,
                        SUM(CASE WHEN r.verdict = 'SCAMMER' THEN 1 ELSE 0 END) AS scam_count,
                        SUM(CASE WHEN r.verdict = 'LEGIT' THEN 1 ELSE 0 END) AS legit_count,
                        SUM(CASE WHEN r.verdict = 'MIXED' THEN 1 ELSE 0 END) AS mixed_count,
                        COUNT(*) AS total_ratings
                    FROM sellers s
                    JOIN ratings r ON r.seller_id = s.id
                    GROUP BY
                        s.id,
                        s.seller_username,
                        s.normalized_username,
                        s.minecraft_uuid
                ) leaderboard
                WHERE {count_column} > 0
                ORDER BY {count_column} DESC, seller_username ASC
                """
            )
        else:
            rows = self.database.query(
                f"""
                SELECT *
                FROM (
                    SELECT
                        s.seller_username,
                        s.normalized_username,
                        s.minecraft_uuid,
                        SUM(CASE WHEN r.verdict = 'SCAMMER' THEN 1 ELSE 0 END) AS scam_count,
                        SUM(CASE WHEN r.verdict = 'LEGIT' THEN 1 ELSE 0 END) AS legit_count,
                        SUM(CASE WHEN r.verdict = 'MIXED' THEN 1 ELSE 0 END) AS mixed_count,
                        COUNT(*) AS total_ratings
                    FROM sellers s
                    JOIN ratings r ON r.seller_id = s.id
                    GROUP BY
                        s.id,
                        s.seller_username,
                        s.normalized_username,
                        s.minecraft_uuid
                ) leaderboard
                WHERE {count_column} > 0
                ORDER BY {count_column} DESC, seller_username ASC
                LIMIT ?
                """,
                (limit,),
            )

        return [self._leaderboard_row(row) for row in rows]

    def _leaderboard_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "seller_username": str(row["seller_username"]),
            "normalized_username": str(row["normalized_username"]),
            "minecraft_uuid": str(row["minecraft_uuid"]),
            "scam_count": int(row["scam_count"]),
            "legit_count": int(row["legit_count"]),
            "mixed_count": int(row["mixed_count"]),
            "total_ratings": int(row["total_ratings"]),
        }

    def _ensure_seller(
        self,
        seller_username: str,
        normalized_username: str,
        minecraft_uuid: str,
        timestamp: datetime,
    ) -> str:
        """Find or create the seller row for a Mojang account UUID.

        Preconditions:
        - `seller_username` is validated display input.
        - `normalized_username` is the stable case-insensitive lookup key.
        - `minecraft_uuid` came from Mojang's profile API.
        - `timestamp` is timezone-aware and generated by application code.

        Postconditions:
        - Returns the seller row id.
        - Existing sellers have username metadata and `updated_at` refreshed.
        - Missing sellers are inserted with Mojang UUID identity.

        Explanation:
        UUID lookup is primary, with normalized username as a legacy fallback so
        rows created before Mojang integration can be upgraded in place.
        """
        if self.database.backend == "azure_sql":
            existing = self.database.query(
                """
                SELECT TOP 1 id
                FROM sellers
                WHERE minecraft_uuid = ?
                """,
                (minecraft_uuid,),
            )
        else:
            existing = self.database.query(
                """
                SELECT id
                FROM sellers
                WHERE minecraft_uuid = ?
                LIMIT 1
                """,
                (minecraft_uuid,),
            )

        if not existing:
            if self.database.backend == "azure_sql":
                existing = self.database.query(
                    """
                    SELECT TOP 1 id
                    FROM sellers
                    WHERE normalized_username = ?
                    """,
                    (normalized_username,),
                )
            else:
                existing = self.database.query(
                    """
                    SELECT id
                    FROM sellers
                    WHERE normalized_username = ?
                    LIMIT 1
                    """,
                    (normalized_username,),
                )

        if existing:
            seller_id = str(existing[0]["id"])
            self.database.execute(
                """
                UPDATE sellers
                SET seller_username = ?,
                    normalized_username = ?,
                    minecraft_uuid = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    seller_username,
                    normalized_username,
                    minecraft_uuid,
                    timestamp.isoformat(),
                    seller_id,
                ),
            )
            return seller_id

        seller_id = new_id()
        self.database.execute(
            """
            INSERT INTO sellers (
                id,
                seller_username,
                normalized_username,
                minecraft_uuid,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                seller_id,
                seller_username,
                normalized_username,
                minecraft_uuid,
                timestamp.isoformat(),
                timestamp.isoformat(),
            ),
        )
        return seller_id

    def _row_to_rating(self, row: dict[str, Any]) -> Rating:
        """Convert a SQLite row into a typed `Rating` domain object.

        Preconditions:
        - `row` came from the `ratings` table and includes all rating columns.

        Postconditions:
        - String enum values are converted back into `Verdict`.
        - ISO timestamp strings are converted back into `datetime` objects.
        """
        return Rating(
            id=str(row["id"]),
            seller_username=str(row["seller_username"]),
            normalized_username=str(row["normalized_username"]),
            verdict=Verdict(str(row["verdict"])),
            item_type=str(row["item_type"]),
            item_name=row["item_name"],
            quantity=row["quantity"],
            price=row["price"],
            currency=row["currency"],
            description=row["description"],
            evidence_url=row["evidence_url"],
            reporter_username=row["reporter_username"],
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
        )
