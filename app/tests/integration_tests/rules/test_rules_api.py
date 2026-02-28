import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_rules_admin(admin_client: AsyncClient):
    res = await admin_client.get("/rules")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) > 0

@pytest.mark.asyncio
async def test_get_rules_user_forbidden(ac: AsyncClient):
    await ac.post("/users/auth/register", json={
        "email": "hacker@example.com", "password": "pwd", "confirm_password": "pwd",
        "first_name": "H", "last_name": "A", "surname": "C"
    })
    res = await ac.get("/rules")
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_update_rule_admin(admin_client: AsyncClient):
    rules_res = await admin_client.get("/rules")
    first_rule_id = rules_res.json()[0]["id"]
    original_val = rules_res.json()[0]["read_p"]

    patch_res = await admin_client.patch(f"/rules/{first_rule_id}", json={
        "read_p": not original_val
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["read_p"] != original_val
