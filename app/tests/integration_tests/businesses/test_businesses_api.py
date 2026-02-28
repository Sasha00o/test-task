import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("name,password,confirm_password,expected_status", [
    ("ShopA", "pass1", "pass1", 201),
    ("ShopA", "pass2", "pass2", 409),
    ("ShopB", "pass1", "mismatch", 422)
])
async def test_register_business(ac: AsyncClient, name, password, confirm_password, expected_status):
    response = await ac.post("/businesses/auth/register", json={
        "name": name,
        "password": password,
        "confirm_password": confirm_password
    })

    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_login_and_logout_business(ac: AsyncClient):
    await ac.post("/businesses/auth/register", json={
        "name": "ShopLogin", "password": "pwd", "confirm_password": "pwd"
    })
    ac.cookies.clear()
    login_res = await ac.post("/businesses/auth/login", json={
        "name": "ShopLogin", "password": "pwd"
    })
    assert login_res.status_code == 200
    assert "businessAccessToken" in login_res.cookies

    logout_res = await ac.post("/businesses/auth/logout")
    assert logout_res.status_code == 200
    assert not ac.cookies.get("businessAccessToken")
