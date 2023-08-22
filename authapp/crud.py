from sqlalchemy.orm import Session
from . import models, schemas
from jose import jwt
from authapp.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
    JWT_REFRESH_SECRET_KEY,
    JWT_SECRET_KEY,
)


def get_user_by_id(session: Session, user_id: int):
    return session.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(session: Session, email: str):
    return session.query(models.User).filter(models.User.email == email).first()


def get_all_users(session: Session, skip: int = 0, limit: int = 100):
    return session.query(models.User).offset(skip).limit(limit).all()


def get_all_posts(session: Session, skip: int = 0, limit: int = 100):
    return session.query(models.Post).offset(skip).limit(limit).all()


def find_user(session: Session, dependancies):
    token = dependancies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload["sub"]
    existing_user = (
        session.query(models.User).filter(models.User.user_id == user_id).first()
    )
    return existing_user, user_id


def find_admin(session: Session, dependancies):
    token = dependancies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    is_admin = payload["access"]
    return is_admin


def get_post_by_id(session: Session, post_id: int):
    return session.query(models.Post).filter(models.Post.post_id == post_id).first()
