from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

clitent = AsyncIOMotorClient(settings.MONGO_URI)

db = clitent[settings.DATABASE_NAME]

users_collection = db["users"]
notes_collection = db["notes"]