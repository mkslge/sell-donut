from fastapi import HTTPException

from app.integrations.mojang_client import (
    MinecraftProfile,
    MojangProfileClient,
    MojangProfileLookupError,
)
from app.models.rating import Rating, Verdict
from app.repositories.rating_repository import RatingRepository
from app.schemas.rating_schemas import RatingCreate
from app.services.reputation_service import calculate_reputation
from app.utils.usernames import normalize_username, validate_username
from app.validators.rating_validators import validate_rating_payload


class RatingService:
    """Business logic boundary for rating workflows.

    This layer owns validation orchestration, normalization, aggregate summary
    behavior, and calls into repositories for persistence.
    """

    def __init__(
        self,
        repository: RatingRepository,
        mojang_client: MojangProfileClient,
    ):
        """Create the service with its persistence dependency.

        Preconditions:
        - `repository` points at an initialized storage backend.
        - `mojang_client` can resolve Minecraft usernames to Mojang profiles.

        Postconditions:
        - Service methods can resolve account identity and read/write ratings.
        """
        self.repository = repository
        self.mojang_client = mojang_client

    def create_rating(
        self,
        username: str,
        payload: RatingCreate,
        submitter_fingerprint: str,
    ) -> Rating:
        """Validate and create a seller rating.

        Preconditions:
        - `username` is raw path input from the API.
        - `payload` is a parsed Pydantic request body.
        - `submitter_fingerprint` identifies the submitting client.

        Postconditions:
        - Invalid usernames or payloads raise `HTTPException`.
        - Valid input is resolved to a Mojang UUID and persisted as one rating.
        - Returns the created `Rating`.
        """
        profile = self._resolve_profile(username)
        seller_username = profile.username
        validated_payload = validate_rating_payload(payload)
        normalized_username = normalize_username(seller_username)

        if self.repository.has_recent_submission(submitter_fingerprint):
            raise HTTPException(
                status_code=429,
                detail="You can submit one rating every 1 minute in this prototype.",
            )

        return self.repository.create_rating(
            seller_username=seller_username,
            normalized_username=normalized_username,
            minecraft_uuid=profile.uuid,
            payload=validated_payload,
            submitter_fingerprint=submitter_fingerprint,
        )

    def list_ratings(self, username: str) -> tuple[str, list[Rating]]:
        """Return display username plus ratings for a seller.

        Preconditions:
        - `username` is raw path input from the API.

        Postconditions:
        - Invalid usernames raise `HTTPException`.
        - Ratings are looked up by Mojang UUID.
        - Returns an empty rating list when the seller has no reports.
        """
        profile = self._resolve_profile(username)
        seller = self.repository.get_seller_by_uuid(profile.uuid)

        if seller is None:
            return profile.username, []

        return profile.username, self.repository.list_ratings(str(seller["id"]))

    def summarize_seller(self, username: str) -> dict:
        """Calculate aggregate reputation data for one seller.

        Preconditions:
        - `username` is raw path input from the API.

        Postconditions:
        - Returned keys match `SellerSummaryResponse` field names.
        - Counts and percentages are derived from all ratings for the seller.
        - Sellers with no ratings return zero counts and `NO_DATA` reputation.

        Explanation:
        Summary calculation stays in the service because it combines repository
        data with business rules. The label itself is delegated to
        `calculate_reputation` so that thresholds can evolve independently.
        """
        seller_username, ratings = self.list_ratings(username)
        total = len(ratings)
        legit_count = sum(1 for rating in ratings if rating.verdict == Verdict.LEGIT)
        scammer_count = sum(1 for rating in ratings if rating.verdict == Verdict.SCAMMER)
        mixed_count = sum(1 for rating in ratings if rating.verdict == Verdict.MIXED)
        legit_percentage = round((legit_count / total) * 100) if total else 0

        return {
            "seller_username": seller_username,
            "total_ratings": total,
            "legit_count": legit_count,
            "scammer_count": scammer_count,
            "mixed_count": mixed_count,
            "legit_percentage": legit_percentage,
            "reputation": calculate_reputation(ratings),
        }

    def recent_ratings(self, limit: int = 8) -> list[Rating]:
        """Return the newest ratings across all sellers."""
        return self.repository.list_recent_ratings(limit=limit)

    def total_ratings(self) -> int:
        """Return the total number of ratings stored in the system."""
        return self.repository.count_ratings()

    def get_leaderboard(self, limit: int = 10) -> dict[str, list[dict]]:
        """Return top sellers by scam and legit report counts."""
        return self.repository.leaderboard(limit=limit)

    def resolve_profile(self, username: str) -> MinecraftProfile:
        """Expose Mojang identity resolution for other backend routes.

        Preconditions:
        - `username` is raw path input from the API.

        Postconditions:
        - Returns the resolved Mojang profile for a valid username.
        - Raises the same HTTP errors as the rating workflows.

        Explanation:
        The avatar route needs the stable UUID but does not need any rating
        database access. Exposing the resolver here keeps identity rules in one
        place instead of duplicating Mojang lookup behavior in routes.
        """
        return self._resolve_profile(username)

    def _resolve_profile(self, username: str) -> MinecraftProfile:
        """Validate a username and resolve it to Mojang account identity.

        Preconditions:
        - `username` is raw path input from the API.

        Postconditions:
        - Returns Mojang profile data for valid existing Minecraft accounts.
        - Raises `HTTPException(400)` for invalid or unknown usernames.
        - Raises `HTTPException(502)` when Mojang lookup is unavailable.

        Explanation:
        The application stores reputation by Mojang UUID so reports survive
        username changes. This private helper keeps that identity policy in one
        place for create, list, and summary workflows.
        """
        seller_username = validate_username(username)

        try:
            profile = self.mojang_client.lookup_profile(seller_username)
        except MojangProfileLookupError as exc:
            raise HTTPException(
                status_code=502,
                detail="Could not verify Minecraft username with Mojang.",
            ) from exc

        if profile is None:
            raise HTTPException(status_code=400, detail="Minecraft profile not found.")

        return profile
