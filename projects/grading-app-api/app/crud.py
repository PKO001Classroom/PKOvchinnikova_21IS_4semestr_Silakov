from . import database
from . import models
from typing import List, Optional

DB_PATH = "grades.db"

# CRUD для студентов
def get_students() -> List[models.Student]:
    rows = database.get_all_students(DB_PATH)
    return [models.Student(id=row[0], name=row[1], student_id=row[2]) for row in rows]

def get_student(student_id: int) -> Optional[models.Student]:
    row = database.get_student_by_id(DB_PATH, student_id)
    if row:
        return models.Student(id=row[0], name=row[1], student_id=row[2])
    return None

def create_student(student: models.StudentCreate) -> Optional[models.Student]:
    student_id = database.add_student(DB_PATH, student.name, student.student_id)
    if student_id:
        return get_student(student_id)
    return None

def update_student(student_id: int, student: models.StudentUpdate) -> Optional[models.Student]:
    current = get_student(student_id)
    if not current:
        return None

    name = student.name if student.name is not None else current.name
    student_id_num = student.student_id if student.student_id is not None else current.student_id

    success = database.update_student(DB_PATH, student_id, name, student_id_num)
    if success:
        return get_student(student_id)
    return None

def delete_student(student_id: int) -> bool:
    return database.delete_student(DB_PATH, student_id)

# CRUD для предметов
def get_subjects() -> List[models.Subject]:
    rows = database.get_all_subjects(DB_PATH)
    return [models.Subject(id=row[0], name=row[1]) for row in rows]

def create_subject(subject: models.SubjectCreate) -> Optional[models.Subject]:
    subject_id = database.add_subject(DB_PATH, subject.name)
    if subject_id:
        return models.Subject(id=subject_id, name=subject.name)
    return None

# CRUD для оценок
def create_grade(grade: models.GradeCreate) -> Optional[models.Grade]:
    success = database.add_grade(DB_PATH, grade.student_id, grade.subject_id,
                                 grade.grade, grade.date)
    if success:
        subjects = {s.id: s.name for s in get_subjects()}
        return models.Grade(
            id=0,
            student_id=grade.student_id,
            subject_id=grade.subject_id,
            subject_name=subjects.get(grade.subject_id, ""),
            grade=grade.grade,
            date=grade.date
        )
    return None

def get_student_grades(student_id: int) -> List[models.Grade]:
    rows = database.get_grades_for_student(DB_PATH, student_id)
    return [
        models.Grade(
            id=row[0],
            student_id=student_id,
            subject_id=0,
            subject_name=row[1],
            grade=row[2],
            date=row[3]
        )
        for row in rows
    ]

def get_student_statistics(student_id: int) -> Optional[models.StudentStats]:
    student = get_student(student_id)
    if not student:
        return None

    grades = get_student_grades(student_id)

    grades_by_subject = {}
    for grade in grades:
        if grade.subject_name not in grades_by_subject:
            grades_by_subject[grade.subject_name] = []
        grades_by_subject[grade.subject_name].append(grade.grade)

    grades_summary = {
        subject: {
            "grades": g_list,
            "average": round(sum(g_list) / len(g_list), 2)
        }
        for subject, g_list in grades_by_subject.items()
    }

    avg = database.get_student_average(DB_PATH, student_id)

    return models.StudentStats(
        student_id=student_id,
        student_name=student.name,
        total_grades=len(grades),
        average_grade=avg,
        grades_by_subject=grades_summary
    )