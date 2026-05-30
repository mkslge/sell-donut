from app.schemas.rating_schemas import (
    RatingCreate,
    RatingResponse,
    SellerRatingsResponse,
    SellerSummaryResponse,
)
from app.services.rating_service import RatingService


def create_rating(
    username: str,
    payload: RatingCreate,
    service: RatingService,
) -> RatingResponse:
    """Create a rating and shape it for the API response.

    Preconditions:
    - `username` and `payload` are request inputs accepted by FastAPI.
    - `service` is initialized with a repository.

    Postconditions:
    - Invalid inputs propagate as service-layer HTTP errors.
    - Valid input returns a `RatingResponse` matching the public API contract.
    """
    rating = service.create_rating(username=username, payload=payload)
    return RatingResponse.model_validate(rating.__dict__)


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
        ratings=[RatingResponse.model_validate(rating.__dict__) for rating in ratings],
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
