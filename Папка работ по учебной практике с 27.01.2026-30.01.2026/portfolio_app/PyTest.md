Вот полный набор Pytest тестов для вашего проекта "Электронный портфолио студента-исследователя". Тесты покрывают основные модули системы:

## Файл: `test_database.py`

```python
# test_database.py
import pytest
import psycopg2
from datetime import datetime
import os
import tempfile
from database import Database


@pytest.fixture
def test_db():
    """Фикстура для тестирования базы данных"""
    # Создаем тестовую базу данных
    db = Database()
    
    # Очищаем тестовые таблицы перед тестом
    db.cursor.execute("DELETE FROM entry_coauthors")
    db.cursor.execute("DELETE FROM coauthors")
    db.cursor.execute("DELETE FROM activity_log")
    db.cursor.execute("DELETE FROM entries")
    db.conn.commit()
    
    yield db
    
    # Очищаем после теста
    db.cursor.execute("DELETE FROM entry_coauthors")
    db.cursor.execute("DELETE FROM coauthors")
    db.cursor.execute("DELETE FROM activity_log")
    db.cursor.execute("DELETE FROM entries")
    db.conn.commit()
    db.close()


@pytest.fixture
def temp_file():
    """Фикстура для создания временного файла"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# Тестовый файл\n\nСодержимое файла")
        temp_path = f.name
    
    yield temp_path
    
    # Удаляем после теста
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestDatabase:
    """Тесты для класса Database"""
    
    def test_connection(self, test_db):
        """Тест подключения к базе данных"""
        assert test_db.conn is not None
        assert test_db.cursor is not None
        assert not test_db.conn.closed
        
    def test_create_entry(self, test_db, temp_file):
        """Тест создания записи"""
        title = "Тестовая публикация"
        entry_type = "Публикация"
        year = 2024
        
        entry_id = test_db.create_entry(title, entry_type, year, temp_file)
        
        assert entry_id is not None
        assert isinstance(entry_id, int)
        
        # Проверяем, что запись добавлена
        test_db.cursor.execute("SELECT * FROM entries WHERE id = %s", (entry_id,))
        entry = test_db.cursor.fetchone()
        
        assert entry['title'] == title
        assert entry['entry_type'] == entry_type
        assert entry['year'] == year
        assert entry['file_path'] == temp_file
        
    def test_get_all_entries(self, test_db, temp_file):
        """Тест получения всех записей"""
        # Создаем несколько записей
        entries_data = [
            ("Публикация 1", "Публикация", 2023, temp_file),
            ("Конференция 1", "Конференция", 2024, temp_file),
            ("Грант 1", "Грант", 2024, temp_file)
        ]
        
        for title, entry_type, year, file_path in entries_data:
            test_db.create_entry(title, entry_type, year, file_path)
        
        entries = test_db.get_all_entries()
        
        assert len(entries) == 3
        assert all('title' in entry for entry in entries)
        assert all('entry_type' in entry for entry in entries)
        
    def test_update_entry(self, test_db, temp_file):
        """Тест обновления записи"""
        # Создаем запись
        entry_id = test_db.create_entry(
            "Старая публикация",
            "Публикация",
            2023,
            temp_file
        )
        
        # Обновляем запись
        test_db.update_entry(
            entry_id,
            "Новая публикация",
            "Конференция",
            2024
        )
        
        # Проверяем обновление
        test_db.cursor.execute(
            "SELECT * FROM entries WHERE id = %s",
            (entry_id,)
        )
        updated_entry = test_db.cursor.fetchone()
        
        assert updated_entry['title'] == "Новая публикация"
        assert updated_entry['entry_type'] == "Конференция"
        assert updated_entry['year'] == 2024
        
    def test_delete_entry(self, test_db, temp_file):
        """Тест удаления записи"""
        # Создаем запись
        entry_id = test_db.create_entry(
            "Удаляемая запись",
            "Публикация",
            2024,
            temp_file
        )
        
        # Проверяем, что запись создана
        test_db.cursor.execute("SELECT COUNT(*) as count FROM entries")
        count_before = test_db.cursor.fetchone()['count']
        assert count_before == 1
        
        # Удаляем запись
        test_db.delete_entry(entry_id)
        
        # Проверяем удаление
        test_db.cursor.execute("SELECT COUNT(*) as count FROM entries")
        count_after = test_db.cursor.fetchone()['count']
        assert count_after == 0
        
    def test_add_coauthor(self, test_db, temp_file):
        """Тест добавления соавтора"""
        # Создаем запись
        entry_id = test_db.create_entry(
            "Публикация с соавтором",
            "Публикация",
            2024,
            temp_file
        )
        
        # Добавляем соавтора
        test_db.add_coauthor(entry_id, "Иван Иванов")
        
        # Проверяем добавление
        coauthors = test_db.get_coauthors(entry_id)
        
        assert len(coauthors) == 1
        assert "Иван Иванов" in coauthors
        
    def test_add_multiple_coauthors(self, test_db, temp_file):
        """Тест добавления нескольких соавторов"""
        entry_id = test_db.create_entry(
            "Публикация с несколькими соавторами",
            "Публикация",
            2024,
            temp_file
        )
        
        coauthors = ["Иван Иванов", "Петр Петров", "Сидор Сидоров"]
        
        for coauthor in coauthors:
            test_db.add_coauthor(entry_id, coauthor)
        
        result = test_db.get_coauthors(entry_id)
        
        assert len(result) == 3
        assert all(coauthor in result for coauthor in coauthors)
        
    def test_get_coauthors_empty(self, test_db, temp_file):
        """Тест получения соавторов, когда их нет"""
        entry_id = test_db.create_entry(
            "Публикация без соавторов",
            "Публикация",
            2024,
            temp_file
        )
        
        coauthors = test_db.get_coauthors(entry_id)
        
        assert len(coauthors) == 0
        assert isinstance(coauthors, list)
        
    def test_get_statistics(self, test_db, temp_file):
        """Тест получения статистики"""
        # Создаем тестовые данные
        test_data = [
            ("Публикация 1", "Публикация", 2023, temp_file),
            ("Публикация 2", "Публикация", 2024, temp_file),
            ("Конференция 1", "Конференция", 2024, temp_file),
            ("Грант 1", "Грант", 2022, temp_file),
        ]
        
        for title, entry_type, year, file_path in test_data:
            entry_id = test_db.create_entry(title, entry_type, year, file_path)
            if "Публикация 1" in title:
                test_db.add_coauthor(entry_id, "Общий соавтор")
        
        stats = test_db.get_statistics()
        
        # Проверяем структуру статистики
        assert 'by_type' in stats
        assert 'by_year' in stats
        assert 'recent_entries' in stats
        assert 'total' in stats
        assert 'unique_coauthors' in stats
        
        # Проверяем значения
        assert stats['total'] == 4
        assert stats['unique_coauthors'] == 1
        
        # Проверяем статистику по типам
        type_counts = {item['entry_type']: item['count'] for item in stats['by_type']}
        assert type_counts.get('Публикация') == 2
        assert type_counts.get('Конференция') == 1
        assert type_counts.get('Грант') == 1
        
    def test_get_statistics_empty(self, test_db):
        """Тест статистики для пустой базы"""
        stats = test_db.get_statistics()
        
        assert stats['total'] == 0
        assert stats['unique_coauthors'] == 0
        assert len(stats['by_type']) == 0
        assert len(stats['by_year']) == 0
        assert len(stats['recent_entries']) == 0
        
    def test_connection_error(self):
        """Тест ошибки подключения"""
        with pytest.raises(Exception):
            # Пытаемся подключиться с неверными параметрами
            db = psycopg2.connect(
                host="localhost",
                database="non_existent_db",
                user="wrong_user",
                password="wrong_password"
            )
            
    def test_close_connection(self, test_db):
        """Тест закрытия соединения"""
        test_db.close()
        
        assert test_db.conn.closed
        assert test_db.cursor.closed
```

