from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI, version
from app.users.router import router as router_users
from app.businesses.router import router as router_businesses


app = FastAPI()

app.include_router(router_users)
app.include_router(router_businesses)

app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
)
