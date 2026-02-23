from app.dao.base import BaseDAO
from app.goods.models import Goods


class GoodsDAO(BaseDAO):
    model = Goods
