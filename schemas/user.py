from pydantic import BaseModel, EmailStr


# Te dhenat qe i dergon user-i kur regjistrohet
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# Te dhenat qe i dergon user-i kur ben login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Pergjigjja qe kthehet pas register
# Password nuk kthehet kurr
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True


# Pergjigjja qe kthehet pas login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str