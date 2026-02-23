from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI, version
from app.users.router import router as router_users
from app.businesses.router import router as router_businesses
from app.goods.router import router as router_goods
from app.rules.router import router as router_rules
from app.orders.router import router as router_orders


app = FastAPI()

app.include_router(router_users)
app.include_router(router_businesses)
app.include_router(router_goods)
app.include_router(router_rules)
app.include_router(router_orders)

app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
)
