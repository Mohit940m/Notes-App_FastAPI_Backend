from app.core.database import users_collection
from app.utils.password_handler import hash_password
# from app.utils.auth import hash_password

import datetime

async def create_user(user_data: dict):
    user_data["password"] = hash_password(user_data["password"])
    user_data["created_at"] = datetime.datetime.utcnow()
    result = await users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data

async def find_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

