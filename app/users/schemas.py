from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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


class SUserUpdate(BaseModel):
    email: Optional[EmailStr | None]
    first_name: Optional[str | None]
    last_name: Optional[str | None]
    surname: Optional[str | None]


class SUserUpdateById(SUserUpdate):
    role: Optional[str | None] = Field(
        description='Оставьте поле пустым, если вы не ADMIN')
