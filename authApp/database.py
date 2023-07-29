from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg2://postgres:mypassword@localhost/auth"
engine = create_engine(DATABASE_URL)
Base = declarative_base(engine)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)