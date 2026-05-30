from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import Database
from app.integrations.mojang_client import MojangProfileClient
from app.repositories.rating_repository import RatingRepository
from app.routes.avatar_routes import router as avatar_router
from app.routes.rating_routes import router as rating_router


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "selldonut.db"


def create_app(
    db_path: str | Path = DEFAULT_DB_PATH,
    mojang_client: MojangProfileClient | None = None,
) -> FastAPI:
    """Build and configure the FastAPI application.

    Preconditions:
    - `db_path` points to a SQLite database file location that the process can
      create or open.
    - `mojang_client`, when provided, implements Mojang profile lookup.

    Postconditions:
    - The returned app has rating routes registered.
    - During lifespan startup, the SQLite schema is initialized and a shared
      `RatingRepository` plus Mojang client are attached to `app.state`.

    Explanation:
    The app factory keeps production startup and tests using the same wiring
    while allowing tests to pass an isolated temporary database path.
    """
    database = Database(db_path)
    profile_client = mojang_client or MojangProfileClient()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Open app-scoped resources for the API process.

        Preconditions:
        - `database` has been constructed with the database path for this app.
        - `profile_client` has been constructed or injected.

        Postconditions:
        - Startup initializes the schema and exposes shared dependencies.
        - Shutdown closes the SQLite connection so file handles are not leaked.
        """
        database.initialize()
        app.state.rating_repository = RatingRepository(database)
        app.state.mojang_client = profile_client
        yield
        database.close()

    app = FastAPI(title="SellDonut API", version="0.1.0", lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return a stable 400 shape for Pydantic request validation failures.

        Preconditions:
        - FastAPI raised `RequestValidationError` while parsing path/query/body
          input.

        Postconditions:
        - The client receives `{"error": "<message>"}` instead of FastAPI's
          default `{"detail": [...]}` response.
        """
        first_error = exc.errors()[0] if exc.errors() else {}
        message = first_error.get("msg", "Invalid request.")
        return JSONResponse(status_code=400, content={"error": message})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Return a stable error envelope for deliberate HTTP failures.

        Preconditions:
        - Application code raised `HTTPException` with a client-facing message.

        Postconditions:
        - The original status code is preserved and the response body is shaped
          as `{"error": exc.detail}`.
        """
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        """Hide implementation details for unexpected server errors.

        Preconditions:
        - An unhandled exception escaped application code.

        Postconditions:
        - The client receives a generic 500 response without a stack trace.
        """
        return JSONResponse(status_code=500, content={"error": "Internal server error."})

    app.include_router(avatar_router)
    app.include_router(rating_router)
    return app


app = create_app()
