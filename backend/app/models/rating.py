from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class Verdict(StrEnum):
    LEGIT = "LEGIT"
    SCAMMER = "SCAMMER"


class Reputation(StrEnum):
    NO_DATA = "NO_DATA"
    LEGIT = "LEGIT"
    MOSTLY_LEGIT = "MOSTLY_LEGIT"
    MIXED = "MIXED"
    RISKY = "RISKY"
    SCAMMER = "SCAMMER"


@dataclass(frozen=True)
class Rating:
    """Immutable domain representation of a persisted trade rating.

    Preconditions:
    - Values come from validated request data or trusted database rows.

    Postconditions:
    - Callers receive a read-only object that cannot be accidentally mutated
      while response data is being assembled.
    """

    id: str
    seller_username: str
    normalized_username: str
    verdict: Verdict
    item_type: str
    item_name: str | None
    quantity: int | None
    price: float | None
    currency: str | None
    description: str | None
    evidence_url: str | None
    reporter_username: str | None
    created_at: datetime
    updated_at: datetime


def new_id() -> str:
    """Generate a public-safe unique id for domain records.

    Preconditions:
    - None.

    Postconditions:
    - Returns a UUID4 string suitable for primary-key usage in this prototype.
    """
    return str(uuid4())


def now_utc() -> datetime:
    """Return the current time as a timezone-aware UTC datetime.

    Preconditions:
    - System clock is available.

    Postconditions:
    - Returned datetime includes UTC timezone information.
    """
    return datetime.now(UTC)
