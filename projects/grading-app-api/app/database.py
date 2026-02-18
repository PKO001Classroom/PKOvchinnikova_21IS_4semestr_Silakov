import sqlite3
from typing import List, Tuple, Optional

DB_PATH = "grades.db"

def init_db(db_path: str = DB_PATH) -> None:
    """Создание таблиц students, subjects и grades."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    student_id TEXT UNIQUE NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    grade INTEGER NOT NULL CHECK(grade >= 2 AND grade <= 5),
                    date TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            ''')
            conn.commit()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")

def add_student(db_path: str, name: str, student_id: str) -> Optional[int]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO students (name, student_id) VALUES (?, ?)", (name, student_id))
            conn.commit()
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"❌ Ошибка добавления студента: {e}")
        return None

def get_all_students(db_path: str) -> List[Tuple]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, student_id FROM students ORDER BY name")
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки студентов: {e}")
        return []

def get_student_by_id(db_path: str, student_id: int) -> Optional[Tuple]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, student_id FROM students WHERE id = ?", (student_id,))
            return cur.fetchone()
    except Exception as e:
        print(f"❌ Ошибка загрузки студента: {e}")
        return None

def update_student(db_path: str, student_id: int, name: str, student_id_num: str) -> bool:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE students SET name = ?, student_id = ? WHERE id = ?",
                       (name, student_id_num, student_id))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"❌ Ошибка обновления студента: {e}")
        return False

def delete_student(db_path: str, student_id: int) -> bool:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"❌ Ошибка удаления студента: {e}")
        return False

def add_subject(db_path: str, name: str) -> Optional[int]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"❌ Ошибка добавления предмета: {e}")
        return None

def get_all_subjects(db_path: str) -> List[Tuple]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM subjects ORDER BY name")
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки предметов: {e}")
        return []

def add_grade(db_path: str, student_id: int, subject_id: int, grade: int, date: str) -> bool:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO grades (student_id, subject_id, grade, date)
                VALUES (?, ?, ?, ?)
            ''', (student_id, subject_id, grade, date))
            conn.commit()
        return True
    except Exception as e:
        print(f"❌ Ошибка добавления оценки: {e}")
        return False

def get_grades_for_student(db_path: str, student_id: int) -> List[Tuple]:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT g.id, s.name, g.grade, g.date
                FROM grades g
                JOIN subjects s ON g.subject_id = s.id
                WHERE g.student_id = ?
                ORDER BY g.date DESC
            ''', (student_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки оценок: {e}")
        return []

def get_student_average(db_path: str, student_id: int) -> float:
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT AVG(grade) FROM grades WHERE student_id = ?", (student_id,))
            result = cur.fetchone()[0]
            return round(result, 2) if result else 0.0
    except Exception as e:
        print(f"❌ Ошибка подсчета среднего: {e}")
        return 0.0