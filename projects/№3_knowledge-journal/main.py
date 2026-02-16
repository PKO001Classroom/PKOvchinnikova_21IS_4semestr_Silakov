# analytical_knowledge_journal/main.py
import sys
import os
from pathlib import Path

print("=" * 50)
print("🚀 Запуск Аналитического журнала знаний")
print("=" * 50)

# Добавляем путь к src в PYTHONPATH
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

print(f"📁 Текущая папка: {current_dir}")
print(f"📂 Папка src: {src_dir}")
print(f"✅ PythonPath: {sys.path}")

try:
    print("\n🔍 Проверка импортов модулей...")

    # Проверяем наличие файлов в src
    files_in_src = os.listdir(src_dir)
    print(f"📄 Файлы в папке src/: {files_in_src}")

    # Импортируем модули
    from database import DatabaseManager

    print("✅ database.py загружен")

    from file_manager import FileManager

    print("✅ file_manager.py загружен")

    from gui import KnowledgeJournalGUI

    print("✅ gui.py загружен")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Проверьте, что все файлы в папке src/")
    input("Нажмите Enter для выхода...")
    sys.exit(1)
except Exception as e:
    print(f"❌ Другая ошибка: {e}")
    import traceback

    traceback.print_exc()
    input("Нажмите Enter для выхода...")
    sys.exit(1)


def main():
    """Основная функция запуска приложения"""
    try:
        print("\n📋 Загрузка конфигурации...")
        import config

        print(f"📁 Папка для конспектов: {config.NOTES_DIR}")
        print(f"📊 Папка для экспорта: {config.EXPORTS_DIR}")

        print("\n🔧 Инициализация базы данных...")
        db_manager = DatabaseManager(config.DB_CONFIG)
        print("✅ База данных подключена")

        print("\n📁 Инициализация файлового менеджера...")
        file_manager = FileManager(config.NOTES_DIR)
        print("✅ Файловый менеджер готов")

        print("\n🖥️ Загрузка графического интерфейса...")
        app = KnowledgeJournalGUI(db_manager, file_manager)
        print("✅ Интерфейс создан")

        print("\n" + "=" * 50)
        print("✅ Приложение успешно запущено!")
        print("=" * 50)

        # Запуск главного цикла Tkinter
        app.run()

    except Exception as e:
        print(f"\n❌ Критическая ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()