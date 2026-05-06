from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    print(result.fetchall())
