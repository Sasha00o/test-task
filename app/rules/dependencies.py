from fastapi import Depends, Request

from app.exceptions import InsufficientPermissionsException, TokenAbsendException
from app.rules.dao import RulesDAO, ResourcesDAO
from app.users.dependencies import get_current_user
from app.businesses.dependencies import get_current_businesses


class CheckUserPermission:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    async def __call__(self, request: Request):
        # Проверяем: есть ли хоть какой-то токен?
        user_token = request.cookies.get('userAccessToken')
        business_token = request.cookies.get('businessAccessToken')
        auth_header = request.headers.get("Authorization")

        if not user_token and not auth_header:
            # Пользователь не залогинен вообще
            if business_token:
                # Но залогинен как бизнес → 403
                raise InsufficientPermissionsException
            raise TokenAbsendException

        # Получаем пользователя стандартным способом
        current_user = await get_current_user(
            token=user_token or auth_header.split(" ")[1]
        )

        resource = await ResourcesDAO.find_one_or_none(name=self.resource)
        if not resource:
            raise InsufficientPermissionsException

        rule = await RulesDAO.find_one_or_none(
            role_id=current_user.role_id,
            resource_id=resource.id
        )
        if not rule or not getattr(rule, self.action, False):
            raise InsufficientPermissionsException

        return current_user


class CheckBusinessPermission:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    async def __call__(self, request: Request):
        # Проверяем: есть ли хоть какой-то токен?
        business_token = request.cookies.get('businessAccessToken')
        user_token = request.cookies.get('userAccessToken')
        auth_header = request.headers.get("Authorization")

        if not business_token and not auth_header:
            # Бизнес не залогинен
            if user_token:
                # Но залогинен как обычный юзер → 403
                raise InsufficientPermissionsException
            raise TokenAbsendException

        # Получаем бизнес стандартным способом
        current_business = await get_current_businesses(
            token=business_token or auth_header.split(" ")[1]
        )

        resource = await ResourcesDAO.find_one_or_none(name=self.resource)
        if not resource:
            raise InsufficientPermissionsException

        rule = await RulesDAO.find_one_or_none(
            role_id=current_business.role_id,
            resource_id=resource.id
        )
        if not rule or not getattr(rule, self.action, False):
            raise InsufficientPermissionsException

        return current_business
