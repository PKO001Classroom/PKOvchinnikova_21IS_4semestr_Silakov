"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
from typing import List, Tuple


def init_db(db_path: str = "достижения.db") -> None:
    """Создание базы данных и таблицы, если их нет"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS достижения (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                название TEXT NOT NULL,
                дата TEXT NOT NULL,
                тип TEXT,
                уровень TEXT,
                описание TEXT
            )
        """)
        conn.commit()
        print("База данных инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
    finally:
        if conn:
            conn.close()


def save_achievement(name: str, date: str, typ: str, level: str, desc: str,
                     db_path: str = "достижения.db") -> bool:
    """Сохранение достижения в базу данных"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO достижения (название, дата, тип, уровень, описание) VALUES (?, ?, ?, ?, ?)",
            (name, date, typ, level, desc)
        )
        conn.commit()
        print(f"Успешно сохранено: {name}")
        return True
    except Exception as e:
        print(f"Ошибка сохранения в БД: {e}")
        return False
    finally:
        if conn:
            conn.close()


def load_all_achievements(db_path: str = "достижения.db") -> List[Tuple]:
    """Загрузка всех записей из базы данных"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, название, дата, тип, уровень, описание
            FROM достижения
            ORDER BY дата DESC
        """)
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"Ошибка загрузки из БД: {e}")
        return []
    finally:
        if conn:
            conn.close()


def delete_achievement(achievement_id: int, db_path: str = "достижения.db") -> bool:
    """Удаление достижения по ID"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM достижения WHERE id = ?", (achievement_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка удаления: {e}")
        return False
    finally:
        if conn:
            conn.close()
