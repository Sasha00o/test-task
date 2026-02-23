from datetime import datetime
import uuid

from fastapi import Depends, Request, status
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsendException,
    TokenExpiredException,
    UserIsNotPresentException,
    UserInactiveException,
)
from app.businesses.dao import BusinessDAO


def get_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    token = request.cookies.get('businessAccessToken')

    if not token:
        raise TokenAbsendException

    return token


async def get_current_businesses(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.RANDOM_SECRET, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get('exp')
    if not expire or (int(expire) < int(datetime.utcnow().timestamp())):
        raise TokenExpiredException
    business_id: str = payload.get('sub')
    if not business_id:
        raise UserIsNotPresentException
    business = await BusinessDAO.find_by_id(uuid.UUID(business_id))
    if not business:
        raise UserIsNotPresentException
    if business.is_active is False:
        raise UserInactiveException

    return business
