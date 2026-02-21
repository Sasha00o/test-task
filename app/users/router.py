import uuid

from fastapi import APIRouter, Depends, Response
from app.exceptions import IncorrectEmailOrPasswordException, NotFoundException, UserInactiveException, UsersAlreadyExistsException, InsufficientPermissionsException
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SUserLogin, SUserRegister, SUserUpdate, SUserUpdateById
from fastapi import HTTPException, status
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.rules.dao import RolesDAO

router = APIRouter(prefix='/users',
                   tags=['Пользователи'])


@router.post('/auth/register', status_code=201)
async def register_user(response: Response, user_data: SUserRegister):
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UsersAlreadyExistsException

    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='Пароли не совпадают')

    role = await RolesDAO.find_one_or_none(name='USER')

    hashed_password = get_password_hash(user_data.password)
    user = await UsersDAO.add(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        surname=user_data.surname,
        role_id=role.id
    )
    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie('accessToken', access_token, httponly=True)

    return {'ok': True}


@router.post('/auth/login')
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    if not user.is_active:
        raise UserInactiveException
    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie('accessToken', access_token, httponly=True)

    return {'ok': True}


@router.post('/auth/logout')
async def logout_users(response: Response):
    response.delete_cookie('booking_access_token')
    return {'ok': True}


@router.get('/me')
async def get_users_me(current_user: Users = Depends(
        get_current_user)):
    return current_user


@router.patch('/me')
async def update_users_me(user_data: SUserUpdate,
                          current_user: Users = Depends(get_current_user)):
    user = await UsersDAO.update_by_id(id=current_user.id,
                                       email=user_data.email,
                                       first_name=user_data.first_name,
                                       last_name=user_data.last_name,
                                       surname=user_data.surname,
                                       )
    return user


@router.get('/{id}')
async def get_user_by_id(
    id: uuid.UUID,
    current_user: Users = Depends(get_current_user)
):
    role = await RolesDAO.find_by_id(current_user.role_id)
    if role.name != 'ADMIN' and id != current_user.id:
        raise InsufficientPermissionsException
    user = await UsersDAO.find_one_or_none(id=id)
    if not user:
        raise NotFoundException

    return user


@router.patch('/{id}')
async def update_user_by_id(
    id: uuid.UUID,
    user_data: SUserUpdateById,
    current_user: Users = Depends(get_current_user)
):
    role = await RolesDAO.find_by_id(current_user.role_id)
    if role.name != 'ADMIN' and id != current_user.id:
        raise InsufficientPermissionsException
    if user_data.role:
        if role.name != 'ADMIN':
            raise InsufficientPermissionsException
    user = await UsersDAO.find_one_or_none(id=id)
    if not user:
        raise NotFoundException

    user = await UsersDAO.update_by_id(id=id,
                                       email=user_data.email,
                                       first_name=user_data.first_name,
                                       last_name=user_data.last_name,
                                       surname=user_data.surname,
                                       )
    return user


@router.delete('/{id}', status_code=204)
async def delete_user(
    id: uuid.UUID,
    current_user: Users = Depends(get_current_user)
):
    role = await RolesDAO.find_by_id(current_user.role_id)
    if role.name != 'ADMIN':
        raise InsufficientPermissionsException
    await UsersDAO.delete_user_by_id(id=id)
    return
