from fastapi import APIRouter, Query, Request

import app.controllers.rating_controller as rating_controller
from app.integrations.mojang_client import MojangProfileClient
from app.repositories.rating_repository import RatingRepository
from app.schemas.rating_schemas import (
    LeaderboardResponse,
    RatingCreate,
    RatingResponse,
    RatingStatsResponse,
    SellerRatingsResponse,
    SellerSummaryResponse,
)
from app.services.rating_service import RatingService
from app.utils.request_metadata import submitter_fingerprint


router = APIRouter(prefix="/rating", tags=["ratings"])


def get_rating_service(request: Request) -> RatingService:
    """Build a request-local service from app-scoped dependencies.

    Preconditions:
    - App lifespan startup has attached `rating_repository` to `app.state`.

    Postconditions:
    - Returns a new lightweight `RatingService` for the current request.

    Explanation:
    The repository owns shared database access; the service is cheap to create
    per request and keeps route handlers free of business logic.
    """
    repository: RatingRepository = request.app.state.rating_repository
    mojang_client: MojangProfileClient = request.app.state.mojang_client
    return RatingService(repository=repository, mojang_client=mojang_client)


@router.get("/recent", response_model=list[RatingResponse])
def list_recent_ratings(request: Request, limit: int = 8) -> list[RatingResponse]:
    """Handle `GET /rating/recent`."""
    return rating_controller.list_recent_ratings(get_rating_service(request), limit=limit)


@router.get("/stats", response_model=RatingStatsResponse)
def get_stats(request: Request) -> RatingStatsResponse:
    """Handle `GET /rating/stats`."""
    return rating_controller.get_stats(get_rating_service(request))


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
) -> LeaderboardResponse:
    """Handle `GET /rating/leaderboard`."""
    return rating_controller.get_leaderboard(get_rating_service(request), limit=limit)


@router.post("/{username}", response_model=RatingResponse, status_code=201)
def create_rating(
    username: str,
    payload: RatingCreate,
    request: Request,
) -> RatingResponse:
    """Handle `POST /rating/{username}`.

    Preconditions:
    - FastAPI has parsed `username` and the JSON request body.

    Postconditions:
    - Returns HTTP 201 with the created rating on success.
    - Validation errors are returned by global exception handlers.
    """
    return rating_controller.create_rating(
        username=username,
        payload=payload,
        service=get_rating_service(request),
        submitter_fingerprint=submitter_fingerprint(request),
    )


@router.get("/{username}", response_model=SellerRatingsResponse)
def list_ratings(username: str, request: Request) -> SellerRatingsResponse:
    """Handle `GET /rating/{username}`.

    Preconditions:
    - FastAPI has parsed `username` from the path.

    Postconditions:
    - Returns the seller display username and all known ratings.
    - Unknown sellers return an empty ratings array.
    """
    return rating_controller.list_ratings(
        username=username,
        service=get_rating_service(request),
    )


@router.get("/{username}/summary", response_model=SellerSummaryResponse)
def get_summary(username: str, request: Request) -> SellerSummaryResponse:
    """Handle `GET /rating/{username}/summary`.

    Preconditions:
    - FastAPI has parsed `username` from the path.

    Postconditions:
    - Returns total counts, legit percentage, and reputation label.
    - Unknown sellers return a zero-count `NO_DATA` summary.
    """
    return rating_controller.get_summary(
        username=username,
        service=get_rating_service(request),
    )
