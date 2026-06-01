from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoggingResponse(BaseModel):
    visits: int = Field(alias="visits", ge=0)

    model_config = ConfigDict(populate_by_name=True)
