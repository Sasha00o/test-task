from pydantic import BaseModel, model_validator


class SBusinessRegister(BaseModel):
    name: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("password and confirm_password do not match")
        return self


class SBusinessLogin(BaseModel):
    name: str
    password: str
