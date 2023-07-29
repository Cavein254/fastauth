from sqlalchemy import Column, Integer, String,DateTime, Boolean,ForeignKey
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(250), nullable=False)
    admin = Column(Boolean, default=False)

class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer)
    access_token = Column(String(500), primary_key=True)
    refresh_token = Column(String(500), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)

class Post(Base):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True)
    author_id = Column(Integer(), ForeignKey('users.id'))
    title=Column(String, nullable=False)
    post=Column(String, nullable=False)
    published = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)