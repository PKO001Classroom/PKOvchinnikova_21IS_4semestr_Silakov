import sqlite3
import json
from datetime import datetime


class Database:
    def __init__(self, db_name="portfolio.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.init_achievements()

    def create_tables(self):
        """Создание всех таблиц базы данных"""
        # Таблица записей портфолио
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                название TEXT NOT NULL,
                тип TEXT NOT NULL,
                дата DATE NOT NULL,
                описание TEXT,
                соавторы TEXT
            )
        ''')

        # Таблица ключевых слов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL
            )
        ''')

        # Таблица связи запись-ключевые слова
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_keywords (
                entry_id INTEGER,
                keyword_id INTEGER,
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (keyword_id) REFERENCES keywords(id),
                PRIMARY KEY (entry_id, keyword_id)
            )
        ''')

        # Таблица достижений
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                название TEXT NOT NULL UNIQUE,
                описание TEXT,
                получено BOOLEAN DEFAULT FALSE,
                дата_получения DATE
            )
        ''')

        # Таблица компетенций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS competencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                название TEXT NOT NULL UNIQUE,
                категория TEXT
            )
        ''')

        # Таблица связи запись-компетенции
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_competencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                competency_id INTEGER,
                уровень INTEGER CHECK (уровень >= 1 AND уровень <= 5),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (competency_id) REFERENCES competencies(id)
            )
        ''')

        # Таблица целей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                тип TEXT NOT NULL,
                описание TEXT NOT NULL,
                цель INTEGER NOT NULL,
                текущее INTEGER DEFAULT 0,
                выполнено BOOLEAN DEFAULT FALSE,
                дата_создания DATE DEFAULT CURRENT_DATE
            )
        ''')

        self.conn.commit()

    def init_achievements(self):
        """Инициализация достижений"""
        achievements = [
            ("Первый шаг", "Создана первая запись"),
            ("Командный игрок", "Три и более записи с соавторами"),
            ("Разносторонний", "Записи минимум трёх разных типов"),
            ("Подготовленный год", "Три и более записи за один календарный год"),
            ("Словобог", "Суммарный объём описаний превысил 5000 символов")
        ]

        for name, desc in achievements:
            self.cursor.execute('''
                INSERT OR IGNORE INTO achievements (название, описание)
                VALUES (?, ?)
            ''', (name, desc))

        self.conn.commit()

    # ============ МЕТОДЫ ДЛЯ ЗАПИСЕЙ ============

    def add_entry(self, title, entry_type, date, description, authors):
        """Добавление новой записи"""
        self.cursor.execute('''
            INSERT INTO entries (название, тип, дата, описание, соавторы)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, entry_type, date, description, authors))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_entries(self):
        """Получение всех записей"""
        self.cursor.execute("SELECT * FROM entries ORDER BY дата DESC")
        return self.cursor.fetchall()

    def get_all_entries_with_keywords(self):
        """Получение записей с ключевыми словами"""
        self.cursor.execute('''
            SELECT e.*, GROUP_CONCAT(k.keyword, ', ') as keywords
            FROM entries e
            LEFT JOIN entry_keywords ek ON e.id = ek.entry_id
            LEFT JOIN keywords k ON ek.keyword_id = k.id
            GROUP BY e.id
            ORDER BY e.дата DESC
        ''')
        return self.cursor.fetchall()

    def search_entries(self, search_text):
        """Поиск записей"""
        self.cursor.execute('''
            SELECT e.*, GROUP_CONCAT(k.keyword, ', ') as keywords
            FROM entries e
            LEFT JOIN entry_keywords ek ON e.id = ek.entry_id
            LEFT JOIN keywords k ON ek.keyword_id = k.id
            WHERE LOWER(e.название) LIKE ? OR LOWER(e.описание) LIKE ? OR LOWER(k.keyword) LIKE ?
            GROUP BY e.id
            ORDER BY e.дата DESC
        ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        return self.cursor.fetchall()

    def delete_entry(self, entry_id):
        """Удаление записи"""
        # Удаляем связи с ключевыми словами
        self.cursor.execute("DELETE FROM entry_keywords WHERE entry_id = ?", (entry_id,))
        # Удаляем связи с компетенциями
        self.cursor.execute("DELETE FROM entry_competencies WHERE entry_id = ?", (entry_id,))
        # Удаляем запись
        self.cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()

    # ============ МЕТОДЫ ДЛЯ КЛЮЧЕВЫХ СЛОВ ============

    def add_keyword_to_entry(self, entry_id, keyword):
        """Добавление ключевого слова к записи"""
        # Добавляем ключевое слово если его нет
        self.cursor.execute('''
            INSERT OR IGNORE INTO keywords (keyword) VALUES (?)
        ''', (keyword,))

        # Получаем ID ключевого слова
        self.cursor.execute("SELECT id FROM keywords WHERE keyword = ?", (keyword,))
        keyword_id = self.cursor.fetchone()[0]

        # Создаем связь
        self.cursor.execute('''
            INSERT OR IGNORE INTO entry_keywords (entry_id, keyword_id)
            VALUES (?, ?)
        ''', (entry_id, keyword_id))

        self.conn.commit()

    def get_all_keywords(self):
        """Получение всех ключевых слов"""
        self.cursor.execute("SELECT keyword FROM keywords ORDER BY keyword")
        return [row[0] for row in self.cursor.fetchall()]

    def get_keywords_statistics(self):
        """Статистика по ключевым словам"""
        self.cursor.execute('''
            SELECT k.keyword, COUNT(ek.entry_id) as count
            FROM keywords k
            LEFT JOIN entry_keywords ek ON k.id = ek.keyword_id
            GROUP BY k.id
            HAVING count > 0
            ORDER BY count DESC
        ''')
        return self.cursor.fetchall()

    # ============ МЕТОДЫ ДЛЯ СОАВТОРОВ ============

    def get_authors_statistics(self):
        """Статистика по соавторам"""
        self.cursor.execute('''
            SELECT соавторы, COUNT(*) as count
            FROM entries
            WHERE соавторы IS NOT NULL AND соавторы != ''
            GROUP BY соавторы
            ORDER BY count DESC
        ''')
        return self.cursor.fetchall()

    def count_entries_with_authors(self):
        """Количество записей с соавторами"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM entries 
            WHERE соавторы IS NOT NULL AND соавторы != ''
        ''')
        return self.cursor.fetchone()[0]

    # ============ МЕТОДЫ ДЛЯ ДОСТИЖЕНИЙ ============

    def get_achievements(self):
        """Получение всех достижений"""
        self.cursor.execute('''
            SELECT * FROM achievements ORDER BY 
            CASE WHEN получено THEN 0 ELSE 1 END,
            дата_получения DESC
        ''')
        return self.cursor.fetchall()

    def unlock_achievement(self, achievement_name):
        """Разблокировка достижения"""
        self.cursor.execute('''
            UPDATE achievements 
            SET получено = TRUE, дата_получения = CURRENT_DATE
            WHERE название = ? AND получено = FALSE
        ''', (achievement_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_achievement_status(self, achievement_name):
        """Получение статуса достижения"""
        self.cursor.execute('''
            SELECT получено FROM achievements WHERE название = ?
        ''', (achievement_name,))
        result = self.cursor.fetchone()
        return result[0] if result else False

    def get_total_description_length(self):
        """Общая длина всех описаний"""
        self.cursor.execute('''
            SELECT SUM(LENGTH(описание)) FROM entries
        ''')
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_entry_types_count(self):
        """Количество уникальных типов записей"""
        self.cursor.execute('''
            SELECT COUNT(DISTINCT тип) FROM entries
        ''')
        return self.cursor.fetchone()[0]

    def get_entries_by_year(self, year):
        """Количество записей за год"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM entries 
            WHERE strftime('%Y', дата) = ?
        ''', (str(year),))
        return self.cursor.fetchone()[0]

    # ============ МЕТОДЫ ДЛЯ КОМПЕТЕНЦИЙ ============

    def add_competency_to_entry(self, entry_id, competency_name, level):
        """Добавление компетенции к записи"""
        # Добавляем компетенцию если ее нет
        self.cursor.execute('''
            INSERT OR IGNORE INTO competencies (название) VALUES (?)
        ''', (competency_name,))

        # Получаем ID компетенции
        self.cursor.execute("SELECT id FROM competencies WHERE название = ?", (competency_name,))
        competency_id = self.cursor.fetchone()[0]

        # Создаем связь с уровнем
        self.cursor.execute('''
            INSERT INTO entry_competencies (entry_id, competency_id, уровень)
            VALUES (?, ?, ?)
        ''', (entry_id, competency_id, level))

        self.conn.commit()

    def get_competencies_statistics(self):
        """Статистика по компетенциям"""
        self.cursor.execute('''
            SELECT c.название, 
                   AVG(ec.уровень) as средний_уровень,
                   COUNT(ec.id) as количество_оценок
            FROM competencies c
            LEFT JOIN entry_competencies ec ON c.id = ec.competency_id
            GROUP BY c.id
            HAVING количество_оценок > 0
            ORDER BY средний_уровень DESC
        ''')
        return self.cursor.fetchall()

    def get_recommendations(self):
        """Получение рекомендаций"""
        recommendations = []

        # Находим компетенции с низким уровнем
        self.cursor.execute('''
            SELECT c.название, AVG(ec.уровень) as avg_level
            FROM competencies c
            JOIN entry_competencies ec ON c.id = ec.competency_id
            GROUP BY c.id
            HAVING avg_level < 3
        ''')

        weak_competencies = self.cursor.fetchall()

        for comp_name, avg_level in weak_competencies:
            if "Презентация" in comp_name:
                recommendations.append(
                    f"Вы почти не развиваете компетенцию '{comp_name}'. "
                    f"Рекомендуем выступить на студенческой конференции."
                )
            elif "Команд" in comp_name:
                recommendations.append(
                    f"Компетенция '{comp_name}' требует развития. "
                    f"Участвуйте в групповых проектах."
                )
            elif "Базы данных" in comp_name:
                recommendations.append(
                    f"Для развития '{comp_name}' пройдите курс по SQL."
                )
            else:
                recommendations.append(
                    f"Обратите внимание на компетенцию '{comp_name}' "
                    f"(текущий уровень: {avg_level:.1f}/5)."
                )

        return recommendations

    # ============ МЕТОДЫ ДЛЯ ЦЕЛЕЙ ============

    def add_goal(self, goal_type, description, target):
        """Добавление новой цели"""
        self.cursor.execute('''
            INSERT INTO goals (тип, описание, цель)
            VALUES (?, ?, ?)
        ''', (goal_type, description, target))
        self.conn.commit()

    def get_goals(self):
        """Получение всех целей"""
        self.cursor.execute('''
            SELECT * FROM goals ORDER BY 
            CASE WHEN выполнено THEN 1 ELSE 0 END,
            дата_создания DESC
        ''')
        return self.cursor.fetchall()

    def update_goal_progress(self, goal_id, current_value):
        """Обновление прогресса цели"""
        self.cursor.execute('''
            UPDATE goals 
            SET текущее = ?, 
                выполнено = CASE WHEN ? >= цель THEN TRUE ELSE FALSE END
            WHERE id = ?
        ''', (current_value, current_value, goal_id))
        self.conn.commit()

    # ============ ЗАКРЫТИЕ СОЕДИНЕНИЯ ============

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()