from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")

engine = create_engine("postgresql+psycopg2://postgres:mypassword@localhost:5432/auth2")
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
