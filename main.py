from authApp import schemas, models
from authApp.database import Base,engine,SessionLocal
from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from authApp.auth_bearer import JWTBearer
from functools import wraps
from sqlalchemy.orm import Session
import datetime
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

@app.post('/logout')
def logout(dependancies=Depends(JWTBearer()), db:Session = Depends(get_session)):
    token = dependancies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(models.TokenTable).all()
    info = []
    for record in token_record:
        print("record", record)
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()
 
    existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_token == token).first()
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}
        
@app.post('/change-password')
def change_password(request:schemas.changepassword, db:Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password does not match")
    
    password_hash = get_hashed_password(request.new_password)
    user.password = password_hash
    db.commit()

    return {"message": "Password changed successfully", "payload":user}

@app.get('/getusers')
def getusers(dependancies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    users = session.query(models.User).all()
    return users

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
