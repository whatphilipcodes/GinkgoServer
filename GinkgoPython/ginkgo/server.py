from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ginkgo.api import frontend_routes, unreal_routes
from ginkgo.core.config import settings
from ginkgo.services.llm import llm_service
from ginkgo.services.seed import sync_seeds
from ginkgo.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Sync database seeds on startup."""
    sync_seeds()
    await llm_service.initialize()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(frontend_routes.router)
app.include_router(unreal_routes.router)

if settings.frontend_dist.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=settings.frontend_dist / "assets"),
        name="assets",
    )
    app.mount(
        "/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend"
    )
else:
    logger.warning(f"Frontend build directory not found at {settings.frontend_dist}")
    logger.warning(
        f"Run '{settings.frontend_build_command}' in {settings.frontend_dir} first."
    )
