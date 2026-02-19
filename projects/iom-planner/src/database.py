"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
import json
import os
from typing import List, Tuple, Optional


def init_db(db_path: str = "iom.db") -> None:
    """Инициализация базы данных и создание всех таблиц"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # Таблица цели
            c.execute('''
                CREATE TABLE IF NOT EXISTS цели (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    название TEXT NOT NULL,
                    тип TEXT NOT NULL,
                    статус TEXT DEFAULT 'Новая',
                    план_дата TEXT,
                    факт_дата TEXT,
                    темп TEXT,
                    описание TEXT
                )
            ''')

            # Таблица навыка
            c.execute('''
                CREATE TABLE IF NOT EXISTS навыка (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    название TEXT UNIQUE NOT NULL
                )
            ''')

            # Таблица цель_навыки
            c.execute('''
                CREATE TABLE IF NOT EXISTS цель_навыки (
                    цель_id INTEGER,
                    навык_id INTEGER,
                    FOREIGN KEY (цель_id) REFERENCES цели (id),
                    FOREIGN KEY (навык_id) REFERENCES навыка (id)
                )
            ''')

            # Таблица компетенции
            c.execute('''
                CREATE TABLE IF NOT EXISTS компетенции (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    название TEXT NOT NULL,
                    категория TEXT
                )
            ''')

            # Таблица цель_компетенции
            c.execute('''
                CREATE TABLE IF NOT EXISTS цель_компетенции (
                    цель_id INTEGER,
                    компетенция_id INTEGER,
                    уровень INTEGER CHECK (уровень BETWEEN 1 AND 5),
                    FOREIGN KEY (цель_id) REFERENCES цели (id),
                    FOREIGN KEY (компетенция_id) REFERENCES компетенции (id)
                )
            ''')

            # Таблица достижения
            c.execute('''
                CREATE TABLE IF NOT EXISTS достижения (
                    код TEXT PRIMARY KEY,
                    название TEXT NOT NULL,
                    описание TEXT,
                    получено INTEGER DEFAULT 0
                )
            ''')

            # Таблица цель_каса
            c.execute('''
                CREATE TABLE IF NOT EXISTS цель_каса (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    текст_цели TEXT NOT NULL,
                    тип_цели TEXT,
                    параметр TEXT,
                    текущий_прогресс INTEGER DEFAULT 0,
                    целевой_прогресс INTEGER NOT NULL
                )
            ''')

            # Заполняем достижения начальными данными
            achievements = [
                ('ach1', 'Старт', 'Создана первая цель', 0),
                ('ach2', 'Пунктуальный', 'Три или более завершённых целей в срок', 0),
                ('ach3', 'Многогранный', 'Есть цели минимум трёх разных типов', 0),
                ('ach4', 'Навыковый рост', 'У одного навыка четыре или более связанных завершённых целей', 0),
                ('ach5', 'Планирование', 'Одновременно в статусе "В процессе" пять или более целей', 0)
            ]

            c.execute("SELECT COUNT(*) FROM достижения")
            if c.fetchone()[0] == 0:
                c.executemany("INSERT INTO достижения VALUES (?, ?, ?, ?)", achievements)

            conn.commit()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")


def load_competencies_to_db(db_path: str = "iom.db") -> None:
    """Загрузка компетенций из JSON файла в базу данных"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM компетенции")
            if c.fetchone()[0] == 0 and os.path.exists('competencies.json'):
                with open('competencies.json', 'r', encoding='utf-8') as f:
                    competencies = json.load(f)
                    for comp in competencies:
                        c.execute("INSERT INTO компетенции (название, категория) VALUES (?, ?)",
                                  (comp['название'], comp['категория']))
                conn.commit()
                print("✅ Компетенции загружены из JSON")
    except Exception as e:
        print(f"❌ Ошибка загрузки компетенций: {e}")


def add_goal(db_path: str, name: str, goal_type: str, status: str,
             plan_date: str, fact_date: str, temp: str, description: str) -> Optional[int]:
    """Добавление новой цели"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO цели (название, тип, статус, план_дата, факт_дата, темп, описание)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, goal_type, status, plan_date, fact_date, temp, description))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"❌ Ошибка добавления цели: {e}")
        return None


def update_goal(db_path: str, goal_id: int, name: str, goal_type: str, status: str,
                plan_date: str, fact_date: str, temp: str, description: str) -> bool:
    """Обновление цели"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE цели 
                SET название = ?, тип = ?, статус = ?, план_дата = ?, факт_дата = ?, темп = ?, описание = ?
                WHERE id = ?
            ''', (name, goal_type, status, plan_date, fact_date, temp, description, goal_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка обновления цели: {e}")
        return False


def delete_goal(db_path: str, goal_id: int) -> bool:
    """Удаление цели"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM цели WHERE id = ?", (goal_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка удаления цели: {e}")
        return False


def get_all_goals(db_path: str) -> List[Tuple]:
    """Получение всех целей"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, название, тип, статус FROM цели ORDER BY статус, план_дата")
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки целей: {e}")
        return []


def get_goal_by_id(db_path: str, goal_id: int) -> Optional[Tuple]:
    """Получение цели по ID"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM цели WHERE id = ?", (goal_id,))
            return c.fetchone()
    except Exception as e:
        print(f"❌ Ошибка загрузки цели: {e}")
        return None


def add_skill(db_path: str, skill_name: str) -> int:
    """Добавление навыка (если не существует)"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM навыка WHERE название = ?", (skill_name,))
            row = c.fetchone()
            if row:
                return row[0]
            else:
                c.execute("INSERT INTO навыка (название) VALUES (?)", (skill_name,))
                conn.commit()
                return c.lastrowid
    except Exception as e:
        print(f"❌ Ошибка добавления навыка: {e}")
        return 0


def link_goal_skill(db_path: str, goal_id: int, skill_id: int) -> bool:
    """Связывание цели с навыком"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO цель_навыки (цель_id, навык_id) VALUES (?, ?)", (goal_id, skill_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка связывания цели с навыком: {e}")
        return False


def get_goal_skills(db_path: str, goal_id: int) -> List[str]:
    """Получение навыков цели"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT н.название 
                FROM навыка н
                JOIN цель_навыки цн ON н.id = цн.навык_id
                WHERE цн.цель_id = ?
            ''', (goal_id,))
            return [row[0] for row in c.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка загрузки навыков: {e}")
        return []


def get_all_skills(db_path: str) -> List[str]:
    """Получение всех навыков"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT название FROM навыка")
            return [row[0] for row in c.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка загрузки навыков: {e}")
        return []


def add_competency_link(db_path: str, goal_id: int, competency_id: int, level: int) -> bool:
    """Связывание цели с компетенцией"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO цель_компетенции (цель_id, компетенция_id, уровень)
                VALUES (?, ?, ?)
            ''', (goal_id, competency_id, level))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка связывания цели с компетенцией: {e}")
        return False


def get_goal_competencies(db_path: str, goal_id: int) -> List[Tuple]:
    """Получение компетенций цели"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT к.id, к.название, цк.уровень
                FROM компетенции к
                JOIN цель_компетенции цк ON к.id = цк.компетенция_id
                WHERE цк.цель_id = ?
            ''', (goal_id,))
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки компетенций: {e}")
        return []


