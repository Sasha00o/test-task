import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_marketplace_flow(ac: AsyncClient):
    """
    Complete flow for a marketplace operation.
    """
    bus_res = await ac.post("/businesses/auth/register", json={
        "name": "GlobalTech",
        "password": "strong",
        "confirm_password": "strong"
    })
    assert bus_res.status_code == 201
    
    good_res = await ac.post("/goods", json={
        "title": "Smartphone X",
        "description": "Latest model",
        "price": 999.0
    })
    assert good_res.status_code == 201
    good_id = good_res.json()["id"]

    await ac.post("/businesses/auth/logout")
    
    user_res = await ac.post("/users/auth/register", json={
        "email": "customer@tech.com",
        "password": "secure",
        "confirm_password": "secure",
        "first_name": "John",
        "last_name": "Doe",
        "surname": ""
    })
    assert user_res.status_code == 201
    
    view_res = await ac.get("/goods")
    assert view_res.status_code == 200
    goods = view_res.json()
    assert any(g["id"] == good_id for g in goods)
    
    order_res = await ac.post("/orders", json={
        "good_id": good_id,
        "quantity": 2,
        "delivery_address": "123 Main St"
    })
    assert order_res.status_code == 201
    assert order_res.json()["total_cost"] == 1998.0
