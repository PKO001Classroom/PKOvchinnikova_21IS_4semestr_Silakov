"""
Тесты для приложения "Оценивание"
"""
import pytest
import os
import tempfile
import shutil
import sqlite3
import time
from unittest.mock import MagicMock, patch
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db():
    """Создание временной базы данных для тестов с инициализацией таблиц"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Инициализируем таблицы
    from src.database import init_db
    init_db(path)
    
    yield path
    
    # Даем время на закрытие соединений
    time.sleep(0.1)
    
    if os.path.exists(path):
        try:
            os.unlink(path)
        except PermissionError:
            time.sleep(0.2)
            try:
                os.unlink(path)
            except:
                pass


class TestDatabase:
    """Тесты для модуля database.py"""

    def test_init_db(self, temp_db):
        """Тест инициализации БД"""
        from src.database import init_db

        # Проверяем, что таблицы созданы
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert 'students' in tables
        assert 'subjects' in tables
        assert 'grades' in tables

    def test_add_student(self, temp_db):
        """Тест добавления студента"""
        from src.database import add_student, get_all_students

        student_id = add_student(temp_db, "Иванов Иван", "12345")
        assert student_id > 0

        students = get_all_students(temp_db)
        assert len(students) == 1
        assert students[0][1] == "Иванов Иван"
        assert students[0][2] == "12345"

    def test_add_duplicate_student(self, temp_db):
        """Тест добавления дубликата студента"""
        from src.database import add_student

        add_student(temp_db, "Иванов Иван", "12345")
        result = add_student(temp_db, "Петров Петр", "12345")
        assert result is None

    def test_add_subject(self, temp_db):
        """Тест добавления предмета"""
        from src.database import add_subject, get_all_subjects

        subject_id = add_subject(temp_db, "Математика")
        assert subject_id > 0

        subjects = get_all_subjects(temp_db)
        assert len(subjects) == 1
        assert subjects[0][1] == "Математика"

    def test_add_grade(self, temp_db):
        """Тест добавления оценки"""
        from src.database import add_student, add_subject, add_grade, get_grades_for_student

        student_id = add_student(temp_db, "Иванов Иван", "12345")
        subject_id = add_subject(temp_db, "Математика")

        result = add_grade(temp_db, student_id, subject_id, 5, "2024-01-01")
        assert result is True

        grades = get_grades_for_student(temp_db, student_id)
        assert len(grades) == 1
        assert grades[0][2] == 5

    def test_student_average(self, temp_db):
        """Тест подсчета среднего балла"""
        from src.database import add_student, add_subject, add_grade, get_student_average

        student_id = add_student(temp_db, "Иванов Иван", "12345")
        math_id = add_subject(temp_db, "Математика")
        phys_id = add_subject(temp_db, "Физика")

        add_grade(temp_db, student_id, math_id, 5, "2024-01-01")
        add_grade(temp_db, student_id, math_id, 4, "2024-02-01")
        add_grade(temp_db, student_id, phys_id, 5, "2024-01-15")

        avg = get_student_average(temp_db, student_id)
        assert round(avg, 2) == 4.67  # (5+4+5)/3 = 4.666...


class TestModels:
    """Тесты для модуля models.py"""

    def test_student_model(self):
        """Тест модели Student"""
        from src.models import Student

        student = Student.from_db_row((1, "Иванов Иван", "12345"))
        assert student.id == 1
        assert student.name == "Иванов Иван"
        assert student.student_id == "12345"
        assert student.display_string() == "Иванов Иван (12345)"

    def test_subject_model(self):
        """Тест модели Subject"""
        from src.models import Subject

        subject = Subject.from_db_row((1, "Математика"))
        assert subject.id == 1
        assert subject.name == "Математика"

    def test_grade_model(self):
        """Тест модели Grade"""
        from src.models import Grade

        grade = Grade.from_db_row((1, "Математика", 5, "2024-01-01"))
        assert grade.id == 1
        assert grade.subject_name == "Математика"
        assert grade.grade == 5
        assert grade.date == "2024-01-01"


class TestUtils:
    """Тесты для модуля utils.py"""

    def test_validate_date(self):
        """Тест проверки даты"""
        from src.utils import validate_date

        assert validate_date("2024-01-01") is True
        assert validate_date("2024-13-01") is False
        assert validate_date("01-01-2024") is False

    def test_validate_grade(self):
        """Тест проверки оценки"""
        from src.utils import validate_grade

        assert validate_grade(2) is True
        assert validate_grade(5) is True
        assert validate_grade(1) is False
        assert validate_grade(6) is False

    def test_calculate_average(self):
        """Тест расчета среднего"""
        from src.utils import calculate_average

        assert calculate_average([5, 4, 5]) == 4.67
        assert calculate_average([2, 3, 4]) == 3.0
        assert calculate_average([]) == 0.0


class TestGUI:
    """Тесты для модуля gui.py"""

    @pytest.fixture
    def mock_tkinter(self):
        """Мок для tkinter компонентов"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_root.tk = MagicMock()
            
            with patch('tkinter.ttk.Notebook'):
                with patch('tkinter.Frame'):
                    with patch('tkinter.Label'):
                        with patch('tkinter.Entry'):
                            with patch('tkinter.Text'):
                                with patch('tkinter.Button'):
                                    with patch('tkinter.Listbox'):
                                        with patch('tkinter.ttk.Combobox'):
                                            with patch('tkinter.messagebox.showinfo'):
                                                with patch('tkinter.messagebox.showerror'):
                                                    with patch('tkinter.messagebox.showwarning'):
                                                        yield mock_tk

    def test_app_initialization(self, mock_tkinter, temp_db):
        """Тест инициализации приложения"""
        from src.gui import GradingApp

        with patch('src.database.get_all_students', return_value=[]):
            with patch('src.database.get_all_subjects', return_value=[]):
                root = MagicMock()
                root.tk = MagicMock()
                
                app = GradingApp(root)
                assert app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])