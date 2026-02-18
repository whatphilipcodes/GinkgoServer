from fastapi import FastAPI

from ginkgo.api import frontend_routes, unreal_routes

app = FastAPI()

app.include_router(frontend_routes.router)
app.include_router(unreal_routes.router)
