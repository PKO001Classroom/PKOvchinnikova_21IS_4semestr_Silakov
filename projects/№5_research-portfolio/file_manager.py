# file_manager.py
import os
import re
import webbrowser
import markdown
from datetime import datetime


class FileManager:
    def __init__(self, base_dir="portfolio_md"):
        self.base_dir = base_dir
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        """Создание директории, если она не существует"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def sanitize_filename(self, title):
        """Очистка названия от недопустимых символов"""
        if not title:
            return f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Удаляем недопустимые символы для файлов
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Заменяем пробелы на подчеркивания
        filename = re.sub(r'\s+', '_', filename)
        # Убираем лишние символы в начале и конце
        filename = filename.strip('._')

        # Ограничиваем длину
        if len(filename) > 100:
            filename = filename[:100]

        return filename

    def create_md_file(self, entry_id, title, content=""):
        """Создание Markdown файла"""
        try:
            filename = self.sanitize_filename(title)
            file_path = os.path.join(self.base_dir, f"{filename}_{entry_id}.md")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Файл создан: {file_path}")
            return file_path
        except Exception as e:
            print(f"Ошибка создания файла: {e}")
            return None

    def read_md_file(self, file_path):
        """Чтение содержимого Markdown файла"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return ""

    def update_md_file(self, file_path, content):
        """Обновление содержимого Markdown файла"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Файл обновлен: {file_path}")
            return True
        except Exception as e:
            print(f"Ошибка обновления файла: {e}")
            return False

    def delete_md_file(self, file_path):
        """Удаление Markdown файла"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Файл удален: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False

    def open_md_file_external(self, file_path):
        """Открытие файла во внешнем редакторе или браузере"""
        try:
            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                return False

            # Читаем содержимое
            content = self.read_md_file(file_path)

            # Создаем HTML из Markdown
            html_content = markdown.markdown(content)

            # Создаем полный HTML документ
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{os.path.basename(file_path)}</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 40px; 
                        line-height: 1.6;
                        background-color: #f5f5f5;
                    }}
                    .content {{
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                    h2 {{ color: #555; }}
                    code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                    pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    blockquote {{ border-left: 4px solid #4CAF50; padding-left: 15px; margin-left: 0; color: #666; }}
                </style>
            </head>
            <body>
                <div class="content">
                    <h1>{os.path.basename(file_path).replace('.md', '')}</h1>
                    {html_content}
                </div>
            </body>
            </html>
            """

            # Создаем временный HTML файл
            temp_html = file_path.replace('.md', '.html')
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(full_html)

            # Открываем в браузере
            webbrowser.open(f'file://{os.path.abspath(temp_html)}')
            print(f"Файл открыт в браузере: {temp_html}")
            return True

        except Exception as e:
            print(f"Ошибка открытия файла: {e}")

            # Пробуем открыть в стандартном редакторе
            try:
                os.startfile(file_path)
                return True
            except:
                return False


# Глобальный экземпляр для использования
file_manager = FileManager()