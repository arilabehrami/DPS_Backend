from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.user import User
from routes.auth import router as auth_router


# Krijon tabelat ne databaze
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Digital Personality Simulator",
    description="Backend API for register and login",
    version="1.0.0"
)


# Kjo lejon React-in me fol me backend-in
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ketu po i lidhim register dhe login me main.py
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Backend is alive"
    }