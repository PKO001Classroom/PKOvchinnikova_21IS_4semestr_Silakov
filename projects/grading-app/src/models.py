from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Student:
    id: Optional[int]
    name: str
    student_id: str

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Student':
        return cls(id=row[0], name=row[1], student_id=row[2])

    def display_string(self) -> str:
        return f"{self.name} ({self.student_id})"

@dataclass
class Subject:
    id: Optional[int]
    name: str

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Subject':
        return cls(id=row[0], name=row[1])

@dataclass
class Grade:
    id: Optional[int]
    subject_name: str
    grade: int
    date: str

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Grade':
        return cls(id=row[0], subject_name=row[1], grade=row[2], date=row[3])