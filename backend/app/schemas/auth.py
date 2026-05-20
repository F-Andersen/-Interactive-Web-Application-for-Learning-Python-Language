from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    status: str
    role: RoleRead

    model_config = {"from_attributes": True}
