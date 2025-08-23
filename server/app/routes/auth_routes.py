from fastapi import APIRouter
from app.models.user_models import UserCreate, UserLogin
from app.controllers.auth_controller import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user: UserCreate):
    return await register_user(user)

@router.post("/login")
async def login(user: UserLogin):
    return await login_user(user)
