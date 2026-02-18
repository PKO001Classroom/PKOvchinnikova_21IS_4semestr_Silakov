import pytest
from fastapi.testclient import TestClient
import sys
import os
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import init_db

client = TestClient(app)

def clear_db(db_path="test_grades.db"):
    """Очистка базы данных перед тестами"""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM grades")
        cur.execute("DELETE FROM students")
        cur.execute("DELETE FROM subjects")
        conn.commit()
        conn.close()
    except:
        pass

class TestStudents:
    def setup_method(self):
        clear_db()
        init_db("test_grades.db")
        import app.crud
        app.crud.DB_PATH = "test_grades.db"

    def test_create_student(self):
        response = client.post(
            "/students/",
            json={"name": "Иванов Иван", "student_id": "12345"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Иванов Иван"
        assert data["student_id"] == "12345"
        assert "id" in data

    def test_get_students(self):
        client.post("/students/", json={"name": "Петров Петр", "student_id": "54321"})
        response = client.get("/students/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_student_not_found(self):
        response = client.get("/students/999")
        assert response.status_code == 404

class TestSubjects:
    def setup_method(self):
        clear_db()
        init_db("test_grades.db")
        import app.crud
        app.crud.DB_PATH = "test_grades.db"

    def test_create_subject(self):
        response = client.post("/subjects/", json={"name": "Математика"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Математика"

class TestGrades:
    def setup_method(self):
        clear_db()
        init_db("test_grades.db")
        import app.crud
        app.crud.DB_PATH = "test_grades.db"
        
        # Создаем студента
        student_response = client.post(
            "/students/", 
            json={"name": "Тестов", "student_id": "99999"}
        )
        assert student_response.status_code == 201
        student_data = student_response.json()
        self.student_id = student_data["id"]
        
        # Создаем предмет
        subject_response = client.post(
            "/subjects/", 
            json={"name": "Тестовый предмет"}
        )
        assert subject_response.status_code == 201
        subject_data = subject_response.json()
        self.subject_id = subject_data["id"]

    def test_create_grade(self):
        response = client.post(
            "/grades/",
            json={
                "student_id": self.student_id,
                "subject_id": self.subject_id,
                "grade": 5,
                "date": "2024-01-01"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["grade"] == 5
        assert data["student_id"] == self.student_id
        assert data["subject_id"] == self.subject_id

    def test_get_student_stats(self):
        # Создаем несколько оценок
        client.post("/grades/", json={
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "grade": 5,
            "date": "2024-01-01"
        })
        client.post("/grades/", json={
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "grade": 4,
            "date": "2024-01-02"
        })

        response = client.get(f"/grades/student/{self.student_id}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_grades"] == 2
        assert data["average_grade"] == 4.5
        assert data["student_id"] == self.student_id
        assert data["student_name"] == "Тестов"