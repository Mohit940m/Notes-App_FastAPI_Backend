from fastapi import HTTPException
from app.models.user_models import UserCreate, UserLogin
from app.services.user_service import create_user, find_user_by_email
from app.utils.password_handler import verify_password
from app.utils.jwt_handler import create_access_token

async def register_user(user: UserCreate):
    existing_user = await find_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await create_user(user.dict())
    return {"id": new_user["_id"], "email": new_user["email"]}

async def login_user(user: UserLogin):
    db_user = await find_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user["_id"])})
    return {"access_token": token, "token_type": "bearer"}
