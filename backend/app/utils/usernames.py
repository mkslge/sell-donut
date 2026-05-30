import re

from fastapi import HTTPException


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,16}$")


def normalize_username(username: str) -> str:
    """Return the case-insensitive lookup key for a Minecraft username.

    Preconditions:
    - `username` is a string from the caller.

    Postconditions:
    - Leading/trailing whitespace is removed.
    - The result is lowercase for stable database lookup.
    """
    return username.strip().lower()


def validate_username(username: str) -> str:
    """Validate and trim a Minecraft username.

    Preconditions:
    - `username` is raw user input from a path parameter or equivalent source.

    Postconditions:
    - Returns the trimmed username when it matches Minecraft username format.
    - Raises `HTTPException(400)` with a client-facing message when invalid.

    Explanation:
    Validation preserves display casing, while `normalize_username` handles the
    separate database lookup key. Keeping those separate prevents accidental
    lowercasing in API responses.
    """
    if not username or not username.strip():
        raise HTTPException(status_code=400, detail="Seller username is required.")

    trimmed = username.strip()
    if not USERNAME_PATTERN.fullmatch(trimmed):
        raise HTTPException(
            status_code=400,
            detail="Seller username must be 3-16 letters, numbers, or underscores.",
        )

    return trimmed
