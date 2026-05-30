from dataclasses import dataclass

import httpx


MOJANG_PROFILE_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"


class MojangProfileLookupError(RuntimeError):
    """Raised when Mojang profile lookup cannot be completed."""


@dataclass(frozen=True)
class MinecraftProfile:
    """Resolved Mojang identity for a Minecraft account."""

    uuid: str
    username: str


class MojangProfileClient:
    """Client for resolving Minecraft usernames through Mojang's public API."""

    def __init__(self, timeout_seconds: float = 5.0):
        """Create a Mojang API client.

        Preconditions:
        - `timeout_seconds` is positive and low enough for an API request path.

        Postconditions:
        - The client can perform bounded HTTP lookups against Mojang.
        """
        self.timeout_seconds = timeout_seconds

    def lookup_profile(self, username: str) -> MinecraftProfile | None:
        """Resolve a Minecraft username to Mojang's stable account UUID.

        Preconditions:
        - `username` has already passed Minecraft username format validation.

        Postconditions:
        - Returns `MinecraftProfile` when Mojang has an account for the name.
        - Returns `None` when Mojang reports no profile for the name.
        - Raises `MojangProfileLookupError` when the API cannot be reached or
          returns an unexpected response.

        Explanation:
        Usernames can change, so seller reputation must be keyed by Mojang's
        stable UUID. The API returns UUIDs without hyphens; this backend stores
        the exact Mojang value so future lookups compare consistently.
        """
        try:
            response = httpx.get(
                MOJANG_PROFILE_URL.format(username=username),
                timeout=self.timeout_seconds,
            )
        except httpx.HTTPError as exc:
            raise MojangProfileLookupError("Mojang profile lookup failed.") from exc

        if response.status_code in {204, 404}:
            return None

        if response.status_code != 200:
            raise MojangProfileLookupError("Mojang profile lookup returned an error.")

        data = response.json()
        profile_id = data.get("id")
        profile_name = data.get("name")

        if not isinstance(profile_id, str) or not isinstance(profile_name, str):
            raise MojangProfileLookupError("Mojang profile response was invalid.")

        return MinecraftProfile(uuid=profile_id, username=profile_name)
