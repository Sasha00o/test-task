from sqlalchemy import update

from app.businesses.models import Businesses
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import NotFoundException


class BusinessDAO(BaseDAO):
    """
    Класс для работы с таблицей бизнесов в базе данных.
    """
    model = Businesses

    @classmethod
    async def delete_business_by_id(cls, id):
        """
        Мягкое удаление бизнеса: меняет статус is_active на False.
        """
        async with async_session_maker() as session:
            stmt = (
                update(Businesses)
                .where(Businesses.id == id)
                .values(is_active=False)
            )

            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount == 0:
                raise NotFoundException
