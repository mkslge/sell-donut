from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.routes.rating_routes import get_rating_service


router = APIRouter(prefix="/avatar", tags=["avatar"])


@router.get("/{username}")
def avatar(username: str, request: Request) -> RedirectResponse:
    """Redirect a username to the Mineatar-rendered Minecraft head.

    Preconditions:
    - FastAPI has parsed `username` from the path.
    - App lifespan has attached the Mojang client and repository service
      dependencies.

    Postconditions:
    - A valid username produces a redirect to Mineatar using the account UUID.
    - Invalid or unknown usernames raise the same HTTP errors as rating routes.

    Explanation:
    The frontend can use this stable backend endpoint as an image source. If
    the avatar provider ever changes, only this route needs to be updated.
    """
    profile = get_rating_service(request).resolve_profile(username)
    return RedirectResponse(
        url=f"https://api.mineatar.io/face/{profile.uuid}?scale=32",
        status_code=307,
    )