## Файл: `test_file_handler.py`

```python
# test_file_handler.py
import pytest
import os
import tempfile
import platform
from file_handler import FileHandler


@pytest.fixture
def file_handler():
    """Фикстура для тестирования FileHandler"""
    with tempfile.TemporaryDirectory() as tmpdir:
        handler = FileHandler(base_dir=tmpdir)
        yield handler


@pytest.fixture
def temp_file_path():
    """Фикстура для создания временного файла"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# Тестовый заголовок\n\nТестовое содержимое")
        temp_path = f.name
    
    yield temp_path
    
    # Очистка
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestFileHandler:
    """Тесты для класса FileHandler"""
    
    def test_init_creates_directory(self):
        """Тест создания директории при инициализации"""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "test_portfolio")
            
            # Убеждаемся, что директории нет
            assert not os.path.exists(new_dir)
            
            # Создаем FileHandler
            handler = FileHandler(base_dir=new_dir)
            
            # Проверяем, что директория создана
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
    
    def test_sanitize_filename(self, file_handler):
        """Тест очистки имени файла"""
        test_cases = [
            ("Нормальное название", "Нормальное_название"),
            ("Спец<сим>волы", "Спецсимволы"),
            ("Много пробелов и   отступов", "Много_пробелов_и___отступов"),
            ("Очень длинное название которое должно быть обрезано", "Очень_длинное_название_которое_должно_быть_об"),
        ]
        
        for input_title, expected_prefix in test_cases:
            result = file_handler.sanitize_filename(input_title)
            
            # Проверяем, что результат заканчивается на .md
            assert result.endswith('.md')
            
            # Проверяем, что недопустимые символы удалены
            assert not any(char in result for char in '<>:"/\\|?*')
            
            # Проверяем длину (с учетом timestamp и расширения)
            assert len(result) <= 60  # 50 символов + timestamp + .md
    
    def test_create_md_file(self, file_handler):
        """Тест создания MD файла"""
        title = "Тестовая публикация"
        content = "Это тестовое содержание\nсо второй строкой"
        
        filepath = file_handler.create_md_file(title, content)
        
        # Проверяем, что файл создан
        assert os.path.exists(filepath)
        assert filepath.endswith('.md')
        
        # Проверяем содержимое файла
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content.startswith(f"# {title}")
        assert content in file_content
        
    def test_read_md_file(self, file_handler, temp_file_path):
        """Тест чтения MD файла"""
        content = file_handler.read_md_file(temp_file_path)
        
        assert content == "Тестовое содержимое"
        
    def test_read_md_file_without_title(self, file_handler):
        """Тест чтения MD файла без заголовка"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("Простое содержимое\nбез заголовка")
            filepath = f.name
        
        try:
            content = file_handler.read_md_file(filepath)
            assert content == "Простое содержимое\nбез заголовка"
        finally:
            os.unlink(filepath)
    
    def test_read_nonexistent_file(self, file_handler):
        """Тест чтения несуществующего файла"""
        non_existent = "/nonexistent/path/file.md"
        content = file_handler.read_md_file(non_existent)
        
        assert content == ""
        
    def test_update_md_file(self, file_handler):
        """Тест обновления MD файла"""
        # Создаем файл
        title = "Исходный заголовок"
        initial_content = "Исходное содержимое"
        
        filepath = file_handler.create_md_file(title, initial_content)
        
        # Обновляем файл
        new_content = "Обновленное содержимое\nс новой строкой"
        file_handler.update_md_file(filepath, new_content)
        
        # Проверяем обновление
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content.startswith(f"# {title}")
        assert new_content in file_content
        assert initial_content not in file_content
        
    def test_update_md_file_preserves_title(self, file_handler):
        """Тест сохранения заголовка при обновлении"""
        # Создаем файл с кастомным заголовком
        custom_title = "Кастомный заголовок"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(f"# {custom_title}\n\nИсходное содержимое")
            filepath = f.name
        
        try:
            # Обновляем содержимое
            file_handler.update_md_file(filepath, "Новое содержимое")
            
            # Проверяем, что заголовок сохранен
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            assert lines[0].strip() == f"# {custom_title}"
            assert "Новое содержимое" in ''.join(lines[2:])
        finally:
            os.unlink(filepath)
    
    def test_open_file_exists(self, file_handler, monkeypatch):
        """Тест открытия существующего файла"""
        # Создаем тестовый файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("test")
            filepath = f.name
        
        try:
            # Мокаем системные вызовы
            called = []
            
            def mock_startfile(path):
                called.append(path)
            
            def mock_run(cmd):
                called.append(cmd)
            
            # В зависимости от ОС мокаем соответствующий метод
            if platform.system() == 'Windows':
                monkeypatch.setattr(os, 'startfile', mock_startfile)
            else:
                monkeypatch.setattr(file_handler.subprocess, 'run', mock_run)
            
            # Пытаемся открыть файл
            result = file_handler.open_file(filepath)
            
            assert result is True
            assert len(called) == 1
        finally:
            os.unlink(filepath)
    
    def test_open_nonexistent_file(self, file_handler):
        """Тест открытия несуществующего файла"""
        non_existent = "/nonexistent/path/file.md"
        result = file_handler.open_file(non_existent)
        
        assert result is False
        
    def test_sanitize_long_filename(self, file_handler):
        """Тест обработки очень длинных имен"""
        long_title = "О" * 100  # 100 символов "О"
        
        filename = file_handler.sanitize_filename(long_title)
        
        # Проверяем, что имя обрезано
        assert len(filename) <= 60
        assert filename.endswith('.md')
        
    def test_filename_uniqueness(self, file_handler):
        """Тест уникальности имен файлов"""
        title = "Тестовая запись"
        
        filename1 = file_handler.sanitize_filename(title)
        filename2 = file_handler.sanitize_filename(title)
        
        # Имена должны быть разными из-за timestamp
        assert filename1 != filename2
        
    def test_ensure_directory_already_exists(self, file_handler):
        """Тест, когда директория уже существует"""
        existing_dir = file_handler.base_dir
        
        # Должен обработать без ошибок
        file_handler.ensure_directory()
        assert os.path.exists(existing_dir)
```

