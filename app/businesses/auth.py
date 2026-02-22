from app.businesses.dao import BusinessDAO
from app.users.auth import verify_password


async def authenticate_business(name: str, password: str):
    business = await BusinessDAO.find_one_or_none(name=name)
    if not business or not verify_password(password, business.password_hash):
        return
    return business
