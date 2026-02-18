from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Модели для студентов
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="ФИО студента")
    student_id: str = Field(..., min_length=1, max_length=20, description="Номер зачётки")

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    student_id: Optional[str] = Field(None, min_length=1, max_length=20)

class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True

# Модели для предметов
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название предмета")

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int

    class Config:
        from_attributes = True

# Модели для оценок
class GradeBase(BaseModel):
    student_id: int
    subject_id: int
    grade: int = Field(..., ge=2, le=5, description="Оценка от 2 до 5")
    date: str = Field(..., description="Дата в формате ГГГГ-ММ-ДД")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError('Дата должна быть в формате ГГГГ-ММ-ДД')

class GradeCreate(GradeBase):
    pass

class Grade(GradeBase):
    id: int
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True

# Модели для статистики
class StudentStats(BaseModel):
    student_id: int
    student_name: str
    total_grades: int
    average_grade: float
    grades_by_subject: Dict[str, Any]