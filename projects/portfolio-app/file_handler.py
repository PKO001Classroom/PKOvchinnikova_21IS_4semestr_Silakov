# file_handler.py
import os
import re
import subprocess
import platform


class FileHandler:
    def __init__(self, base_dir="portfolio_md"):
        self.base_dir = base_dir
        self.ensure_directory()

    def ensure_directory(self):
        """Создание директории если не существует"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            print(f"Создана папка: {self.base_dir}")

    def sanitize_filename(self, title):
        """Очистка названия для имени файла"""
        # Удаляем недопустимые символы
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.replace(' ', '_')
        filename = filename.replace('\n', '_')

        # Ограничиваем длину
        if len(filename) > 50:
            filename = filename[:50]

        # Добавляем timestamp для уникальности
        import time
        timestamp = str(int(time.time()))[-4:]
        filename = f"{filename}_{timestamp}.md"

        return filename

    def create_md_file(self, title, content=""):
        """Создание нового .md файла"""
        filename = self.sanitize_filename(title)
        filepath = os.path.join(self.base_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(content)

            print(f"Создан файл: {filepath}")
            return filepath

        except Exception as e:
            print(f"Ошибка создания файла: {e}")
            raise

    def read_md_file(self, filepath):
        """Чтение содержимого .md файла"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Убираем заголовок если он есть
                lines = content.split('\n')
                if lines[0].startswith('# '):
                    return '\n'.join(lines[2:])  # Пропускаем заголовок и пустую строку
                return content
            return ""

        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return ""

    def update_md_file(self, filepath, content):
        """Обновление содержимого .md файла"""
        try:
            # Получаем оригинальное название из первой строки
            original_title = ""
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        original_title = first_line[2:]

            with open(filepath, 'w', encoding='utf-8') as f:
                if original_title:
                    f.write(f"# {original_title}\n\n")
                f.write(content)

            print(f"Обновлен файл: {filepath}")

        except Exception as e:
            print(f"Ошибка обновления файла: {e}")
            raise

    def open_file(self, filepath):
        """Открытие файла во внешнем редакторе"""
        try:
            if not os.path.exists(filepath):
                print(f"Файл не найден: {filepath}")
                return False

            system = platform.system()

            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])

            print(f"Открыт файл: {filepath}")
            return True

        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
            return False


# Для тестирования
if __name__ == "__main__":
    fh = FileHandler()
    print("Тест FileHandler: OK")