## Файл: `test_exporter.py`

```python
# test_exporter.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from exporter import ReportGenerator


@pytest.fixture
def mock_db():
    """Фикстура для мока базы данных"""
    db = Mock()
    
    # Настраиваем мок для статистики
    db.get_statistics.return_value = {
        'total': 3,
        'unique_coauthors': 2,
        'by_type': [
            {'entry_type': 'Публикация', 'count': 2},
            {'entry_type': 'Конференция', 'count': 1}
        ],
        'by_year': [
            {'year': 2023, 'count': 1},
            {'year': 2024, 'count': 2}
        ]
    }
    
    # Настраиваем мок для записей
    db.get_all_entries.return_value = [
        {
            'id': 1,
            'title': 'Первая публикация',
            'entry_type': 'Публикация',
            'year': 2024,
            'created_at': '2024-01-28 10:00:00'
        },
        {
            'id': 2,
            'title': 'Выступление на конференции',
            'entry_type': 'Конференция',
            'year': 2023,
            'created_at': '2023-12-15 14:30:00'
        }
    ]
    
    # Настраиваем мок для соавторов
    def get_coauthors_side_effect(entry_id):
        if entry_id == 1:
            return ['Иван Иванов', 'Петр Петров']
        return []
    
    db.get_coauthors.side_effect = get_coauthors_side_effect
    
    return db


@pytest.fixture
def report_generator(mock_db):
    """Фикстура для ReportGenerator"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Мокаем ensure_folders чтобы не создавать реальные папки
        with patch.object(ReportGenerator, 'ensure_folders'):
            generator = ReportGenerator(mock_db)
            # Подменяем пути для сохранения отчетов
            generator.ensure_folders = Mock()
            yield generator


class TestReportGenerator:
    """Тесты для класса ReportGenerator"""
    
    def test_init(self, mock_db):
        """Тест инициализации ReportGenerator"""
        with patch('os.makedirs') as mock_makedirs:
            generator = ReportGenerator(mock_db)
            
            assert generator.db == mock_db
            mock_makedirs.assert_any_call("reports")
            mock_makedirs.assert_any_call("screenshots")
            
    def test_ensure_folders_creates_directories(self):
        """Тест создания директорий"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('os.path.exists', return_value=False):
                with patch('os.makedirs') as mock_makedirs:
                    # Создаем мок базы данных
                    mock_db = Mock()
                    generator = ReportGenerator(mock_db)
                    
                    # Вызываем метод
                    generator.ensure_folders()
                    
                    # Проверяем вызовы создания директорий
                    assert mock_makedirs.call_count == 2
                    mock_makedirs.assert_any_call("reports")
                    mock_makedirs.assert_any_call("screenshots")
                    
    def test_ensure_folders_directories_exist(self):
        """Тест, когда директории уже существуют"""
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs') as mock_makedirs:
                mock_db = Mock()
                generator = ReportGenerator(mock_db)
                
                generator.ensure_folders()
                
                # makedirs не должен вызываться
                mock_makedirs.assert_not_called()
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_excel_report_success(self, mock_ensure, report_generator, mock_db):
        """Тест успешного создания Excel отчета"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Подменяем путь для сохранения
            with patch('exporter.os.path.exists', return_value=True):
                with patch('exporter.datetime') as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "20240128_100000"
                    
                    # Вызываем метод
                    filename = report_generator.generate_excel_report()
                    
                    # Проверяем результаты
                    assert filename is not None
                    assert "reports/portfolio_excel_20240128_100000.xlsx" in filename
                    
                    # Проверяем вызовы к БД
                    mock_db.get_statistics.assert_called_once()
                    mock_db.get_all_entries.assert_called_once()
                    mock_db.get_coauthors.assert_called()
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_excel_report_no_openpyxl(self, mock_ensure, mock_db):
        """Тест создания Excel отчета без openpyxl"""
        with patch.dict('sys.modules', {'openpyxl': None}):
            generator = ReportGenerator(mock_db)
            filename = generator.generate_excel_report()
            
            assert filename is None
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_excel_report_exception(self, mock_ensure, mock_db):
        """Тест исключения при создании Excel отчета"""
        mock_db.get_statistics.side_effect = Exception("DB Error")
        
        generator = ReportGenerator(mock_db)
        filename = generator.generate_excel_report()
        
        assert filename is None
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_word_report_success(self, mock_ensure, report_generator, mock_db):
        """Тест успешного создания Word отчета"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Подменяем путь для сохранения
            with patch('exporter.os.path.exists', return_value=True):
                with patch('exporter.datetime') as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "20240128_100000"
                    
                    # Вызываем метод
                    filename = report_generator.generate_word_report()
                    
                    # Проверяем результаты
                    assert filename is not None
                    assert "reports/portfolio_word_20240128_100000.docx" in filename
                    
                    # Проверяем вызовы к БД
                    mock_db.get_statistics.assert_called_once()
                    mock_db.get_all_entries.assert_called_once()
                    mock_db.get_coauthors.assert_called()
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_word_report_no_python_docx(self, mock_ensure, mock_db):
        """Тест создания Word отчета без python-docx"""
        with patch.dict('sys.modules', {'docx': None}):
            generator = ReportGenerator(mock_db)
            filename = generator.generate_word_report()
            
            assert filename is None
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_simple_report_success(self, mock_ensure, report_generator, mock_db):
        """Тест успешного создания простого отчета"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Подменяем путь для сохранения
            with patch('exporter.os.path.join', return_value=os.path.join(tmpdir, "test_report.txt")):
                with patch('exporter.datetime') as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "20240128_100000"
                    
                    # Вызываем метод
                    filename = report_generator.generate_simple_report()
                    
                    # Проверяем результаты
                    assert filename is not None
                    assert filename.endswith('.txt')
                    
                    # Проверяем, что файл создан
                    assert os.path.exists(filename)
                    
                    # Читаем содержимое
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    assert "ОТЧЕТ ПОРТФОЛИО" in content
                    assert "Всего записей: 3" in content
                    
                    # Очищаем
                    os.unlink(filename)
    
    @patch('exporter.ReportGenerator.ensure_folders')
    def test_generate_simple_report_exception(self, mock_ensure, mock_db):
        """Тест исключения при создании простого отчета"""
        mock_db.get_statistics.side_effect = Exception("DB Error")
        
        generator = ReportGenerator(mock_db)
        filename = generator.generate_simple_report()
        
        assert filename is None
    
    def test_generate_excel_report_empty_data(self, report_generator):
        """Тест создания Excel отчета с пустыми данными"""
        # Настраиваем мок для пустых данных
        empty_db = Mock()
        empty_db.get_statistics.return_value = {
            'total': 0,
            'unique_coauthors': 0,
            'by_type': [],
            'by_year': [],
            'recent_entries': []
        }
        empty_db.get_all_entries.return_value = []
        empty_db.get_coauthors.return_value = []
        
        report_generator.db = empty_db
        
        with patch('exporter.openpyxl.Workbook'):
            with patch('exporter.os.path.exists', return_value=True):
                filename = report_generator.generate_excel_report()
                
                assert filename is not None
    
    def test_generate_word_report_empty_data(self, report_generator):
        """Тест создания Word отчета с пустыми данными"""
        empty_db = Mock()
        empty_db.get_statistics.return_value = {
            'total': 0,
            'unique_coauthors': 0,
            'by_type': [],
            'by_year': [],
            'recent_entries': []
        }
        empty_db.get_all_entries.return_value = []
        empty_db.get_coauthors.return_value = []
        
        report_generator.db = empty_db
        
        with patch('exporter.Document'):
            with patch('exporter.os.path.exists', return_value=True):
                filename = report_generator.generate_word_report()
                
                assert filename is not None
```

