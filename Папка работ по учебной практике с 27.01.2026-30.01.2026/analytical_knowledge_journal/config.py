# config.py
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
NOTES_DIR = BASE_DIR / "notes_md"
EXPORTS_DIR = BASE_DIR / "exports"

# Создание необходимых папок
for directory in [NOTES_DIR, EXPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# Настройки базы данных
DB_CONFIG = {
    'dbname': 'knowledge_journal',
    'user': 'postgres',
    'password': '1111',  # ⚠️ ВАШ ПАРОЛЬ!
    'host': 'localhost',
    'port': '5432'
}

# Настройки приложения
APP_CONFIG = {
    'app_title': 'Аналитический журнал знаний',
    'window_size': '1200x700',
    'default_font': ('Arial', 12),
    'code_font': ('Consolas', 11)
}

print("✅ Config загружен")