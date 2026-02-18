from fastapi import APIRouter, HTTPException, status
from typing import List
from .. import models, crud

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("/", response_model=List[models.Subject])
async def get_subjects():
    """Получить список всех предметов"""
    return crud.get_subjects()

@router.post("/", response_model=models.Subject, status_code=status.HTTP_201_CREATED)
async def create_subject(subject: models.SubjectCreate):
    """Создать новый предмет"""
    new_subject = crud.create_subject(subject)
    if not new_subject:
        raise HTTPException(status_code=400, detail="Предмет с таким названием уже существует")
    return new_subject