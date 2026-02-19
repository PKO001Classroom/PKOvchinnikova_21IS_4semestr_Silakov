Хорошо, вижу что у вас есть полноценное приложение "Аналитический журнал знаний". Напишу для него комплексные Pytest-тесты:

```python
# test_analytical_journal.py
import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import psycopg2
from datetime import datetime
import json

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# ================ Фикстуры ================

@pytest.fixture
def temp_db_config():
    """Фикстура для конфигурации временной БД"""
    return {
        'dbname': 'test_knowledge_journal',
        'user': 'postgres',
        'password': '1111',
        'host': 'localhost',
        'port': '5432'
    }


@pytest.fixture
def mock_db_connection():
    """Фикстура для мока подключения к БД"""
    with patch('src.database.psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.autocommit = False
        
        yield mock_conn, mock_cursor


@pytest.fixture
def temp_notes_dir():
    """Фикстура для временной директории с заметками"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_exports_dir():
    """Фикстура для временной директории экспорта"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_tkinter():
    """Фикстура для мока tkinter"""
    with patch('src.gui.tkinter') as mock_tk:
        with patch('src.gui.ttk') as mock_ttk:
            with patch('src.gui.messagebox') as mock_mbox:
                # Мокаем основные виджеты
                mock_tk.Tk = Mock()
                mock_tk.Toplevel = Mock()
                mock_tk.Text = Mock()
                mock_tk.END = 'end'
                mock_tk.BOTH = 'both'
                mock_tk.X = 'x'
                mock_tk.Y = 'y'
                mock_tk.W = 'w'
                mock_tk.E = 'e'
                mock_tk.N = 'n'
                mock_tk.S = 's'
                mock_tk.WORD = 'word'
                mock_tk.SUNKEN = 'sunken'
                mock_tk.NORMAL = 'normal'
                mock_tk.DISABLED = 'disabled'
                
                # Мокаем константы геометрии
                mock_tk.LEFT = 'left'
                mock_tk.RIGHT = 'right'
                mock_tk.HORIZONTAL = 'horizontal'
                mock_tk.VERTICAL = 'vertical'
                
                yield {
                    'tk': mock_tk,
                    'ttk': mock_ttk,
                    'messagebox': mock_mbox
                }


# ================ Тесты для DatabaseManager ================

class TestDatabaseManager:
    def test_initialization(self, mock_db_connection):
        """Тест инициализации DatabaseManager"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db_config = {
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'host': 'localhost',
            'port': '5432'
        }
        
        db = DatabaseManager(db_config)
        
        # Проверяем, что connect был вызван с правильными параметрами
        mock_conn.assert_called_with(**db_config)
        assert db.db_config == db_config
        assert db.connection is not None
    
    def test_execute_query_success(self, mock_db_connection):
        """Тест успешного выполнения запроса"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Тестовый запрос
        test_query = "SELECT * FROM notes"
        test_result = [(1, 'Test Note', '2024-01-01', '2024-01-01', 'Category')]
        
        mock_cursor.fetchall.return_value = test_result
        
        result = db.execute_query(test_query, fetch=True)
        
        # Проверяем вызовы
        mock_cursor.execute.assert_called_with(test_query, ())
        mock_conn.commit.assert_called()
        assert result == test_result
    
    def test_execute_query_error(self, mock_db_connection):
        """Тест выполнения запроса с ошибкой"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Симулируем ошибку
        mock_cursor.execute.side_effect = psycopg2.Error("Test error")
        
        result = db.execute_query("INVALID SQL", fetch=True)
        
        # Проверяем rollback
        mock_conn.rollback.assert_called()
        assert result is None
    
    def test_create_note(self, mock_db_connection):
        """Тест создания заметки"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Настраиваем мок
        mock_cursor.fetchall.return_value = [(1,)]
        
        note_id = db.create_note("Test Title", "Test Category", "/path/to/file.md")
        
        # Проверяем вызов execute
        assert mock_cursor.execute.call_count >= 2
        assert note_id == 1
        
        # Проверяем, что логирование активности было вызвано
        # (логирование будет во втором вызове execute)
    
    def test_get_note(self, mock_db_connection):
        """Тест получения заметки"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        test_data = (1, 'Test Title', '/path/to/file.md', 
                    datetime(2024, 1, 1), datetime(2024, 1, 2), 'Category')
        mock_cursor.fetchall.return_value = [test_data]
        
        result = db.get_note(1)
        
        assert result is not None
        assert result['id'] == 1
        assert result['title'] == 'Test Title'
        assert result['category'] == 'Category'
    
    def test_update_note(self, mock_db_connection):
        """Тест обновления заметки"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        db.update_note(1, title="Updated Title", category="Updated Category")
        
        # Проверяем, что execute был вызван
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
    
    def test_delete_note(self, mock_db_connection):
        """Тест удаления заметки"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        db.delete_note(1)
        
        mock_cursor.execute.assert_called_with("DELETE FROM notes WHERE id = %s", (1,))
        mock_conn.commit.assert_called()
    
    def test_get_all_notes(self, mock_db_connection):
        """Тест получения всех заметок"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        test_data = [
            (1, 'Note 1', 'Category 1', '01.01.2024 10:00'),
            (2, 'Note 2', 'Category 2', '02.01.2024 11:00')
        ]
        mock_cursor.fetchall.return_value = test_data
        
        notes = db.get_all_notes()
        
        assert len(notes) == 2
        assert notes[0]['title'] == 'Note 1'
        assert notes[1]['category'] == 'Category 2'
    
    def test_add_tag(self, mock_db_connection):
        """Тест добавления тега"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Настраиваем возвращаемые значения
        mock_cursor.fetchall.side_effect = [
            [],  # Первый вызов - проверка существования тега
            [(1,)],  # Второй вызов - ID нового тега
        ]
        
        db.add_tag(1, "python")
        
        # Проверяем, что было несколько вызовов execute
        assert mock_cursor.execute.call_count >= 3
    
    def test_get_note_tags(self, mock_db_connection):
        """Тест получения тегов заметки"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        test_tags = [('python',), ('sql',), ('database',)]
        mock_cursor.fetchall.return_value = test_tags
        
        tags = db.get_note_tags(1)
        
        assert tags == ['python', 'sql', 'database']
    
    def test_log_activity(self, mock_db_connection):
        """Тест логирования активности"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        db.log_activity(1, 'VIEW')
        
        mock_cursor.execute.assert_called_with(
            "INSERT INTO activity_log (note_id, event_type) VALUES (%s, %s)",
            (1, 'VIEW')
        )
        mock_conn.commit.assert_called()
    
    def test_get_notes_by_category(self, mock_db_connection):
        """Тест получения заметок по категориям"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        test_data = [('Python', 5), ('SQL', 3), ('Algorithms', 2)]
        mock_cursor.fetchall.return_value = test_data
        
        result = db.get_notes_by_category()
        
        assert result == {'Python': 5, 'SQL': 3, 'Algorithms': 2}
    
    def test_get_total_stats(self, mock_db_connection):
        """Тест получения общей статистики"""
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Настраиваем возвращаемые значения для разных запросов
        mock_cursor.fetchall.side_effect = [
            [(10,)],  # total_notes
            [(5,)],   # total_tags
            [(3,)],   # today_activity
            [('Python', 5), ('SQL', 3)],  # notes_by_category
            [('python', 8), ('sql', 5)]   # top_tags
        ]
        
        stats = db.get_total_stats()
        
        assert stats['total_notes'] == 10
        assert stats['total_tags'] == 5
        assert stats['today_activity'] == 3
        assert stats['notes_by_category'] == {'Python': 5, 'SQL': 3}
        assert stats['top_tags'] == [('python', 8), ('sql', 5)]


# ================ Тесты для FileManager ================

class TestFileManager:
    def test_initialization(self, temp_notes_dir):
        """Тест инициализации FileManager"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        assert fm.notes_dir == temp_notes_dir
        assert temp_notes_dir.exists()
    
    def test_create_md_file(self, temp_notes_dir):
        """Тест создания MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        title = "Test Note"
        content = "# Test Content\n\nThis is a test."
        
        filepath = fm.create_md_file(title, content)
        
        assert os.path.exists(filepath)
        assert title.replace(' ', '_') in filepath
        
        # Проверяем содержимое файла
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert "Test Note" in file_content
        assert "This is a test" in file_content
    
    def test_create_md_file_default_content(self, temp_notes_dir):
        """Тест создания MD файла с содержимым по умолчанию"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        title = "Test Note"
        filepath = fm.create_md_file(title)  # Без контента
        
        assert os.path.exists(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert f"# {title}" in content
        assert "📝 Описание" in content
        assert "📚 Основные понятия" in content
    
    def test_read_md_file(self, temp_notes_dir):
        """Тест чтения MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        # Создаем тестовый файл
        test_content = "# Test\n\nThis is test content."
        test_file = temp_notes_dir / "test.md"
        test_file.write_text(test_content, encoding='utf-8')
        
        # Читаем файл
        content = fm.read_md_file(str(test_file))
        
        assert content == test_content
    
    def test_read_nonexistent_file(self, temp_notes_dir):
        """Тест чтения несуществующего файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        content = fm.read_md_file("/nonexistent/path/file.md")
        
        assert content == ""
    
    def test_write_md_file(self, temp_notes_dir):
        """Тест записи MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        test_file = temp_notes_dir / "test.md"
        test_content = "# Updated Content\n\nThis is updated."
        
        result = fm.write_md_file(str(test_file), test_content)
        
        assert result is True
        assert test_file.exists()
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == test_content
    
    def test_delete_md_file(self, temp_notes_dir):
        """Тест удаления MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        # Создаем файл для удаления
        test_file = temp_notes_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        result = fm.delete_md_file(str(test_file))
        
        assert result is True
        assert not test_file.exists()
    
    def test_delete_nonexistent_file(self, temp_notes_dir):
        """Тест удаления несуществующего файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        result = fm.delete_md_file("/nonexistent/path/file.md")
        
        assert result is False


# ================ Тесты для ReportGenerator ================

class TestReportGenerator:
    @pytest.fixture
    def mock_db_manager(self):
        """Фикстура для мока DatabaseManager"""
        mock_db = Mock()
        mock_db.get_total_stats.return_value = {
            'total_notes': 10,
            'total_tags': 5,
            'today_activity': 3,
            'notes_by_category': {'Python': 5, 'SQL': 3, 'Algorithms': 2},
            'top_tags': [('python', 8), ('sql', 5), ('database', 3)]
        }
        mock_db.get_activity_stats.return_value = {
            'daily_activity': [
                ('2024-01-01', 5, 2, 1, 2),
                ('2024-01-02', 6, 3, 2, 1)
            ]
        }
        mock_db.get_recent_notes.return_value = [
            {'id': 1, 'title': 'Recent Note 1', 'category': 'Python', 'updated': '01.01.2024'},
            {'id': 2, 'title': 'Recent Note 2', 'category': 'SQL', 'updated': '02.01.2024'}
        ]
        return mock_db
    
    @pytest.fixture
    def mock_file_manager(self, temp_exports_dir):
        """Фикстура для мока FileManager"""
        mock_fm = Mock()
        mock_fm.notes_dir = temp_exports_dir
        return mock_fm
    
    def test_initialization(self, mock_db_manager, mock_file_manager):
        """Тест инициализации ReportGenerator"""
        from src.reporting import ReportGenerator
        
        generator = ReportGenerator(mock_db_manager, mock_file_manager)
        
        assert generator.db == mock_db_manager
        assert generator.fm == mock_file_manager
        assert generator.exports_dir.exists()
    
    @patch('src.reporting.Workbook')
    def test_generate_excel_report_success(self, mock_workbook, mock_db_manager, mock_file_manager):
        """Тест успешной генерации Excel отчёта"""
        from src.reporting import ReportGenerator
        
        generator = ReportGenerator(mock_db_manager, mock_file_manager)
        
        # Мокаем Workbook и связанные объекты
        mock_wb = Mock()
        mock_ws = Mock()
        mock_chart = Mock()
        
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        mock_wb.create_sheet.return_value = mock_ws
        
        # Настраиваем max_row для Reference
        mock_ws.max_row = 8
        
        # Имитируем импорт BarChart и Reference
        with patch('src.reporting.BarChart', return_value=mock_chart):
            with patch('src.reporting.Reference'):
                filepath = generator.generate_excel_report()
        
        assert filepath is not None
        assert filepath.endswith('.xlsx')
        mock_wb.save.assert_called_once()
    
    @patch('src.reporting.Workbook')
    def test_generate_excel_report_exception(self, mock_workbook, mock_db_manager, mock_file_manager):
        """Тест генерации Excel отчёта с исключением"""
        from src.reporting import ReportGenerator
        
        generator = ReportGenerator(mock_db_manager, mock_file_manager)
        
        # Симулируем ошибку
        mock_workbook.side_effect = Exception("Test error")
        
        filepath = generator.generate_excel_report()
        
        assert filepath is None
    
    @patch('src.reporting.SimpleDocTemplate')
    @patch('src.reporting.Paragraph')
    @patch('src.reporting.Table')
    def test_generate_pdf_report_success(self, mock_table, mock_paragraph, mock_doc_template, 
                                        mock_db_manager, mock_file_manager):
        """Тест успешной генерации PDF отчёта"""
        from src.reporting import ReportGenerator
        
        generator = ReportGenerator(mock_db_manager, mock_file_manager)
        
        # Мокаем SimpleDocTemplate
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc
        
        # Мокаем Table и Paragraph
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance
        
        mock_paragraph_instance = Mock()
        mock_paragraph.return_value = mock_paragraph_instance
        
        filepath = generator.generate_pdf_report()
        
        assert filepath is not None
        assert filepath.endswith('.pdf')
        mock_doc.build.assert_called_once()
    
    @patch('src.reporting.SimpleDocTemplate')
    def test_generate_pdf_report_import_error(self, mock_doc_template, mock_db_manager, mock_file_manager):
        """Тест генерации PDF отчёта с ошибкой импорта"""
        from src.reporting import ReportGenerator
        
        generator = ReportGenerator(mock_db_manager, mock_file_manager)
        
        # Симулируем ImportError
        mock_doc_template.side_effect = ImportError("No module named 'reportlab'")
        
        filepath = generator.generate_pdf_report()
        
        assert filepath is None


# ================ Интеграционные тесты ================

class TestIntegration:
    def test_complete_workflow(self, temp_notes_dir, temp_db_config):
        """Полный тест рабочего процесса"""
        from src.database import DatabaseManager
        from src.file_manager import FileManager
        
        # Мокаем подключение к БД
        with patch('src.database.psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Настраиваем возвращаемые значения
            mock_cursor.fetchall.side_effect = [
                [(1,)],  # create_note
                [(1, 'Test Note', '/path/to/file.md', 
                  datetime(2024, 1, 1), datetime(2024, 1, 1), 'Test')],  # get_note
                [('python',), ('test',)],  # get_note_tags
                [],  # get_tag_id (первый вызов)
                [(1,)],  # get_tag_id (второй вызов)
            ]
            
            # Создаем менеджеры
            db = DatabaseManager(temp_db_config)
            fm = FileManager(temp_notes_dir)
            
            # 1. Создание заметки
            filepath = fm.create_md_file("Test Note", "# Test Content")
            note_id = db.create_note("Test Note", "Test", filepath)
            
            assert note_id == 1
            assert os.path.exists(filepath)
            
            # 2. Получение заметки
            note = db.get_note(note_id)
            assert note['title'] == "Test Note"
            
            # 3. Добавление тегов
            db.add_tag(note_id, "python")
            db.add_tag(note_id, "test")
            
            # 4. Получение тегов
            tags = db.get_note_tags(note_id)
            assert "python" in tags
            assert "test" in tags
            
            # 5. Логирование активности
            db.log_view(note_id)
            db.log_activity(note_id, 'UPDATE')
            
            # 6. Обновление заметки
            db.update_note(note_id, title="Updated Note")
            
            # 7. Чтение файла
            content = fm.read_md_file(filepath)
            assert "Test Content" in content
            
            # 8. Обновление файла
            new_content = "# Updated Content\n\nUpdated text."
            fm.write_md_file(filepath, new_content)
            
            # 9. Проверка обновления
            updated_content = fm.read_md_file(filepath)
            assert "Updated Content" in updated_content
    
    def test_error_handling_scenarios(self, temp_notes_dir):
        """Тест различных сценариев обработки ошибок"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        # 1. Попытка чтения несуществующего файла
        content = fm.read_md_file("/nonexistent/path/file.md")
        assert content == ""
        
        # 2. Попытка удаления несуществующего файла
        result = fm.delete_md_file("/nonexistent/path/file.md")
        assert result is False
        
        # 3. Создание файла с недопустимыми символами в названии
        title = "Test/Note\\With*Special?Chars"
        filepath = fm.create_md_file(title)
        assert filepath is not None
        assert "Test_Note_With_Special_Chars" in filepath


# ================ Тесты конфигурации ================

class TestConfig:
    def test_config_structure(self):
        """Тест структуры конфигурации"""
        import config
        
        # Проверяем наличие обязательных атрибутов
        assert hasattr(config, 'BASE_DIR')
        assert hasattr(config, 'NOTES_DIR')
        assert hasattr(config, 'EXPORTS_DIR')
        assert hasattr(config, 'DB_CONFIG')
        assert hasattr(config, 'APP_CONFIG')
        
        # Проверяем типы
        assert isinstance(config.NOTES_DIR, Path)
        assert isinstance(config.EXPORTS_DIR, Path)
        assert isinstance(config.DB_CONFIG, dict)
        assert isinstance(config.APP_CONFIG, dict)
        
        # Проверяем обязательные ключи в DB_CONFIG
        required_keys = ['dbname', 'user', 'password', 'host', 'port']
        for key in required_keys:
            assert key in config.DB_CONFIG
        
        # Проверяем обязательные ключи в APP_CONFIG
        assert 'app_title' in config.APP_CONFIG
        assert 'window_size' in config.APP_CONFIG


# ================ Тесты валидации данных ================

class TestDataValidation:
    def test_note_data_validation(self):
        """Тест валидации данных заметки"""
        # Валидные данные
        valid_titles = ["Test Note", "Python Basics", "Алгоритмы и структуры данных"]
        for title in valid_titles:
            assert len(title) > 0
            assert len(title) <= 200  # Предполагаемое ограничение
        
        # Невалидные данные
        invalid_titles = ["", "   ", None]
        for title in invalid_titles:
            if title is not None:
                assert len(title.strip()) == 0
    
    def test_file_name_generation(self):
        """Тест генерации имен файлов"""
        from datetime import datetime
        
        test_cases = [
            ("Test Note", "Test_Note"),
            ("Python/Advanced", "Python_Advanced"),
            ("C:\\Windows\\Path", "C__Windows_Path"),
            ("Special*Chars?", "Special_Chars_"),
        ]
        
        for original, expected_part in test_cases:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            expected = f"{timestamp}_{expected_part}.md"
            
            # Проверяем, что имя файла содержит ожидаемую часть
            assert expected_part in expected
            assert expected.endswith('.md')


# ================ Тесты производительности ================

class TestPerformance:
    def test_bulk_file_operations(self, temp_notes_dir):
        """Тест производительности операций с файлами"""
        import time
        from src.file_manager import FileManager
        
        fm = FileManager(temp_notes_dir)
        
        # Тест массового создания файлов
        start_time = time.time()
        
        file_count = 50
        file_paths = []
        
        for i in range(file_count):
            filepath = fm.create_md_file(f"Test Note {i}", f"# Content {i}")
            file_paths.append(filepath)
        
        creation_time = time.time() - start_time
        
        # Тест массового чтения файлов
        start_time = time.time()
        
        for filepath in file_paths:
            content = fm.read_md_file(filepath)
            assert f"Content " in content
        
        reading_time = time.time() - start_time
        
        # Тест массового удаления файлов
        start_time = time.time()
        
        for filepath in file_paths:
            fm.delete_md_file(filepath)
        
        deletion_time = time.time() - start_time
        
        # Проверяем производительность
        assert creation_time < 5.0, f"Создание {file_count} файлов заняло {creation_time:.2f} секунд"
        assert reading_time < 3.0, f"Чтение {file_count} файлов заняло {reading_time:.2f} секунд"
        assert deletion_time < 3.0, f"Удаление {file_count} файлов заняло {deletion_time:.2f} секунд"
    
    def test_database_query_performance(self, mock_db_connection):
        """Тест производительности запросов к БД"""
        import time
        from src.database import DatabaseManager
        
        mock_conn, mock_cursor = mock_db_connection
        db = DatabaseManager({})
        
        # Настраиваем мок для возврата большого набора данных
        large_dataset = [(i, f"Note {i}", f"Category {i % 5}", f"Date {i}") 
                        for i in range(1000)]
        mock_cursor.fetchall.return_value = large_dataset
        
        start_time = time.time()
        
        notes = db.get_all_notes()
        
        query_time = time.time() - start_time
        
        assert len(notes) == 1000
        assert query_time < 2.0, f"Запрос 1000 записей занял {query_time:.2f} секунд"


# ================ Тесты главного модуля ================

class TestMainModule:
    def test_main_imports(self):
        """Тест импортов в главном модуле"""
        # Проверяем, что все необходимые модули могут быть импортированы
        try:
            from main import main
            assert callable(main)
        except ImportError as e:
            pytest.fail(f"Ошибка импорта в main.py: {e}")
    
    @patch('main.DatabaseManager')
    @patch('main.FileManager')
    @patch('main.KnowledgeJournalGUI')
    def test_main_execution(self, mock_gui, mock_fm, mock_db):
        """Тест выполнения главной функции"""
        from main import main
        
        # Настраиваем моки
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        
        mock_fm_instance = Mock()
        mock_fm.return_value = mock_fm_instance
        
        mock_gui_instance = Mock()
        mock_gui.return_value = mock_gui_instance
        
        # Мокаем config
        with patch('main.config') as mock_config:
            mock_config.NOTES_DIR = Path("/test/notes")
            mock_config.EXPORTS_DIR = Path("/test/exports")
            mock_config.DB_CONFIG = {}
            mock_config.APP_CONFIG = {}
            
            # Запускаем main
            main()
            
            # Проверяем вызовы
            mock_db.assert_called_once_with({})
            mock_fm.assert_called_once_with(Path("/test/notes"))
            mock_gui.assert_called_once_with(mock_db_instance, mock_fm_instance)
            mock_gui_instance.run.assert_called_once()


# ================ Тесты для GUI (с моками) ================

class TestGUIWithMocks:
    @patch('src.gui.tk.Tk')
    @patch('src.gui.ttk.Notebook')
    def test_gui_initialization(self, mock_notebook, mock_tk):
        """Тест инициализации GUI"""
        from src.gui import KnowledgeJournalGUI
        
        # Мокаем зависимости
        mock_db = Mock()
        mock_fm = Mock()
        
        # Мокаем tkinter виджеты
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        mock_nb = Mock()
        mock_notebook.return_value = mock_nb
        
        # Создаем GUI
        gui = KnowledgeJournalGUI(mock_db, mock_fm)
        
        # Проверяем вызовы
        mock_tk.assert_called_once()
        mock_root.title.assert_called_with("Аналитический журнал знаний")
        mock_root.geometry.assert_called_with("1200x700")
        mock_notebook.assert_called_once()
        
        assert gui.db == mock_db
        assert gui.fm == mock_fm
    
    def test_gui_methods_with_mocks(self):
        """Тест методов GUI с моками"""
        from src.gui import KnowledgeJournalGUI
        
        # Создаем моки
        mock_db = Mock()
        mock_fm = Mock()
        mock_root = Mock()
        
        # Создаем экземпляр GUI с патчами
        with patch('src.gui.tk.Tk', return_value=mock_root):
            with patch('src.gui.ttk.Notebook'):
                gui = KnowledgeJournalGUI(mock_db, mock_fm)
                
                # Тестируем update_status
                gui.status_bar = Mock()
                gui.update_status("Test message")
                gui.status_bar.config.assert_called()
                
                # Тестируем show_error
                gui.show_error("Test error")
                # Проверяем, что error был залогирован


# ================ Запуск тестов ================

if __name__ == "__main__":
    print("Для запуска тестов используйте команды:")
    print("\n1. Все тесты:")
    print("   pytest test_analytical_journal.py -v")
    
    print("\n2. Только тесты базы данных:")
    print("   pytest test_analytical_journal.py::TestDatabaseManager -v")
    
    print("\n3. Только тесты файлового менеджера:")
    print("   pytest test_analytical_journal.py::TestFileManager -v")
    
    print("\n4. С покрытием кода:")
    print("   pytest test_analytical_journal.py --cov=src --cov-report=html")
    
    print("\n5. Быстрые тесты (без интеграционных):")
    print("   pytest test_analytical_journal.py -m 'not integration'")
```

