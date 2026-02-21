from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI, version
from app.users.router import router as router_users

app = FastAPI()

app.include_router(router_users)

app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
)
