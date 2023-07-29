from authApp import schemas, models
from authApp.database import Base,engine,SessionLocal
from fastapi import FastAPI,Depends, HTTPException, status
from sqlalchemy.orm import Session

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

app = FastAPI()

