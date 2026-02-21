from pydantic import BaseModel, EmailStr


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    surname: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str
