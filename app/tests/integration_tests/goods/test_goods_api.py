import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_business(ac: AsyncClient):

    res = await ac.post("/businesses/auth/register", json={
        "name": "BTest", "password": "pwd", "confirm_password": "pwd"
    })
    if res.status_code not in (200, 201):
        login_res = await ac.post("/businesses/auth/login", json={
            "name": "BTest",
            "password": "pwd",
        })
        assert login_res.status_code == 200, login_res.text
    return ac


@pytest.fixture
async def auth_user(ac: AsyncClient):

    res = await ac.post("/users/auth/register", json={
        "email": "utest@example.com", "password": "pwd", "confirm_password": "pwd",
        "first_name": "U", "last_name": "T", "surname": "S"
    })
    if res.status_code not in (200, 201):
        login_res = await ac.post("/users/auth/login", json={
            "email": "utest@example.com",
            "password": "pwd",
        })
        assert login_res.status_code == 200, login_res.text
    return ac


@pytest.mark.asyncio
async def test_create_good_business(auth_business: AsyncClient):
    res = await auth_business.post("/goods", json={
        "title": "Laptop", "description": "Gaming", "price": 1000.0
    })
    assert res.status_code == 201
    assert res.json()["title"] == "Laptop"


@pytest.mark.asyncio
async def test_create_good_user_forbidden(auth_user: AsyncClient):
    res = await auth_user.post("/goods", json={
        "title": "Hack", "description": "Try", "price": 1.0
    })
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_get_goods_user(auth_user: AsyncClient):
    res = await auth_user.get("/goods")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_get_goods_business(auth_business: AsyncClient):
    res = await auth_business.get("/goods")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_update_and_delete_good(auth_business: AsyncClient):
    post_res = await auth_business.post("/goods", json={
        "title": "Mouse", "description": "Wireless", "price": 50.0
    })
    good_id = post_res.json()["id"]

    patch_res = await auth_business.patch(f"/goods/{good_id}", json={
        "price": 45.0
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["price"] == 45.0

    toggle_res = await auth_business.patch(f"/goods/{good_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] == False

    del_res = await auth_business.delete(f"/goods/{good_id}")
    assert del_res.status_code == 204
