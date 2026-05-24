import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from middleware.logging_middleware import LoggingMiddleware

# Import models so SQLAlchemy can register all tables before create_all
import models

# Import all routes from routes/__init__.py
from routes import ALL_ROUTERS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Digital Personality Simulator API",
    description="Backend API for Digital Personality Simulator project",
    version="1.0.0",
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Digital Personality Simulator API is running successfully"
    }


for router in ALL_ROUTERS:
    app.include_router(router)