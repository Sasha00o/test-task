from app.dao.base import BaseDAO
from app.rules.models import Rules, Resources, Roles


class RulesDAO(BaseDAO):
    model = Rules


class ResourcesDAO(BaseDAO):
    model = Resources


class RolesDAO(BaseDAO):
    model = Roles
