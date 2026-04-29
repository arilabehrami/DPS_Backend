from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# E lexojme file-in .env
load_dotenv()

# E marrim DATABASE_URL prej .env
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL nuk u gjet. Kontrollo file-in .env.")

# Per SQLite duhet connect_args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Krijojme session per databaze
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base perdoret per modelet/tabelat
Base = declarative_base()


# Kjo perdoret ne routes per me marre databazen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()