from fastapi import APIRouter, HTTPException, status
from typing import List
from .. import models, crud

router = APIRouter(prefix="/grades", tags=["grades"])

@router.post("/", response_model=models.Grade, status_code=status.HTTP_201_CREATED)
async def create_grade(grade: models.GradeCreate):
    """Выставить оценку студенту"""
    student = crud.get_student(grade.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    subjects = crud.get_subjects()
    subject_exists = any(s.id == grade.subject_id for s in subjects)
    if not subject_exists:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    new_grade = crud.create_grade(grade)
    if not new_grade:
        raise HTTPException(status_code=400, detail="Не удалось сохранить оценку")
    return new_grade

@router.get("/student/{student_id}", response_model=List[models.Grade])
async def get_student_grades(student_id: int):
    """Получить все оценки студента"""
    student = crud.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    return crud.get_student_grades(student_id)

@router.get("/student/{student_id}/stats", response_model=models.StudentStats)
async def get_student_statistics(student_id: int):
    """Получить статистику успеваемости студента"""
    student = crud.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    stats = crud.get_student_statistics(student_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Нет данных для статистики")
    return stats