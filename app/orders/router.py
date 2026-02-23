import uuid

from fastapi import APIRouter, Depends

from app.exceptions import NotFoundException
from app.goods.dao import GoodsDAO
from app.orders.dao import OrdersDAO
from app.orders.schemas import SOrderCreate
from app.rules.dependencies import CheckUserPermission

router = APIRouter(prefix='/orders',
                   tags=['Заказы'])


@router.post('', status_code=201)
async def create_order(
    order_data: SOrderCreate,
    current_user=Depends(CheckUserPermission("ORDERS", "create_p"))
):
    good = await GoodsDAO.find_by_id(order_data.good_id)
    if not good:
        raise NotFoundException
    if not good.is_active:
        raise NotFoundException

    total_cost = good.price * order_data.quantity

    order = await OrdersDAO.add(
        user_id=current_user.id,
        good_id=order_data.good_id,
        quantity=order_data.quantity,
        total_cost=total_cost,
        delivery_address=order_data.delivery_address
    )
    return order


@router.get('')
async def get_orders(
    current_user=Depends(CheckUserPermission("ORDERS", "read_p"))
):
    orders = await OrdersDAO.find_all(user_id=current_user.id)
    return orders


@router.get('/all')
async def get_all_orders(
    current_user=Depends(CheckUserPermission("ORDERS", "read_all_p"))
):
    orders = await OrdersDAO.find_all()
    return orders
