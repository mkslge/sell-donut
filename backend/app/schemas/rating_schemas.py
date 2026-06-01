from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.rating import Reputation, Verdict


class RatingCreate(BaseModel):
    outcome: Verdict
    trade_category: Annotated[
        str,
        Field(alias="tradeCategory", min_length=1, max_length=60),
    ]
    trade_description: Annotated[
        str,
        Field(alias="tradeDescription", min_length=1, max_length=120),
    ]
    quantity: Annotated[int | None, Field(ge=1)] = None
    price: Annotated[float | None, Field(ge=0)] = None
    currency: Annotated[str | None, Field(max_length=32)] = None
    review_text: Annotated[
        str,
        Field(alias="reviewText", min_length=10, max_length=1000),
    ]
    evidence_url: Annotated[HttpUrl | None, Field(alias="evidenceUrl")] = None
    reporter_username: Annotated[
        str | None,
        Field(alias="reporterUsername", min_length=3, max_length=16),
    ] = None

    model_config = ConfigDict(populate_by_name=True)


class RatingResponse(BaseModel):
    id: str
    seller_username: str = Field(alias="sellerUsername")
    outcome: Verdict
    trade_category: str = Field(alias="tradeCategory")
    trade_description: str = Field(alias="tradeDescription")
    quantity: int | None = None
    price: float | None = None
    currency: str | None = None
    review_text: str = Field(alias="reviewText")
    evidence_url: str | None = Field(default=None, alias="evidenceUrl")
    reporter_username: str | None = Field(default=None, alias="reporterUsername")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class SellerRatingsResponse(BaseModel):
    seller_username: str = Field(alias="sellerUsername")
    ratings: list[RatingResponse]

    model_config = ConfigDict(populate_by_name=True)


class SellerSummaryResponse(BaseModel):
    seller_username: str = Field(alias="sellerUsername")
    total_ratings: int = Field(alias="totalRatings")
    legit_count: int = Field(alias="legitCount")
    scammer_count: int = Field(alias="scammerCount")
    mixed_count: int = Field(alias="mixedCount")
    legit_percentage: int = Field(alias="legitPercentage")
    reputation: Reputation

    model_config = ConfigDict(populate_by_name=True)


class RatingStatsResponse(BaseModel):
    total_ratings: int = Field(alias="totalRatings", ge=0)

    model_config = ConfigDict(populate_by_name=True)
