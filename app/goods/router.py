import uuid

from fastapi import APIRouter, Depends, Request, HTTPException

from app.exceptions import NotFoundException, InsufficientPermissionsException
from app.goods.dao import GoodsDAO
from app.goods.schemas import SProductCreate, SProductUpdate
from app.rules.dependencies import CheckUserPermission, CheckBusinessPermission

router = APIRouter(prefix='/goods',
                   tags=['Товары'])


@router.get('')
async def get_goods(request: Request):
    """
    Получение списка товаров.
    Доступно как обычным пользователям, так и бизнесу
    при наличии соответствующих прав на ресурс GOODS.
    """
    # Попробуем авторизовать как пользователя
    try:
        await CheckUserPermission("GOODS", "read_all_p")(request)
    except HTTPException as user_exc:
        # Если не получилось — пробуем как бизнес
        try:
            await CheckBusinessPermission("GOODS", "read_all_p")(request)
        except HTTPException:
            # Если ни как пользователь, ни как бизнес — отдаем первую ошибку
            raise user_exc

    goods = await GoodsDAO.find_all(is_active=True)
    return goods


@router.get('/{good_id}')
async def get_good_by_id(
    good_id: uuid.UUID,
    current_user=Depends(CheckUserPermission("GOODS", "read_p"))
):
    good = await GoodsDAO.find_by_id(good_id)
    if not good:
        raise NotFoundException
    return good


@router.post('', status_code=201)
async def create_good(
    product_data: SProductCreate,
    current_business=Depends(CheckBusinessPermission("GOODS", "create_p"))
):
    good = await GoodsDAO.add(
        title=product_data.title,
        description=product_data.description,
        price=product_data.price,
        owner_id=current_business.id
    )
    return good


@router.patch('/{good_id}')
async def update_good(
    good_id: uuid.UUID,
    product_data: SProductUpdate,
    current_business=Depends(CheckBusinessPermission("GOODS", "update_p"))
):
    good = await GoodsDAO.find_by_id(good_id)
    if not good:
        raise NotFoundException
    if good.owner_id != current_business.id:
        raise InsufficientPermissionsException

    update_data = product_data.model_dump(exclude_unset=True)
    if not update_data:
        return good
    good = await GoodsDAO.update_by_id(id=good_id, **update_data)
    return good


@router.patch('/{good_id}/toggle')
async def toggle_good_active(
    good_id: uuid.UUID,
    current_business=Depends(CheckBusinessPermission("GOODS", "update_p"))
):
    good = await GoodsDAO.find_by_id(good_id)
    if not good:
        raise NotFoundException
    if good.owner_id != current_business.id:
        raise InsufficientPermissionsException

    good = await GoodsDAO.update_by_id(id=good_id, is_active=not good.is_active)
    return good


@router.delete('/{good_id}', status_code=204)
async def delete_good(
    good_id: uuid.UUID,
    current_business=Depends(CheckBusinessPermission("GOODS", "delete_p"))
):
    good = await GoodsDAO.find_by_id(good_id)
    if not good:
        raise NotFoundException
    if good.owner_id != current_business.id:
        raise InsufficientPermissionsException

    await GoodsDAO.delete_by_id(id=good_id)
    return
