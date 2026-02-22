from app.businesses.models import Businesses
from app.dao.base import BaseDAO


class BusinessDAO(BaseDAO):
    model = Businesses
