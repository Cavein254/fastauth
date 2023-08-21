from pydantic import BaseModel, Field, EmailStr
import datetime


class User(BaseModel):
    username: str
    email: str
    admin: bool


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    admin: bool = Field(default=False)

    class Config:
        orm_mode = True


class requestdetails(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class changepassword(BaseModel):
    email: str
    old_password: str
    new_password: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime

    class Config:
        orm_mode = True


class Post(BaseModel):
    author_id: str
    title: str
    post: str

    class Config:
        orm_mode = True


class GetUser(BaseModel):
    username: str
    email: str
    admin: bool
    posts: list[Post]

    class Config:
        orm_mode = True
