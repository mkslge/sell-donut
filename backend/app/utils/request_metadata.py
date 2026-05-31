from fastapi import Request


def submitter_fingerprint(request: Request) -> str:
    """Build a light client fingerprint from request metadata.

    Preconditions:
    - `request` is the incoming FastAPI request.

    Postconditions:
    - Returns a stable string that can be used for prototype rate limiting.
    """
    forwarded_for = request.headers.get("x-forwarded-for", "")
    real_ip = request.headers.get("x-real-ip", "")
    user_agent = request.headers.get("user-agent", "")

    return f"{forwarded_for.split(',')[0] or real_ip or 'unknown'}:{user_agent[:120]}"
