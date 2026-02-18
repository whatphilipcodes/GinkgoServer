from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ginkgo.api import frontend_routes, unreal_routes
from ginkgo.core.config import settings

app = FastAPI()

# Include API routes
app.include_router(frontend_routes.router)
app.include_router(unreal_routes.router)

# Serve the built frontend from GinkgoFrontend/dist
if settings.frontend_dist.exists():
    # Serve static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=settings.frontend_dist / "assets"),
        name="assets",
    )
    # Serve the main HTML file for all other routes (SPA fallback)
    app.mount(
        "/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend"
    )
else:
    print(f"⚠️  Warning: Frontend build directory not found at {settings.frontend_dist}")
    print(
        f"   Run '{settings.frontend_build_command}' in {settings.frontend_dir} first."
    )
