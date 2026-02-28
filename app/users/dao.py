from sqlalchemy import update

from app.dao.base import BaseDAO
from app.users.models import Users
from app.database import async_session_maker
from app.exceptions import NotFoundException


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def delete_user_by_id(cls, id):
        async with async_session_maker() as session:
            stmt = (
                update(Users)
                .where(Users.id == id)
                .values(is_active=False)
            )

            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount == 0:
                raise NotFoundException
