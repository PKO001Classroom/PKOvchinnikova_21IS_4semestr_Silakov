# src/file_manager.py
import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime


class FileManager:
    def __init__(self, notes_dir):
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(exist_ok=True)
        print(f"✅ Папка для конспектов: {self.notes_dir}")

    def create_md_file(self, title, content=""):
        try:
            # Создаём имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_title = title.replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = f"{timestamp}_{clean_title}.md"

            filepath = self.notes_dir / filename

            # Стандартное содержимое
            if not content:
                content = f"""# {title}

## 📝 Описание

## 📚 Основные понятия

## 📋 Примеры

## 💡 Выводы

---
*Создано: {datetime.now().strftime("%d.%m.%Y %H:%M")}*
"""

            # Создание файла
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Создан файл: {filepath}")
            return str(filepath.absolute())

        except Exception as e:
            print(f"❌ Ошибка создания файла: {e}")
            raise

    def read_md_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return ""

    def write_md_file(self, filepath, content):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Файл обновлён: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Ошибка записи файла: {e}")
            return False

    def delete_md_file(self, filepath):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Файл удалён: {filepath}")
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка удаления файла: {e}")
            return False

    def open_in_external_editor(self, filepath):
        try:
            system = platform.system()

            if system == "Windows":
                os.startfile(filepath)
            elif system == "Darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])

            print(f"✅ Файл открыт: {filepath}")

        except Exception as e:
            print(f"❌ Ошибка открытия файла: {e}")
            raise