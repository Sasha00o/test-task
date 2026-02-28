import pytest
from httpx import AsyncClient


@pytest.fixture
async def env_setup(ac: AsyncClient):
    res = await ac.post("/businesses/auth/register", json={
        "name": "OrderBShop", "password": "pwd", "confirm_password": "pwd"
    })
    if res.status_code not in (200, 201):
        login_res = await ac.post("/businesses/auth/login", json={
            "name": "OrderBShop",
            "password": "pwd",
        })
        assert login_res.status_code == 200, login_res.text
    res = await ac.post("/goods", json={
        "title": "TV", "description": "4K", "price": 500.0
    })
    good_id = res.json()["id"]
    ac.cookies.clear()

    res_user = await ac.post("/users/auth/register", json={
        "email": "buyer@example.com", "password": "pwd", "confirm_password": "pwd",
        "first_name": "B", "last_name": "U", "surname": "Y"
    })
    if res_user.status_code not in (200, 201):
        login_res = await ac.post("/users/auth/login", json={
            "email": "buyer@example.com",
            "password": "pwd",
        })
        assert login_res.status_code == 200, login_res.text
    return ac, good_id


@pytest.mark.asyncio
async def test_create_order_user(env_setup):
    ac, good_id = env_setup

    res = await ac.post("/orders", json={
        "good_id": good_id,
        "quantity": 2,
        "delivery_address": "Home"
    })
    assert res.status_code == 201
    assert res.json()["total_cost"] == 1000.0


@pytest.mark.asyncio
async def test_create_order_business_forbidden(ac: AsyncClient):
    await ac.post("/businesses/auth/register", json={
        "name": "BadBiz", "password": "pwd", "confirm_password": "pwd"
    })
    res = await ac.post("/orders", json={
        "good_id": "00000000-0000-0000-0000-000000000000",
        "quantity": 1,
        "delivery_address": "Nowhere"
    })
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_get_my_orders(env_setup):
    ac, good_id = env_setup
    await ac.post("/orders", json={
        "good_id": good_id, "quantity": 1, "delivery_address": "Home"
    })

    res = await ac.get("/orders")
    assert res.status_code == 200
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_get_all_orders_admin(admin_client: AsyncClient):
    res = await admin_client.get("/orders/all")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
