from fastapi import FastAPI
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import logger
from app.models import user  # noqa: F401 — necesario para que SQLAlchemy registre el modelo antes de create_all
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RESTful API for user management with complete CRUD operations",
)

app.include_router(users.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "version": settings.app_version}