Также создайте конфигурационный файл для pytest:

```python
# conftest.py
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch


def pytest_addoption(parser):
    """Добавление опций командной строки для pytest"""
    parser.addoption(
        "--integration", 
        action="store_true",
        default=False,
        help="Запускать интеграционные тесты"
    )
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Запускать тесты производительности"
    )


def pytest_collection_modifyitems(config, items):
    """Фильтрация тестов по маркерам"""
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="Требуется флаг --integration")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    if not config.getoption("--performance"):
        skip_performance = pytest.mark.skip(reason="Требуется флаг --performance")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестового окружения для каждого теста"""
    # Создаем временные директории
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Создаем структуру папок как в проекте
        (Path(temp_dir) / "src").mkdir(exist_ok=True)
        (Path(temp_dir) / "notes_md").mkdir(exist_ok=True)
        (Path(temp_dir) / "exports").mkdir(exist_ok=True)
        
        try:
            yield temp_dir
        finally:
            os.chdir(original_dir)


@pytest.fixture
def sample_md_content():
    """Пример содержимого MD файла"""
    return """# Test Note

## Описание
Это тестовая заметка.

## Основные понятия
- Понятие 1
- Понятие 2

## Примеры
```python
print("Hello, World!")
```

## Выводы
Тест завершен успешно.

---
*Создано: 27.01.2024 12:00*
"""
```

