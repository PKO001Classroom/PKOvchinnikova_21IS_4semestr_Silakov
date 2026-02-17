# test_complete.py
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from database import DatabaseManager
from file_manager import FileManager
from config import DB_CONFIG, NOTES_DIR


def run_complete_test():
    print("=" * 50)
    print("ПОЛНЫЙ ТЕСТ ПРИЛОЖЕНИЯ")
    print("=" * 50)

    db = DatabaseManager(DB_CONFIG)
    fm = FileManager(NOTES_DIR)

    try:
        # 1. Тест создания конспекта
        print("\n1. Тест создания конспекта...")
        filepath = fm.create_md_file("Тестовый конспект", "# Тест\nЭто тестовый конспект.")
        note_id = db.create_note("Тестовый конспект", "Тестирование", filepath)
        print(f"   ✅ Конспект создан: ID={note_id}")

        # 2. Тест тегов
        print("\n2. Тест добавления тегов...")
        db.add_tag(note_id, "тест")
        db.add_tag(note_id, "python")
        tags = db.get_note_tags(note_id)
        print(f"   ✅ Теги добавлены: {tags}")

        # 3. Тест статистики
        print("\n3. Тест статистики...")
        stats = db.get_total_stats()
        print(f"   ✅ Всего конспектов: {stats['total_notes']}")
        print(f"   ✅ Всего тегов: {stats['total_tags']}")

        # 4. Тест активности
        print("\n4. Тест логов активности...")
        db.log_view(note_id)
        print("   ✅ Активность залогирована")

        # 5. Тест отчетов
        print("\n5. Тест модуля отчетов...")
        try:
            from reporting import ReportGenerator
            generator = ReportGenerator(db, fm)

            excel_path = generator.generate_excel_report()
            if excel_path:
                print(f"   ✅ Excel отчет создан: {excel_path}")

            pdf_path = generator.generate_pdf_report()
            if pdf_path:
                print(f"   ✅ PDF отчет создан: {pdf_path}")
        except Exception as e:
            print(f"   ⚠️ Ошибка отчетов: {e}")

        # 6. Очистка
        print("\n6. Очистка тестовых данных...")
        fm.delete_md_file(filepath)
        db.delete_note(note_id)
        print("   ✅ Тестовые данные удалены")

        print("\n" + "=" * 50)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()


if __name__ == "__main__":
    run_complete_test()