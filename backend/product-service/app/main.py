import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app.controller.product_controller import router as product_router
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Microservice API",
    description="Handles product catalog management, supplier submissions and Data Steward approvals.",
    version="1.0.0",
)

# allow_origins=["*"] combined with allow_credentials=True is an invalid
# combination per the CORS spec — browsers silently reject credentialed
# requests against a wildcard origin. List explicit origins instead;
# override via the ALLOWED_ORIGINS env var (comma-separated) once you
# know your deployed frontend's real URL.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:9000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "Handled application exception: %s (status %s) on %s %s",
        exc.message, exc.status_code, request.method, request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
def readiness_check():
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception:
        logger.exception("Readiness check failed — database unreachable")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "detail": "Database unreachable"},
        )

    return {"status": "ready"}


app.include_router(product_router)