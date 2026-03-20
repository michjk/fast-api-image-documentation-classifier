from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.database import Base, engine
from app.groups.router import router as groups_router
from app.images.router import router as images_router
from app.jobs.router import router as jobs_router
from app.models import Group, Image, Job, User


def create_app() -> FastAPI:
    app = FastAPI(title="Image Documentation Classifier", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    app.include_router(groups_router, prefix="/api/v1")
    app.include_router(images_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