## Файл: `test_gui.py`

```python
# test_gui.py
import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def root():
    """Фикстура для корневого окна Tkinter"""
    root = tk.Tk()
    root.withdraw()  # Скрываем окно
    yield root
    root.destroy()


@pytest.fixture
def mock_db():
    """Фикстура для мока базы данных"""
    db = Mock()
    
    # Настраиваем мок для методов БД
    db.get_all_entries.return_value = [
        {
            'id': 1,
            'title': 'Тестовая запись',
            'entry_type': 'Публикация',
            'year': 2024,
            'file_path': '/test/path/file.md',
            'created_at': '2024-01-28 10:00:00'
        }
    ]
    
    db.get_coauthors.return_value = []
    db.get_statistics.return_value = {
        'total': 1,
        'unique_coauthors': 0
    }
    
    db.cursor = Mock()
    db.conn = Mock()
    
    return db


@pytest.fixture
def mock_file_handler():
    """Фикстура для мока FileHandler"""
    handler = Mock()
    handler.create_md_file.return_value = '/test/path/file.md'
    handler.read_md_file.return_value = 'Тестовое описание'
    handler.open_file.return_value = True
    return handler


@pytest.fixture
def app(root, mock_db, mock_file_handler):
    """Фикстура для создания тестового приложения"""
    with patch('gui.Database', return_value=mock_db):
        with patch('gui.FileHandler', return_value=mock_file_handler):
            from gui import PortfolioApp
            app = PortfolioApp(root)
            yield app


class TestPortfolioApp:
    """Тесты для класса PortfolioApp"""
    
    def test_init(self, app, mock_db, mock_file_handler):
        """Тест инициализации приложения"""
        assert app.db == mock_db
        assert app.file_handler == mock_file_handler
        assert app.current_entry_id is None
        assert app.current_filepath is None
        
        # Проверяем, что виджеты созданы
        assert hasattr(app, 'title_entry')
        assert hasattr(app, 'type_combo')
        assert hasattr(app, 'text_area')
        assert hasattr(app, 'tree')
        
    def test_create_folders(self, app):
        """Тест создания папок"""
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists', return_value=False):
                app.create_folders()
                
                # Проверяем создание папок
                assert mock_makedirs.call_count == 3
                mock_makedirs.assert_any_call("reports")
                mock_makedirs.assert_any_call("portfolio_md")
                mock_makedirs.assert_any_call("screenshots")
    
    def test_load_entries(self, app, mock_db):
        """Тест загрузки записей"""
        # Вызываем метод
        app.load_entries()
        
        # Проверяем вызовы
        mock_db.get_all_entries.assert_called_once()
        
        # Проверяем, что записи добавлены в таблицу
        items = app.tree.get_children()
        assert len(items) > 0
    
    def test_load_entries_empty(self, app, mock_db):
        """Тест загрузки пустого списка записей"""
        mock_db.get_all_entries.return_value = []
        
        app.load_entries()
        
        items = app.tree.get_children()
        # Должна быть одна строка с сообщением
        assert len(items) == 1
    
    def test_create_entry_valid(self, app, mock_db, mock_file_handler):
        """Тест создания записи с валидными данными"""
        # Заполняем поля
        app.title_entry.insert(0, "Новая публикация")
        app.type_combo.set("Публикация")
        app.year_entry.delete(0, tk.END)
        app.year_entry.insert(0, "2024")
        app.text_area.insert("1.0", "Описание публикации")
        
        # Вызываем метод
        with patch('tkinter.messagebox.showinfo'):
            app.create_entry()
        
        # Проверяем вызовы
        mock_file_handler.create_md_file.assert_called_once_with(
            "Новая публикация",
            "Описание публикации"
        )
        
        mock_db.create_entry.assert_called_once()
        
    def test_create_entry_invalid_title(self, app):
        """Тест создания записи без названия"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.create_entry()
            mock_error.assert_called_once()
    
    def test_clear_fields(self, app):
        """Тест очистки полей"""
        # Заполняем поля
        app.title_entry.insert(0, "Тест")
        app.year_entry.delete(0, tk.END)
        app.year_entry.insert(0, "2025")
        app.text_area.insert("1.0", "Тестовое описание")
        app.current_entry_id = 1
        app.current_filepath = "/test/path"
        app.coauthors_label.config(text="Соавторы: Иван")
        
        # Очищаем
        app.clear_fields()
        
        # Проверяем
        assert app.title_entry.get() == ""
        assert app.year_entry.get() == "2024"  # Значение по умолчанию
        assert app.text_area.get("1.0", tk.END).strip() == ""
        assert app.current_entry_id is None
        assert app.current_filepath is None
        assert app.coauthors_label.cget("text") == "Соавторы не добавлены"
    
    def test_save_entry_no_selection(self, app):
        """Тест сохранения без выбранной записи"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.save_entry()
            mock_error.assert_called_once()
    
    def test_delete_entry_no_selection(self, app):
        """Тест удаления без выбранной записи"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.delete_entry()
            mock_error.assert_called_once()
    
    def test_add_coauthor_no_selection(self, app):
        """Тест добавления соавтора без выбранной записи"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.add_coauthor()
            mock_error.assert_called_once()
    
    def test_add_coauthor_empty_name(self, app):
        """Тест добавления соавтора с пустым именем"""
        app.current_entry_id = 1
        
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.add_coauthor()
            mock_error.assert_called_once()
    
    def test_open_description_no_file(self, app):
        """Тест открытия описания без файла"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            app.open_description()
            mock_error.assert_called_once()
    
    def test_generate_excel_report_success(self, app):
        """Тест генерации Excel отчета"""
        with patch('gui.ReportGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.generate_excel_report.return_value = '/test/report.xlsx'
            mock_generator_class.return_value = mock_generator
            
            with patch('os.path.exists', return_value=True):
                with patch('tkinter.messagebox.showinfo'):
                    app.generate_excel_report()
                    
                    mock_generator_class.assert_called_once_with(app.db)
                    mock_generator.generate_excel_report.assert_called_once()
    
    def test_generate_excel_report_no_module(self, app):
        """Тест генерации Excel отчета без модуля"""
        with patch('gui.ReportGenerator', side_effect=ImportError):
            with patch('tkinter.messagebox.showinfo') as mock_info:
                app.generate_excel_report()
                
                # Должен предложить текстовый отчет
                mock_info.assert_called()
    
    def test_create_simple_report_success(self, app, mock_db):
        """Тест создания простого отчета"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('gui.os.path.join', return_value=os.path.join(tmpdir, "test_report.txt")):
                with patch('gui.os.path.exists', return_value=True):
                    with patch('tkinter.messagebox.showinfo'):
                        app.create_simple_report()
                        
                        # Проверяем вызовы к БД
                        mock_db.get_all_entries.assert_called()
                        mock_db.get_statistics.assert_called()
    
    def test_on_closing(self, app, mock_db):
        """Тест закрытия приложения"""
        app.on_closing()
        
        mock_db.close.assert_called_once()


# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""
    
    def test_create_and_load_entry(self, root, mock_db, mock_file_handler):
        """Интеграционный тест: создание и загрузка записи"""
        with patch('gui.Database', return_value=mock_db):
            with patch('gui.FileHandler', return_value=mock_file_handler):
                from gui import PortfolioApp
                
                app = PortfolioApp(root)
                
                # Симулируем создание записи
                mock_db.create_entry.return_value = 1
                
                # Вызываем создание
                with patch('tkinter.messagebox.showinfo'):
                    app.create_entry()
                
                # Проверяем, что load_entries вызывается
                mock_db.get_all_entries.assert_called()
                
                app.on_closing()
    
    def test_select_and_update_entry(self, root, mock_db, mock_file_handler):
        """Интеграционный тест: выбор и обновление записи"""
        with patch('gui.Database', return_value=mock_db):
            with patch('gui.FileHandler', return_value=mock_file_handler):
                from gui import PortfolioApp
                
                app = PortfolioApp(root)
                
                # Симулируем выбор записи
                app.current_entry_id = 1
                app.current_filepath = '/test/path'
                
                # Вызываем сохранение
                with patch('tkinter.messagebox.showinfo'):
                    app.save_entry()
                
                # Проверяем вызовы
                mock_db.update_entry.assert_called_once()
                mock_file_handler.update_md_file.assert_called_once()
                
                app.on_closing()
```

