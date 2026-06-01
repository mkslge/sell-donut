from app.models.rating import Rating, Reputation, Verdict


def calculate_reputation(ratings: list[Rating]) -> Reputation:
    """Convert a seller's rating history into a simple reputation label.

    Preconditions:
    - `ratings` contains all known ratings for the seller.
    - Each rating verdict is `LEGIT`, `SCAMMER`, or `MIXED`.

    Postconditions:
    - Returns exactly one `Reputation` enum value.
    - Empty rating history returns `NO_DATA`.

    Explanation:
    The thresholds are intentionally simple for the prototype. Keeping them in
    one pure function makes the reputation policy easy to test and change later
    without touching route, database, or response-shaping code.
    """
    total = len(ratings)
    if total == 0:
        return Reputation.NO_DATA
    

    scammer_count = 0
    legit_count = 0

    for rating in ratings:
        if rating.verdict == Verdict.SCAMMER:
            scammer_count += 1
        elif rating.verdict == Verdict.LEGIT:
            legit_count += 1

    legit_percentage = round((legit_count / total) * 100)

    if total >= 3 and scammer_count == total:
        return Reputation.SCAMMER
    if legit_percentage >= 90:
        return Reputation.LEGIT
    if legit_percentage >= 70:
        return Reputation.MOSTLY_LEGIT
    if legit_percentage >= 45:
        return Reputation.MIXED
    return Reputation.RISKY
