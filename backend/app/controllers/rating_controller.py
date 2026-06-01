from app.schemas.rating_schemas import (
    RatingCreate,
    RatingResponse,
    RatingStatsResponse,
    SellerRatingsResponse,
    SellerSummaryResponse,
)
from app.services.rating_service import RatingService


def _rating_to_response(rating) -> RatingResponse:
    return RatingResponse.model_validate(
        {
            "id": rating.id,
            "seller_username": rating.seller_username,
            "outcome": rating.verdict,
            "trade_category": rating.item_type,
            "trade_description": rating.item_name or "",
            "quantity": rating.quantity,
            "price": rating.price,
            "currency": rating.currency,
            "review_text": rating.description or "",
            "evidence_url": rating.evidence_url,
            "reporter_username": rating.reporter_username,
            "created_at": rating.created_at,
        }
    )


def create_rating(
    username: str,
    payload: RatingCreate,
    service: RatingService,
    submitter_fingerprint: str,
) -> RatingResponse:
    """Create a rating and shape it for the API response.

    Preconditions:
    - `username` and `payload` are request inputs accepted by FastAPI.
    - `service` is initialized with a repository.

    Postconditions:
    - Invalid inputs propagate as service-layer HTTP errors.
    - Valid input returns a `RatingResponse` matching the public API contract.
    """
    rating = service.create_rating(
        username=username,
        payload=payload,
        submitter_fingerprint=submitter_fingerprint,
    )
    return _rating_to_response(rating)


def list_ratings(username: str, service: RatingService) -> SellerRatingsResponse:
    """Return all ratings for one seller in API response shape.

    Preconditions:
    - `username` is raw path input.
    - `service` is initialized with a repository.

    Postconditions:
    - Response includes a display username and zero or more ratings.
    - Domain objects are converted into Pydantic response models.
    """
    seller_username, ratings = service.list_ratings(username)
    return SellerRatingsResponse(
        sellerUsername=seller_username,
        ratings=[_rating_to_response(rating) for rating in ratings],
    )


def get_summary(username: str, service: RatingService) -> SellerSummaryResponse:
    """Return aggregate reputation summary for one seller.

    Preconditions:
    - `username` is raw path input.
    - `service` is initialized with a repository.

    Postconditions:
    - Response matches `SellerSummaryResponse`.
    - Sellers with no ratings return the `NO_DATA` summary shape.
    """
    summary = service.summarize_seller(username)
    return SellerSummaryResponse.model_validate(summary)


def list_recent_ratings(service: RatingService, limit: int = 8) -> list[RatingResponse]:
    """Return the newest ratings across all sellers."""
    return [_rating_to_response(rating) for rating in service.recent_ratings(limit=limit)]


def get_stats(service: RatingService) -> RatingStatsResponse:
    """Return global rating statistics for the landing page."""
    return RatingStatsResponse(totalRatings=service.total_ratings())
