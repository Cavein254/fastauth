from authapp import schemas, models, crud
from authapp.database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from authapp.auth_bearer import JWTBearer
from functools import wraps
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from authapp.database import SessionLocal, engine
from authapp.utils import get_hashed_password
from starlette.middleware.cors import CORSMiddleware
from authapp.dbinitializer import get_session


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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"msg": "welcome to your homepage!"}


@app.get("/users/{user_id}", response_model=schemas.GetUser)
def get_user_by_id(
    user_id: int,
    dependancies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    db_user = crud.get_user_by_id(session=session, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="The user does not exist")
    return db_user


@app.get("/admin")
def admin_page(
    dependancies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    is_admin = crud.find_admin(session, dependancies)
    if is_admin == True:
        return {"msg": "welcome to the admin page"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin users can access this page",
        )


@app.post("/create-post")
def create_post(
    request: schemas.Post,
    dependancies=Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    existing_user, user_id = crud.find_user(session, dependancies)
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )

    post_db = models.Post(author_id=user_id, title=request.title, post=request.post)
    session.add(post_db)
    session.commit()
    return {"msg": "Post Created successfully", "payload": "Completed"}


@app.put("/post/{post_id}")
def update_post(
    request: schemas.ModifyPost,
    session: Session = Depends(get_session),
    dependancies=Depends(JWTBearer()),
):
    existing_user, user_id = crud.find_user(session, dependancies)
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )
    db_post = crud.get_post_by_id(session, post_id=request.post_id)
    if int(user_id) != int(db_post.author_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are only allowed to modify their posts",
        )
    db_post.title = request.title
    db_post.post = request.post
    db_post.published = request.published
    session.add(db_post)
    session.commit()
    return "success"


@app.get("/posts")
def get_posts(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    posts = crud.get_all_posts(session, skip=skip, limit=limit)
    return posts


@app.post("/logout")
def logout(dependancies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependancies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)

    user_id = payload["sub"]
    token_record = session.query(models.TokenTable).all()
    info = []
    for record in token_record:
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = (
            session.query(models.TokenTable)
            .where(TokenTable.user_id.in_(info))
            .delete()
        )
        session.commit()

    existing_token = (
        session.query(models.TokenTable)
        .filter(
            models.TokenTable.user_id == user_id,
            models.TokenTable.access_token == token,
        )
        .first()
    )
    if existing_token:
        existing_token.status = False
        session.add(existing_token)
        session.commit()
        session.refresh(existing_token)
    return {"message": "Logout Successfully"}


@app.post("/change-password")
def change_password(
    request: schemas.changepassword,
    session: Session = Depends(get_session),
    dependencies=Depends(JWTBearer()),
):
    user = session.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password does not match",
        )

    password_hash = get_hashed_password(request.new_password)
    user.password = password_hash
    session.commit()

    return {"message": "Password changed successfully", "payload": user}


@app.get("/getusers")
def getusers(
    dependancies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    users = session.query(models.User).all()
    return users


@app.post("/login")
def login(request: schemas.requestdetails, session: Session = Depends(get_session)):
    user = session.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email"
        )
    password_hash = user.password
    if not verify_password(request.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password"
        )
    access = create_access_token(subject=user.user_id, level_access=user.admin)
    refresh = create_refresh_token(user.user_id)

    token_db = models.TokenTable(
        user_id=user.user_id, access_token=access, refresh_token=refresh, status=True
    )
    session.add(token_db)
    session.commit()
    session.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }


@app.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    password_hash = get_hashed_password(user.password)
    new_user = models.User(
        username=user.username, password=password_hash, email=user.email
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"msg": "user created successfully", "payload": new_user}
