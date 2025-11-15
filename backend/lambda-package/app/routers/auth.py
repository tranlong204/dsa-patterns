from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from app.config import settings
from app.auth import verify_password, create_access_token, get_current_username

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # Default single user
    if username != settings.DEFAULT_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not settings.DEFAULT_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Server not configured with password hash")
    if not verify_password(password, settings.DEFAULT_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def me(current_user: str = Depends(get_current_username)):
    return {"username": current_user}


