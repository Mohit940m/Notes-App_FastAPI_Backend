from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    pinned: bool = False
    serial_no: Optional[int] = None  # For drag/drop order

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    pinned: Optional[bool] = None
    serial_no: Optional[int] = None

class NoteOut(BaseModel):
    id: str
    user_id: str
    title: str
    content: Optional[str]
    pinned: bool
    serial_no: Optional[int]
    created_at: datetime
    updated_at: datetime
