from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.note_models import NoteCreate, NoteUpdate, NoteDB
from app.core.database import db


class NoteService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["notes"]
        
    async def create_note(self, note: NoteCreate, creator_id: str) -> NoteDB:
        doc = note.dict()
        doc.update({
            "creator_id": creator_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return NoteDB(**doc)
    
    
    async def get_notes(self, creator_id: str) -> list[NoteDB]:
        cursor = self.collection.find({"creator_id": creator_id}).sort("order", 1)
        # Convert the '_id' from ObjectId to string before creating the Pydantic model.
        return [NoteDB(**{**doc, "_id": str(doc["_id"])}) async for doc in cursor]
    
    async def update_note(self, note_id: str, note_update: NoteUpdate, creator_id: str) -> Optional[NoteDB]:
        update_data = {k: v for k, v in note_update.dict(exclude_unset=True).items()}
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                # Query with ObjectId, not string
                {"_id": ObjectId(note_id), "creator_id": creator_id}, {"$set": update_data}
            )
        # Query with ObjectId, not string
        doc = await self.collection.find_one({"_id": ObjectId(note_id), "creator_id": creator_id})
        # Convert '_id' to string before creating the Pydantic model
        return NoteDB(**{**doc, "_id": str(doc["_id"])}) if doc else None
    
    async def delete_note(self, note_id: str, creator_id: str) -> bool:
        # Query with ObjectId, not string
        result = await self.collection.delete_one({"_id": ObjectId(note_id), "creator_id": creator_id})
        return result.deleted_count > 0
    
    async def reorder_notes(self, creator_id: str, note_ids: List[str]) -> List[NoteDB]:
        """ Update the order acording to user input """
        for index, note_id in enumerate(note_ids):
            await self.collection.update_one(
                # Query with ObjectId, not string
                {"_id": ObjectId(note_id), "creator_id": creator_id},
                {"$set": {"order": index, "updated_at": datetime.utcnow()}}
            )
        return await self.get_notes(creator_id)