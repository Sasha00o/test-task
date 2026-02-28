import uuid

from fastapi import APIRouter, Depends, Response
from app.exceptions import IncorrectEmailOrPasswordException, NotFoundException, UserInactiveException, UserAlreadyExistsException, InsufficientPermissionsException
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SUserLogin, SUserRegister, SUserUpdate, SUserUpdateById
from fastapi import HTTPException, status
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.rules.dao import RolesDAO
from app.rules.dependencies import CheckUserPermission

router = APIRouter(prefix='/users',
                   tags=['Пользователи'])


@router.post('/auth/register', status_code=201)
async def register_user(response: Response, user_data: SUserRegister):
    """
    Регистрация нового пользователя.
    Проверяет существование email, хэширует пароль и выдает JWT куку.
    """
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        if not existing_user.is_active:
            await UsersDAO.delete_by_id(existing_user.id)
        else:
            raise UserAlreadyExistsException

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
    access_token = create_access_token({'sub': str(user.id), 'type': 'user'})
    response.set_cookie('userAccessToken', access_token, httponly=True)

    return {'ok': True}


@router.post('/auth/login')
async def login_user(response: Response, user_data: SUserLogin):
    """
    Авторизация пользователя.
    Проверяет email и пароль, выдает авторизационную куку.
    """
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    if not user.is_active:
        raise UserInactiveException
    access_token = create_access_token({'sub': str(user.id), 'type': 'user'})
    response.set_cookie('userAccessToken', access_token, httponly=True)

    return {'ok': True}


@router.post('/auth/logout')
async def logout_users(response: Response):
    """
    Выход из аккаунта пользователя.
    Очищает куку с JWT-токеном.
    """
    response.delete_cookie('userAccessToken')
    return {'ok': True}


@router.get('/me')
async def get_users_me(current_user: Users = Depends(
        get_current_user)):
    """
    Получение данных текущего авторизованного пользователя.
    """
    return current_user


@router.patch('/me')
async def update_users_me(user_data: SUserUpdate,
                          current_user: Users = Depends(get_current_user)):
    """
    Частичное обновление данных своего профиля (имя, фамилия и т.д.).
    """
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        return current_user
    user = await UsersDAO.update_by_id(id=current_user.id, **update_data)
    return user


@router.get('/{id}')
async def get_user_by_id(
    id: uuid.UUID,
    current_user=Depends(CheckUserPermission("USERS", "read_all_p"))
):
    user = await UsersDAO.find_one_or_none(id=id)
    if not user:
        raise NotFoundException
    return user


@router.patch('/{id}')
async def update_user_by_id(
    id: uuid.UUID,
    user_data: SUserUpdateById,
    current_user=Depends(CheckUserPermission("USERS", "update_all_p"))
):
    user = await UsersDAO.find_one_or_none(id=id)
    if not user:
        raise NotFoundException
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        return user
    user = await UsersDAO.update_by_id(id=id, **update_data)
    return user


@router.delete('/me', status_code=204)
async def delete_me(current_user=Depends(CheckUserPermission("USERS", 'delete_p'))):
    """
    Удаление собственного аккаунта (мягкое удаление).
    Пользователь больше не сможет войти (is_active = False).
    """
    await UsersDAO.delete_user_by_id(id=current_user.id)
    return


@router.delete('/{id}', status_code=204)
async def delete_user(
    id: uuid.UUID,
    current_user=Depends(CheckUserPermission("USERS", "delete_all_p"))
):
    await UsersDAO.delete_user_by_id(id=id)
    return
