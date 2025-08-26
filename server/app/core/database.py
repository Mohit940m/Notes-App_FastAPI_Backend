from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)

db = client[settings.DATABASE_NAME]

async def get_db():
    
    print("Database connection established")
    yield db
    print("Database connection closed")

users_collection = db["users"]
notes_collection = db["notes"]