from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# E lexojme .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Kjo perdoret per me bo password-in hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# E kthen password-in normal ne password te hash-um
def hash_password(password: str):
    return pwd_context.hash(password)


# Kontrollon a perputhet password-i normal me password-in e hash-um
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# Krijon JWT token pas login
def create_access_token(data: dict):
    data_to_encode = data.copy()

    expire_time = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    data_to_encode.update({"exp": expire_time})

    token = jwt.encode(
        data_to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token