from pydantic import BaseModel, EmailStr
from pydantic.schema import datetime
from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostResponse(PostBase):
    id: int
    title: str
    content: str
    published: bool
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: str | None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
