from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.note_models import NoteCreate, NoteUpdate, NoteDB
from app.services.note_service import NoteService
from app.core.database import get_db
from app.utils.auth import get_current_user


router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/create", response_model=NoteDB)
async def create_note(note: NoteCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = NoteService(db)
    return await service.create_note(note, creator_id=str(current_user["_id"]))


@router.get("/", response_model=List[NoteDB])
async def get_notes(db=Depends(get_db), current_user=Depends(get_current_user)):
    service = NoteService(db)
    return await service.get_notes(str(current_user["_id"]))


@router.put("/{note_id}", response_model=NoteDB)
async def update_note(note_id: str, note: NoteUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = NoteService(db)
    updated = await service.update_note(note_id, note, str(current_user["_id"]))
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


@router.delete("/{note_id}")
async def delete_note(note_id: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    service = NoteService(db)
    success = await service.delete_note(note_id, str(current_user["_id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"deleted": True}


@router.post("/reorder", response_model=List[NoteDB])
async def reorder_notes(note_ids: List[str], db=Depends(get_db), current_user=Depends(get_current_user)):
    service = NoteService(db)
    return await service.reorder_notes(creator_id=str(current_user["_id"]), note_ids=note_ids)
