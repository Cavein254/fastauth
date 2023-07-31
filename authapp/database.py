from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")

DATABASE_URL = database_url
engine = create_engine(DATABASE_URL)
Base = declarative_base(engine)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)