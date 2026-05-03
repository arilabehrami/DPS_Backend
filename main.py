from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.user import User
from routes.auth import router as auth_router
from models.personality import Personality
from models.conversation import Conversation
from models.message import Message


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Digital Personality Simulator",
    description="Backend API for register and login",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Backend is alive"
    }