import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("email,password,confirm_password,expected_status", [
    ("newuser@example.com", "pass123", "pass123", 201),
    ("fail@example.com", "pass123", "wrong", 422),
    ("admin@admin.com", "newpass", "newpass", 409)
])
async def test_register_user(ac: AsyncClient, email, password, confirm_password, expected_status):
    response = await ac.post("/users/auth/register", json={
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "first_name": "Test",
        "last_name": "User",
        "surname": "Standard"
    })

    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize("email,password,expected_status", [
    ("newuser@example.com", "pass123", 200),
    ("newuser@example.com", "wrongpass", 401),
    ("ghost@example.com", "pass123", 401)
])
async def test_login_user(ac: AsyncClient, email, password, expected_status):
    response = await ac.post("/users/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == expected_status
    if expected_status == 200:
        assert "userAccessToken" in response.cookies


@pytest.mark.asyncio
async def test_get_me(ac: AsyncClient):
    await ac.post("/users/auth/register", json={
        "email": "me@example.com",
        "password": "pwd", "confirm_password": "pwd",
        "first_name": "Me", "last_name": "Myself", "surname": "I"
    })
    res = await ac.get("/users/me")
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_update_me(ac: AsyncClient):
    await ac.post("/users/auth/register", json={
        "email": "upd@example.com", "password": "pwd", "confirm_password": "pwd",
        "first_name": "Old", "last_name": "Name", "surname": "Sure"
    })
    res = await ac.patch("/users/me", json={"first_name": "NewName"})
    assert res.status_code == 200
    assert res.json()["first_name"] == "NewName"


@pytest.mark.asyncio
async def test_logout(ac: AsyncClient):
    await ac.post("/users/auth/register", json={
        "email": "out@example.com", "password": "pwd", "confirm_password": "pwd",
        "first_name": "Old", "last_name": "Name", "surname": "Sure"
    })
    res = await ac.post("/users/auth/logout")
    assert res.status_code == 200
    res2 = await ac.get("/users/me")
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id_admin_access(admin_client: AsyncClient):
    me = await admin_client.get("/users/me")
    admin_id = me.json()["id"]

    res = await admin_client.get(f"/users/{admin_id}")
    assert res.status_code == 200
    assert res.json()["email"] == "admin@admin.com"
