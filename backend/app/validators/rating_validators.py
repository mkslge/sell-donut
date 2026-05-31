from fastapi import HTTPException

from app.schemas.rating_schemas import RatingCreate


def validate_rating_payload(payload: RatingCreate) -> RatingCreate:
    """Apply rating validation that is easier to read outside Pydantic fields.

    Preconditions:
    - `payload` has already been parsed into `RatingCreate`.

    Postconditions:
    - Returns the same payload when it satisfies business validation.
    - Raises `HTTPException(400)` for invalid business values.

    Explanation:
    Pydantic handles most structural validation. This function is the place for
    business rules that should remain explicit and reusable by services.
    """
    if not payload.trade_category.strip():
        raise HTTPException(status_code=400, detail="tradeCategory is required.")

    if not payload.trade_description.strip():
        raise HTTPException(status_code=400, detail="tradeDescription is required.")

    if not payload.review_text.strip():
        raise HTTPException(status_code=400, detail="reviewText is required.")

    if payload.quantity is not None and payload.quantity < 1:
        raise HTTPException(status_code=400, detail="quantity must be at least 1.")

    if payload.price is not None and payload.price < 0:
        raise HTTPException(status_code=400, detail="price cannot be negative.")

    return payload