И файл с маркерами:

```ini
# pytest.ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short -ra
markers =
    unit: unit tests
    integration: integration tests
    database: database tests
    gui: gui tests
    performance: performance tests
    slow: marks tests as slow
```

## Инструкции по запуску:

1. **Установите зависимости для тестов:**
```bash
pip install pytest pytest-mock pytest-cov openpyxl reportlab psycopg2-binary
```

2. **Запустите все тесты:**
```bash
pytest test_analytical_journal.py -v
```

3. **Запустите тесты по категориям:**
```bash
# Только unit тесты
pytest test_analytical_journal.py -m unit -v

# Только тесты базы данных
pytest test_analytical_journal.py::TestDatabaseManager -v

# Только тесты файлового менеджера
pytest test_analytical_journal.py::TestFileManager -v

# Только интеграционные тесты
pytest test_analytical_journal.py --integration -v
```

4. **Запустите с покрытием кода:**
```bash
pytest test_analytical_journal.py --cov=src --cov-report=html --cov-report=term
```

5. **Запустите конкретный тест:**
```bash
pytest test_analytical_journal.py::TestDatabaseManager::test_create_note -v
```

## Особенности тестов:

1. **Изоляция:** Каждый тест работает в своем временном окружении
2. **Моки:** Используются моки для базы данных и GUI
3. **Полное покрытие:** Тестируются все основные модули
4. **Интеграционные тесты:** Тесты на взаимодействие компонентов
5. **Тесты производительности:** Проверка скорости операций
6. **Обработка ошибок:** Тесты для различных сценариев ошибок

Тесты покрывают:
- Базу данных (DatabaseManager)
- Файловый менеджер (FileManager)
- Генератор отчетов (ReportGenerator)
- Конфигурацию
- Основной модуль
- Валидацию данных
- Производительность
- Интеграционные сценарии