def get_all_competencies(db_path: str) -> List[Tuple]:
    """Получение всех компетенций"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, название FROM компетенции")
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки компетенций: {e}")
        return []


def get_competency_averages(db_path: str) -> List[Tuple]:
    """Получение средних уровней по компетенциям"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT к.название, к.категория, ROUND(AVG(цк.уровень), 1) as средний_уровень
                FROM компетенции к
                LEFT JOIN цель_компетенции цк ON к.id = цк.компетенция_id
                LEFT JOIN цели ц ON цк.цель_id = ц.id AND ц.статус = 'Завершена'
                GROUP BY к.id
            ''')
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки компетенций: {e}")
        return []


def check_achievements(db_path: str) -> List[str]:
    """Проверка и обновление достижений"""
    unlocked = []
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # 1. Старт - создана первая цель
            c.execute("SELECT COUNT(*) FROM цели")
            if c.fetchone()[0] >= 1:
                c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach1'")
                unlocked.append('ach1')

            # 2. Пунктуальный - 3+ целей в срок
            c.execute('''
                SELECT COUNT(*) FROM цели 
                WHERE статус = 'Завершена' 
                AND факт_дата IS NOT NULL 
                AND план_дата IS NOT NULL
                AND факт_дата <= план_дата
            ''')
            if c.fetchone()[0] >= 3:
                c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach2'")
                unlocked.append('ach2')

            # 3. Многогранный - цели 3+ разных типов
            c.execute("SELECT COUNT(DISTINCT тип) FROM цели WHERE статус = 'Завершена'")
            if c.fetchone()[0] >= 3:
                c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach3'")
                unlocked.append('ach3')

            # 4. Навыковый рост - у одного навыка 4+ целей
            c.execute('''
                SELECT н.название, COUNT(цн.цель_id) 
                FROM навыка н
                JOIN цель_навыки цн ON н.id = цн.навык_id
                JOIN цели ц ON цн.цель_id = ц.id AND ц.статус = 'Завершена'
                GROUP BY н.id
                HAVING COUNT(цн.цель_id) >= 4
            ''')
            if c.fetchone():
                c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach4'")
                unlocked.append('ach4')

            # 5. Планирование - 5+ целей в процессе
            c.execute("SELECT COUNT(*) FROM цели WHERE статус = 'В процессе'")
            if c.fetchone()[0] >= 5:
                c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach5'")
                unlocked.append('ach5')

            conn.commit()
        return unlocked
    except Exception as e:
        print(f"❌ Ошибка проверки достижений: {e}")
        return []


def get_all_achievements(db_path: str) -> List[Tuple]:
    """Получение всех достижений"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM достижения ORDER BY получено DESC, название")
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки достижений: {e}")
        return []


def add_semester_goal(db_path: str, text: str, goal_type: str, param: str, target: int) -> Optional[int]:
    """Добавление цели на семестр"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO цель_каса (текст_цели, тип_цели, параметр, целевой_прогресс)
                VALUES (?, ?, ?, ?)
            ''', (text, goal_type, param, target))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"❌ Ошибка добавления цели на семестр: {e}")
        return None


def get_semester_goals(db_path: str) -> List[Tuple]:
    """Получение всех целей на семестр"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, текст_цели, тип_цели, текущий_прогресс, целевой_прогресс FROM цель_каса")
            return c.fetchall()
    except Exception as e:
        print(f"❌ Ошибка загрузки целей на семестр: {e}")
        return []


def delete_semester_goal(db_path: str, goal_id: int) -> bool:
    """Удаление цели на семестр"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM цель_каса WHERE id = ?", (goal_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка удаления цели на семестр: {e}")
        return False


def update_semester_progress(db_path: str, goal_id: int, progress: int) -> bool:
    """Обновление прогресса цели на семестр"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE цель_каса SET текущий_прогресс = ? WHERE id = ?", (progress, goal_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка обновления прогресса: {e}")
        return False