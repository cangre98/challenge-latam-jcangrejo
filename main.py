from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import logger
from app.models import user  # noqa: F401
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RESTful API for user management with complete CRUD operations",
    lifespan=lifespan,
)

app.include_router(users.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "version": settings.app_version}
