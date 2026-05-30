import sqlite3
from datetime import datetime

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
    ) -> Rating:
        """Persist one rating and return the stored domain model.

        Preconditions:
        - `seller_username` has already passed Minecraft username validation.
        - `normalized_username` is the lowercase lookup key for that username.
        - `minecraft_uuid` came from Mojang's profile API.
        - `payload` has already passed API validation.

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
            verdict=payload.verdict,
            item_type=payload.item_type.strip().upper(),
            item_name=payload.item_name,
            quantity=payload.quantity,
            price=payload.price,
            currency=payload.currency,
            description=payload.description,
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
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                rating.created_at.isoformat(),
                rating.updated_at.isoformat(),
            ),
        )
        return rating

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

    def get_seller_by_uuid(self, minecraft_uuid: str) -> sqlite3.Row | None:
        """Return the seller row for a Mojang UUID.

        Preconditions:
        - `minecraft_uuid` came from Mojang's profile API.

        Postconditions:
        - Returns the seller row when the UUID has stored ratings.
        - Returns `None` when this account has no stored seller row.
        """
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

    def _row_to_rating(self, row: sqlite3.Row) -> Rating:
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
