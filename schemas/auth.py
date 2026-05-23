from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    workspace_id: int
    role_id: int
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    id: int
    workspace_id: int
    role_id: int
    username: str
    email: EmailStr
    role: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse
