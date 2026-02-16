# src/database.py
import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.connect()
        print(f"✅ Подключение к БД: {db_config['dbname']}")

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = False
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                self.connection.commit()
                return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Ошибка выполнения запроса: {e}")
            return None

    # БАЗОВЫЕ МЕТОДЫ
    def create_note(self, title, category, file_path):
        query = """
        INSERT INTO notes (title, category, file_path, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        now = datetime.now()
        result = self.execute_query(query, (title, category, file_path, now, now), fetch=True)
        note_id = result[0][0] if result else None

        if note_id:
            self.log_activity(note_id, 'CREATE')

        return note_id

    def get_note(self, note_id):
        query = "SELECT * FROM notes WHERE id = %s"
        result = self.execute_query(query, (note_id,), fetch=True)
        if result:
            return {
                'id': result[0][0],
                'title': result[0][1],
                'file_path': result[0][2],
                'created_at': result[0][3],
                'updated_at': result[0][4],
                'category': result[0][5]
            }
        return None

    def update_note(self, note_id, title=None, category=None):
        updates = []
        params = []

        if title:
            updates.append("title = %s")
            params.append(title)
        if category:
            updates.append("category = %s")
            params.append(category)

        if not updates:
            return

        params.append(note_id)
        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = %s"
        self.execute_query(query, tuple(params))
        self.log_activity(note_id, 'UPDATE')

    def delete_note(self, note_id):
        query = "DELETE FROM notes WHERE id = %s"
        self.execute_query(query, (note_id,))

    def get_all_notes(self):
        query = """
        SELECT id, title, category, 
               TO_CHAR(updated_at, 'DD.MM.YYYY HH24:MI') as updated
        FROM notes 
        ORDER BY updated_at DESC
        """
        result = self.execute_query(query, fetch=True)

        notes = []
        if result:
            for row in result:
                notes.append({
                    'id': row[0],
                    'title': row[1],
                    'category': row[2],
                    'updated': row[3]
                })
        return notes

    # ТЕГИ
    def add_tag(self, note_id, tag_name):
        # Создаём тег
        tag_query = """
        INSERT INTO tags (name) 
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
        RETURNING id
        """
        self.execute_query(tag_query, (tag_name,))

        # Получаем ID тега
        get_tag_query = "SELECT id FROM tags WHERE name = %s"
        result = self.execute_query(get_tag_query, (tag_name,), fetch=True)
        if not result:
            return

        tag_id = result[0][0]

        # Связываем
        link_query = """
        INSERT INTO note_tags (note_id, tag_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """
        self.execute_query(link_query, (note_id, tag_id))

    def get_note_tags(self, note_id):
        query = """
        SELECT t.name 
        FROM tags t
        JOIN note_tags nt ON t.id = nt.tag_id
        WHERE nt.note_id = %s
        """
        result = self.execute_query(query, (note_id,), fetch=True)
        return [row[0] for row in result] if result else []

    def remove_tag(self, note_id, tag_name):
        query = """
        DELETE FROM note_tags 
        WHERE note_id = %s AND tag_id = (
            SELECT id FROM tags WHERE name = %s
        )
        """
        self.execute_query(query, (note_id, tag_name))

    # АКТИВНОСТЬ
    def log_activity(self, note_id, event_type):
        query = """
        INSERT INTO activity_log (note_id, event_type)
        VALUES (%s, %s)
        """
        self.execute_query(query, (note_id, event_type))

    def log_view(self, note_id):
        self.log_activity(note_id, 'VIEW')

    # СТАТИСТИКА
    def get_notes_by_category(self):
        query = """
        SELECT category, COUNT(*) as count
        FROM notes
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        """
        result = self.execute_query(query, fetch=True)
        return {row[0]: row[1] for row in result} if result else {}

    def get_activity_stats(self, days=30):
        query = """
        SELECT DATE(event_time) as date, 
               COUNT(*) as total,
               SUM(CASE WHEN event_type = 'CREATE' THEN 1 ELSE 0 END) as creates,
               SUM(CASE WHEN event_type = 'UPDATE' THEN 1 ELSE 0 END) as updates,
               SUM(CASE WHEN event_type = 'VIEW' THEN 1 ELSE 0 END) as views
        FROM activity_log
        WHERE event_time >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY DATE(event_time)
        ORDER BY date
        """
        result = self.execute_query(query, (days,), fetch=True)
        return {
            'daily_activity': result if result else []
        }

    def get_top_tags(self, limit=5):
        query = """
        SELECT t.name, COUNT(nt.note_id) as usage_count
        FROM tags t
        JOIN note_tags nt ON t.id = nt.tag_id
        GROUP BY t.id, t.name
        ORDER BY usage_count DESC
        LIMIT %s
        """
        result = self.execute_query(query, (limit,), fetch=True)
        return result if result else []

    def get_recent_notes(self, limit=5):
        query = """
        SELECT id, title, category, 
               TO_CHAR(updated_at, 'DD.MM.YYYY') as updated
        FROM notes
        ORDER BY updated_at DESC
        LIMIT %s
        """
        result = self.execute_query(query, (limit,), fetch=True)

        notes = []
        if result:
            for row in result:
                notes.append({
                    'id': row[0],
                    'title': row[1],
                    'category': row[2],
                    'updated': row[3]
                })
        return notes

    def get_total_stats(self):
        # Общее количество
        query_total = "SELECT COUNT(*) FROM notes"
        total_result = self.execute_query(query_total, fetch=True)
        total_notes = total_result[0][0] if total_result else 0

        # Теги
        query_tags = "SELECT COUNT(*) FROM tags"
        tags_result = self.execute_query(query_tags, fetch=True)
        total_tags = tags_result[0][0] if tags_result else 0

        # Активность сегодня
        query_today = """
        SELECT COUNT(*) 
        FROM activity_log 
        WHERE DATE(event_time) = CURRENT_DATE
        """
        today_result = self.execute_query(query_today, fetch=True)
        today_activity = today_result[0][0] if today_result else 0

        return {
            'total_notes': total_notes,
            'total_tags': total_tags,
            'today_activity': today_activity,
            'notes_by_category': self.get_notes_by_category(),
            'top_tags': self.get_top_tags(5)
        }

    def disconnect(self):
        if self.connection:
            self.connection.close()