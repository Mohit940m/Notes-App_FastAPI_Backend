from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class NoteBase(BaseModel):
    title: str
    content: str
    pinned: bool = False


class NoteCreate(NoteBase):
    order: Optional[int] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    pinned: Optional[bool] = None
    order: Optional[int] = None


class NoteDB(NoteBase):
    id: str = Field(default_factory=str, alias="_id")
    creator_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    order: Optional[int] = None

    class Config:
        json_encoders = {ObjectId: str}
        orm_mode = True
