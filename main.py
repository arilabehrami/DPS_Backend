from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.user import User
from models.personality import Personality
from models.conversation import Conversation
from models.message import Message

from routes.auth import router as auth_router
from routes.personality import router as personality_router
from routes.user import router as user_router
from routes.conversation import router as conversation_router
from routes.message import router as message_router
from routes import test


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Personality Simulator",
    description="Backend API for authentication, personalities, conversations and AI chat",
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
app.include_router(personality_router) 
app.include_router(user_router)
app.include_router(test.router, prefix="", tags=["Test"])
app.include_router(conversation_router)
app.include_router(message_router)

@app.get("/")
def home():
    return {"message": "Backend is alive"}