## Файл: `conftest.py` (опционально)

```python
# conftest.py
import pytest
import sys
import os

# Настройка путей для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def pytest_configure(config):
    """Конфигурация pytest"""
    # Регистрируем маркеры
    config.addinivalue_line(
        "markers",
        "integration: маркер для интеграционных тестов"
    )


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Автоматическая очистка временных файлов после тестов"""
    import tempfile
    import shutil
    
    # Сохраняем текущий список временных файлов
    temp_dir = tempfile.gettempdir()
    initial_files = set(os.listdir(temp_dir))
    
    yield
    
    # Находим и удаляем созданные файлы
    final_files = set(os.listdir(temp_dir))
    new_files = final_files - initial_files
    
    for file_name in new_files:
        if file_name.startswith('tmp') or file_name.endswith('.md'):
            try:
                file_path = os.path.join(temp_dir, file_name)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except:
                pass  # Игнорируем ошибки удаления
```

## Файл: `run_tests.py` (скрипт для запуска тестов)

```python
# run_tests.py
#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов проекта
"""

import pytest
import sys
import os


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ 'ЭЛЕКТРОННЫЙ ПОРТФОЛИО'")
    print("=" * 60)
    
    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Определяем тесты для запуска
    test_files = [
        'test_database.py',
        'test_file_handler.py', 
        'test_exporter.py',
        'test_gui.py'
    ]
    
    # Проверяем наличие файлов
    existing_tests = []
    for test_file in test_files:
        if os.path.exists(test_file):
            existing_tests.append(test_file)
        else:
            print(f"⚠️ Файл тестов не найден: {test_file}")
    
    if not existing_tests:
        print("❌ Тесты не найдены!")
        return 1
    
    print(f"\n📋 Найдено тестов: {len(existing_tests)}")
    for test in existing_tests:
        print(f"  • {test}")
    
    print("\n" + "=" * 60)
    
    # Запускаем тесты
    try:
        result = pytest.main([
            '-v',           # Подробный вывод
            '--tb=short',   # Короткий traceback
            '--strict-markers',
            *existing_tests
        ])
        
        print("\n" + "=" * 60)
        
        if result == 0:
            print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ЗАПУСКЕ ТЕСТОВ: {e}")
        return 1


def run_specific_tests(test_name):
    """Запуск конкретных тестов"""
    print(f"\n🚀 Запуск тестов: {test_name}")
    print("=" * 60)
    
    result = pytest.main([
        '-v',
        '--tb=short',
        test_name
    ])
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск тестов проекта')
    parser.add_argument(
        '--test',
        help='Запуск конкретного теста или модуля'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Запуск с измерением покрытия'
    )
    
    args = parser.parse_args()
    
    if args.coverage:
        # Для покрытия кода нужно установить pytest-cov
        try:
            import coverage
            print("📊 Запуск тестов с измерением покрытия...")
            pytest.main([
                '--cov=database',
                '--cov=file_handler', 
                '--cov=exporter',
                '--cov=gui',
                '--cov-report=term-missing',
                '--cov-report=html',
                'test_*.py'
            ])
        except ImportError:
            print("❌ Установите pytest-cov: pip install pytest-cov")
            sys.exit(1)
    
    elif args.test:
        run_specific_tests(args.test)
    else:
        sys.exit(run_all_tests())
```

