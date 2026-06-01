from fastapi import APIRouter, Request

from app.repositories.logging_repository import LoggingRepository
from app.schemas.logging_schemas import LoggingResponse


router = APIRouter(prefix="/logging", tags=["logging"])


def get_logging_repository(request: Request) -> LoggingRepository:
    return request.app.state.logging_repository


@router.post("/visit", response_model=LoggingResponse)
def log_visit(request: Request) -> LoggingResponse:
    """Increment the site visit counter."""
    visit_count = get_logging_repository(request).increment_visits()
    return LoggingResponse(visits=visit_count)


@router.get("/visits", response_model=LoggingResponse)
def get_visits(request: Request) -> LoggingResponse:
    """Return the current site visit counter."""
    visit_count = get_logging_repository(request).get_visit_count()
    return LoggingResponse(visits=visit_count)
