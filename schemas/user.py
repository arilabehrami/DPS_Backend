from pydantic import BaseModel


# =========================
# CREATE USER
# =========================
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# =========================
# LOGIN USER
# =========================
class UserLogin(BaseModel):
    email: str
    password: str


# =========================
# RESPONSE USER (FIX)
# =========================
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True