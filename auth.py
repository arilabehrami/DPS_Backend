from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):

    # fake auth per testim
    if token != "test":
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {
        "id": 1,
        "username": "test_user"
    }