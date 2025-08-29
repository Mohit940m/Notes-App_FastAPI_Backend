from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.note_models import NoteCreate, NoteUpdate, NoteDB, NoteReorderPayload
from pymongo import UpdateOne
from app.core.database import db


class NoteService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["notes"]
        
    async def create_note(self, note: NoteCreate, creator_id: str) -> NoteDB:
        # Get the current number of notes for the user to set the order for the new note
        current_notes_count = await self.collection.count_documents({"creator_id": creator_id})
        doc = note.dict()
        doc.update({
            "creator_id": creator_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "order": current_notes_count
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
    
    async def reorder_notes(self, creator_id: str, reorder_data: List[NoteReorderPayload]) -> List[NoteDB]:
        """ Update the order acording to user input """
        if not reorder_data:
            return await self.get_notes(creator_id)

        # If only one note is being moved, we need to adjust the order of other notes.
        if len(reorder_data) == 1:
            item_to_move = reorder_data[0]
            note_id_to_move = item_to_move.note_id
            target_order = item_to_move.order

            # First, get the current order of the note being moved.
            note_doc = await self.collection.find_one(
                {"_id": ObjectId(note_id_to_move), "creator_id": creator_id},
                projection={"order": 1}
            )

            # If the note doesn't exist or doesn't belong to the user, do nothing.
            if not note_doc:
                return await self.get_notes(creator_id)

            source_order = note_doc.get("order")

            # If the note is already in the target position, there's nothing to do.
            if source_order == target_order:
                return await self.get_notes(creator_id)

            # --- Atomically shift other notes to make room or close the gap ---
            if source_order > target_order:
                # The note is moving UP the list (to a lower order number).
                # Increment the order of all notes between the target and the source.
                await self.collection.update_many(
                    {"creator_id": creator_id, "order": {"$gte": target_order, "$lt": source_order}},
                    {"$inc": {"order": 1}}
                )
            else:  # source_order < target_order
                # The note is moving DOWN the list (to a higher order number).
                # Decrement the order of all notes between the source and the target.
                await self.collection.update_many(
                    {"creator_id": creator_id, "order": {"$gt": source_order, "$lte": target_order}},
                    {"$inc": {"order": -1}}
                )

            # Finally, update the moved note to its new target order.
            await self.collection.update_one(
                {"_id": ObjectId(note_id_to_move), "creator_id": creator_id},
                {"$set": {"order": target_order, "updated_at": datetime.utcnow()}}
            )
        else:
            # This is the original logic for a full reorder of multiple items.
            operations = [
                UpdateOne(
                    {"_id": ObjectId(item.note_id), "creator_id": creator_id},
                    {"$set": {"order": item.order, "updated_at": datetime.utcnow()}},
                )
                for item in reorder_data
            ]
            await self.collection.bulk_write(operations)

        return await self.get_notes(creator_id)