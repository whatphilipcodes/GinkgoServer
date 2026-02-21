from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ginkgo.api import frontend_routes, test_ui, unreal_routes
from ginkgo.core.config import settings
from ginkgo.services.llm_service import llm_service
from ginkgo.services.seed_service import sync_seeds


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Sync database seeds on startup."""
    sync_seeds()
    await llm_service.initialize()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(frontend_routes.router)
app.include_router(unreal_routes.router)

if settings.enable_test_ui:
    app.include_router(test_ui.router)

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
    print(f"⚠️  Warning: Frontend build directory not found at {settings.frontend_dist}")
    print(
        f"   Run '{settings.frontend_build_command}' in {settings.frontend_dir} first."
    )
