from sqlalchemy.orm import Session
from . import models, schemas


def get_user(session:Session, user_id:int):
    return session.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(session:Session, email:str):
    return session.query(models.User).filter(models.User.email == email).first()

def get_all_users(session:Session, skip: int=0, limit: int= 100):
    return session.query(models.User).offset(skip).limit(limit).all()

def get_all_posts(session:Session, skip: int=0, limit: int= 100):
    return session.query(models.Post).offset(skip).limit(limit).all()

def create_user_post(session:Session, post: schemas.Post):
    pass