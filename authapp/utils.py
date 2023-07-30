import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from functools import wraps


ACCESS_TOKEN_EXPIRE_MINUTES = 60 # 1 HOUR
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14 # 2 WEEKS
ALGORITHM = 'HS256'
JWT_SECRET_KEY= "^@&#*@))@nduwuhdb&*(3484370)&&@&@9439483482"
JWT_REFRESH_SECRET_KEY = "^@&#*@66###7372932947JSHFJSDALK"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password:str) -> str:
    return password_context.hash(password)

def verify_password(password:str, password_hash:str) -> bool:
    return password_context.verify(password, password_hash)

def create_access_token(subject: Union[str, Any],expires_delta: int = None, level_access: bool = False) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject), "access": level_access}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        payload = jwt.decode(kwargs['dependecies'], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload['sub']
        data = kwargs['session'].query[models.TokenTable].filter_by(user_id = user_id, access_token=kwargs['dependencies'], status=True).first()
        if data:
            return func(kwargs['dependencies'], kwargs['session'])
        else:
            return {"msg":"Token blocked"}
        
        return wrapper