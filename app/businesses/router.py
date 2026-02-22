from fastapi import APIRouter, Response
from app.businesses.dao import BusinessDAO
from app.businesses.schemas import SBusinessRegister, SBusinessLogin
from app.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from app.rules.dao import RolesDAO
from app.users.auth import create_access_token, get_password_hash
from app.businesses.auth import authenticate_business


router = APIRouter(prefix='/businesses',
                   tags=['Бизнесы'])


@router.post('/auth/register')
async def create_businesses(response: Response, business_data: SBusinessRegister):
    business = await BusinessDAO.find_one_or_none(name=business_data.name)
    if business:
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


@router.post('/auth/login')
async def login_businesses(response: Response, business_data: SBusinessLogin):
    business = await authenticate_business(business_data.name, business_data.password)
    if not business:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({'sub': str(business.id)})
    response.set_cookie('businessAccessToken', access_token, httponly=True)
    return access_token


@router.post('/auth/logout')
async def logout_business(response: Response):
    response.delete_cookie('businessAccessToken')
    return {'ok': True}
