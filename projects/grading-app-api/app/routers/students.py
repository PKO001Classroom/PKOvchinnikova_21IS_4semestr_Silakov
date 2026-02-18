from fastapi import APIRouter, HTTPException, status
from typing import List
from .. import models, crud

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/", response_model=List[models.Student])
async def get_students():
    """Получить список всех студентов"""
    return crud.get_students()

@router.get("/{student_id}", response_model=models.Student)
async def get_student(student_id: int):
    """Получить студента по ID"""
    student = crud.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@router.post("/", response_model=models.Student, status_code=status.HTTP_201_CREATED)
async def create_student(student: models.StudentCreate):
    """Создать нового студента"""
    new_student = crud.create_student(student)
    if not new_student:
        raise HTTPException(status_code=400, detail="Студент с таким номером зачётки уже существует")
    return new_student

@router.put("/{student_id}", response_model=models.Student)
async def update_student(student_id: int, student: models.StudentUpdate):
    """Обновить данные студента"""
    updated = crud.update_student(student_id, student)
    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int):
    """Удалить студента"""
    deleted = crud.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return None