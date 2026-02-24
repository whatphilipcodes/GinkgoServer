from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ginkgo.api import frontend_routes, unreal_routes
from ginkgo.core.config import settings
from ginkgo.services.inspector import inspector_service
from ginkgo.services.seed import sync_seeds
from ginkgo.utils.logger import get_logger
from ginkgo.utils.network import get_local_ip

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Server spin-up"""
    sync_seeds()
    await inspector_service.initialize()
    local_ip = get_local_ip()
    logger.critical(f"Launch successful! URL: http://{local_ip}:{settings.server_port}")
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
