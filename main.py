from authApp import schemas, models
from authApp.database import Base,engine,SessionLocal
from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth_bearer import JWTBearer
from functools import wraps
from sqlalchemy.orm import Session
from authApp.utils import get_hashed_password
from authApp.utils import ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,create_access_token,create_refresh_token, verify_password, get_hashed_password, JWT_REFRESH_SECRET_KEY, JWT_SECRET_KEY

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

app = FastAPI()


@app.post('/login')
def login(request:schemas.requestdetails, Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    password_hash = user.password
    if not verify_password(request.password, password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = models.TokenTable(user_id=user.id, access_token=access, refresh_token=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }

@app.post('/register')
def register_user(user:schemas.UserCreate, session:Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    password_hash = get_hashed_password(user.password)
    new_user = models.User(user=user.username, password=password_hash, email=user.email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {'msg':'user created successfully', 'payload': new_user}
