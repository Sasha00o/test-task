from fastapi import APIRouter, Response
from app.exceptions import IncorrectEmailOrPasswordException, UserInactiveException, UsersAlreadyExistsException
from app.users.dao import UsersDAO
from app.users.schemas import SUserLogin, SUserRegister
from fastapi import HTTPException, status
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.rules.dao import RolesDAO

router = APIRouter(prefix='/users',
                   tags=['Пользователи'])


@router.post('/register', status_code=201)
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


@router.post('/login')
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    if not user.is_active:
        raise UserInactiveException
    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie('accessToken', access_token, httponly=True)

    return {'ok': True}