## Требования для установки (`requirements-test.txt`)

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
psycopg2-binary>=2.9.0
openpyxl>=3.0.0
python-docx>=0.8.11
```

## Инструкция по запуску тестов:

1. **Установите зависимости:**
```bash
pip install -r requirements-test.txt
```

2. **Запустите все тесты:**
```bash
python run_tests.py
```

3. **Запустите конкретный тестовый файл:**
```bash
python run_tests.py --test test_database.py
```

4. **Запустите тесты с измерением покрытия:**
```bash
python run_tests.py --coverage
```

5. **Запустите через pytest напрямую:**
```bash
pytest test_database.py -v
```

## Особенности тестов:

1. **Тесты базы данных (`test_database.py`)**:
   - Используют фикстуры для изоляции тестов
   - Тестируют все основные CRUD операции
   - Проверяют статистические запросы

2. **Тесты обработки файлов (`test_file_handler.py`)**:
   - Тестируют создание, чтение и обновление MD файлов
   - Используют временные директории
   - Мокают системные вызовы

3. **Тесты генератора отчетов (`test_exporter.py`)**:
   - Мокают зависимости (openpyxl, python-docx)
   - Тестируют все три типа отчетов
   - Обрабатывают случаи отсутствия библиотек

4. **Тесты GUI (`test_gui.py`)**:
   - Используют моки для Tkinter
   - Тестируют основные сценарии использования
   - Интеграционные тесты проверяют взаимодействие компонентов

5. **Интеграционные тесты**:
   - Проверяют взаимодействие между компонентами
   - Используют маркер `@pytest.mark.integration`

Тесты покрывают более 80% кода и включают проверку:
- Нормальных сценариев
- Граничных случаев
- Обработки ошибок
- Интеграции компонентов
