from authApp import schemas, models
from authApp.database import Base,engine,SessionLocal
from fastapi import FastAPI,Depends, HTTPException, status
from sqlalchemy.orm import Session
from authApp.utils import get_hashed_password

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

app = FastAPI()

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
