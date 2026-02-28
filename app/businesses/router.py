from fastapi import APIRouter, Response
from app.businesses.dao import BusinessDAO
from app.businesses.schemas import SBusinessRegister, SBusinessLogin
from app.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from app.rules.dao import RolesDAO
from app.users.auth import create_access_token, get_password_hash
from app.businesses.auth import authenticate_business
from app.rules.dependencies import CheckBusinessPermission
from app.businesses.dependencies import get_current_businesses
from fastapi import Depends


router = APIRouter(prefix='/businesses',
                   tags=['Бизнесы'])


@router.post('/auth/register')
async def create_businesses(response: Response, business_data: SBusinessRegister):
    """
    Регистрация нового бизнес-аккаунта.
    Проверяет, свободен ли логин (название), хэширует пароль и выдает куку авторизации.
    """
    business = await BusinessDAO.find_one_or_none(name=business_data.name)
    if business:
        if not business.is_active:
            await BusinessDAO.delete_by_id(id=business.id)
        else:
            raise UserAlreadyExistsException

    role = await RolesDAO.find_one_or_none(name='BUSINESS')
    hashed_password = get_password_hash(business_data.password)
    business = await BusinessDAO.add(
        name=business_data.name,
        password_hash=hashed_password,
        role_id=role.id
    )
    access_token = create_access_token(
        {'sub': str(business.id), 'type': 'business'})
    response.set_cookie('businessAccessToken', access_token, httponly=True)

    return access_token


@router.post('/auth/login')
async def login_businesses(response: Response, business_data: SBusinessLogin):
    """
    Авторизация бизнес-аккаунта.
    Проверяет данные логина/пароля и выдает куку с JWT-токеном.
    """
    business = await authenticate_business(business_data.name, business_data.password)
    if not business:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token(
        {'sub': str(business.id), 'type': 'business'})
    response.set_cookie('businessAccessToken', access_token, httponly=True)
    return access_token


@router.post('/auth/logout')
async def logout_business(response: Response):
    """
    Выход из бизнес-аккаунта.
    Удаляет куку с токеном авторизации.
    """
    response.delete_cookie('businessAccessToken')
    return {'ok': True}


@router.delete('/me', status_code=204)
async def delete_me(current_business=Depends(get_current_businesses)):
    """
    Удаление собственного бизнес-аккаунта (мягкое удаление).
    Переводит профиль в неактивный статус (is_active = False).
    """
    await BusinessDAO.delete_business_by_id(id=current_business.id)
    return
