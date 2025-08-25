from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.note_models import NoteCreate, NoteUpdate, NoteDB


class NoteService:
    def __inti__(self, db: AsyncIOMotorDatabase):
        self.collection = db["notes"]
        
    async def create_note(self, note: NoteCreate, creator_id: str) -> NoteDb:
        doc = note.dist()
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
        return [NoteDB(**doc, id=str(doc["_id"])) async for doc in cursor]
    
    async def update_note(self, note_id: str, note_update: NoteUpdate, creator_id: str) -> Optional[NoteDB]:
        update_date = {k: v for k, v in note_update.dict(exclude_unset=True).item()}
        if update_date:
            update_date["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": note_id, "creator_id": creator_id}, {"$set": update_date}
            )
        doc = await self.collection.find_one({"_id": note_id, "creator_id": creator_id})
        return NoteDB(**doc, id=str(doc["_id"])) if doc else None
    
    async def delete_note(self, note_id: str, creator_id: str) -> bool:
        result = await self.collection.delete_one({"_id": note_id, "creator_id": creator_id})
        return result.deleted_count > 0
    
    async def reorder_notes(self, note_ids: List[str], creator_id: str) -> List[NoteDB]:
        """ Update the order acording to user input """
        for index, note_id in enumerate(note_id):
            await self.collection.update_one(
                {"_id": note_id, "creator_id": creator_id},
                {"$set": {"order": index, "updated_at": datetime.utcnow()}}
            )
        return await self.get_notes(creator_id)