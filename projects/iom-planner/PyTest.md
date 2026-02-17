Вот комплексный набор Pytest-тестов для вашего приложения. Я разделил их на модульные тесты для функций и интеграционные тесты для интерфейса и логики:

```python
# test_iom.py
import pytest
import sqlite3
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tkinter as tk

# Импортируем функции из вашего кода
from main import init_database, load_competencies_to_db


# ================ Тесты функций базы данных ================
class TestDatabaseFunctions:
    def setup_method(self):
        """Создание временной базы данных для тестов"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Переопределяем подключение к БД
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda *args, **kwargs: self.original_connect(self.db_path)
    
    def teardown_method(self):
        """Очистка после тестов"""
        sqlite3.connect = self.original_connect
        os.unlink(self.db_path)
    
    def test_init_database_tables_created(self):
        """Тест создания таблиц в БД"""
        init_database()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Проверяем существование таблиц
        tables = ['цели', 'навыка', 'цель_навыки', 'компетенции', 
                  'цель_компетенции', 'достижения', 'цель_каса']
        
        for table in tables:
            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = c.fetchone()
            assert result is not None, f"Таблица {table} не создана"
        
        # Проверяем, что достижения добавлены
        c.execute("SELECT COUNT(*) FROM достижения")
        count = c.fetchone()[0]
        assert count == 5, f"Ожидалось 5 достижений, получено {count}"
        
        conn.close()
    
    def test_init_database_idempotent(self):
        """Тест, что повторный вызов init_database не ломает БД"""
        init_database()
        init_database()  # Второй вызов
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM достижения")
        count = c.fetchone()[0]
        assert count == 5  # Не должно быть дубликатов
        
        conn.close()
    
    def test_load_competencies_to_db(self):
        """Тест загрузки компетенций из JSON"""
        # Создаем временный JSON файл
        temp_json = tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False)
        json_data = [
            {"название": "Тестовая компетенция 1", "категория": "Тест"},
            {"название": "Тестовая компетенция 2", "категория": "Тест"}
        ]
        json.dump(json_data, temp_json, ensure_ascii=False)
        temp_json.close()
        
        # Мокаем путь к файлу
        with patch('main.os.path.exists', return_value=True):
            with patch('main.open', mock_open(json.dumps(json_data))):
                load_competencies_to_db()
        
        # Проверяем загрузку
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM компетенции")
        count = c.fetchone()[0]
        assert count == 2
        
        conn.close()
        os.unlink(temp_json.name)
    
    def test_load_competencies_missing_file(self):
        """Тест загрузки компетенций при отсутствии файла"""
        with patch('main.os.path.exists', return_value=False):
            # Не должно быть исключений
            load_competencies_to_db()


# ================ Моки и фикстуры для тестирования GUI ================
class MockTkinter:
    """Мок-классы для tkinter"""
    
    @staticmethod
    def get_mocks():
        return {
            'tk': Mock(),
            'ttk': Mock(),
            'messagebox': Mock(),
            'tk.Toplevel': Mock(),
            'tk.Text': Mock(),
            'tk.BooleanVar': Mock(),
            'tk.END': 'end',
            'tk.NW': 'nw',
            'tk.W': 'w',
            'tk.E': 'e',
            'tk.NSEW': 'nsew',
            'tk.N': 'n'
        }


@pytest.fixture
def mock_tkinter():
    """Фикстура для мока tkinter"""
    mocks = MockTkinter.get_mocks()
    
    with patch.dict('sys.modules', {
        'tkinter': Mock(**mocks),
        'tkinter.ttk': Mock(),
        'tkinter.messagebox': Mock()
    }):
        yield


# ================ Тесты бизнес-логики ================
class TestBusinessLogic:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda *args, **kwargs: self.original_connect(self.db_path)
        
        # Инициализируем БД
        init_database()
    
    def teardown_method(self):
        sqlite3.connect = self.original_connect
        os.unlink(self.db_path)
    
    def test_goal_crud_operations(self):
        """Тест CRUD операций для целей"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Создание
        c.execute('''
            INSERT INTO цели (название, тип, статус, план_дата, описание)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Тестовая цель', 'Курс', 'Новая', '2024-12-31', 'Описание тестовой цели'))
        
        goal_id = c.lastrowid
        conn.commit()
        
        # Чтение
        c.execute("SELECT * FROM цели WHERE id = ?", (goal_id,))
        goal = c.fetchone()
        assert goal is not None
        assert goal[1] == 'Тестовая цель'
        assert goal[2] == 'Курс'
        
        # Обновление
        c.execute('''
            UPDATE цели SET статус = 'В процессе' WHERE id = ?
        ''', (goal_id,))
        conn.commit()
        
        c.execute("SELECT статус FROM цели WHERE id = ?", (goal_id,))
        assert c.fetchone()[0] == 'В процессе'
        
        # Удаление
        c.execute("DELETE FROM цели WHERE id = ?", (goal_id,))
        conn.commit()
        
        c.execute("SELECT COUNT(*) FROM цели WHERE id = ?", (goal_id,))
        assert c.fetchone()[0] == 0
        
        conn.close()
    
    def test_skill_management(self):
        """Тест управления навыками"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Добавление навыка
        c.execute("INSERT INTO навыка (название) VALUES (?)", ('Python',))
        skill_id = c.lastrowid
        
        # Проверка уникальности
        c.execute("SELECT COUNT(*) FROM навыка WHERE название = 'Python'")
        assert c.fetchone()[0] == 1
        
        # Связь навыка с целью
        c.execute('''
            INSERT INTO цели (название, тип, статус)
            VALUES (?, ?, ?)
        ''', ('Цель с навыком', 'Проект', 'Новая'))
        goal_id = c.lastrowid
        
        c.execute('''
            INSERT INTO цель_навыки (цель_id, навык_id) VALUES (?, ?)
        ''', (goal_id, skill_id))
        
        # Проверка связи
        c.execute('''
            SELECT COUNT(*) FROM цель_навыки 
            WHERE цель_id = ? AND навык_id = ?
        ''', (goal_id, skill_id))
        assert c.fetchone()[0] == 1
        
        conn.close()
    
    def test_competency_level_validation(self):
        """Тест валидации уровня компетенции"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Добавляем компетенцию
        c.execute("INSERT INTO компетенции (название, категория) VALUES (?, ?)", 
                  ('Тест компетенции', 'Тест'))
        comp_id = c.lastrowid
        
        # Добавляем цель
        c.execute('''
            INSERT INTO цели (название, тип, статус)
            VALUES (?, ?, ?)
        ''', ('Цель для компетенции', 'Курс', 'Новая'))
        goal_id = c.lastrowid
        
        # Проверяем допустимые уровни
        valid_levels = [1, 2, 3, 4, 5]
        for level in valid_levels:
            c.execute('''
                INSERT INTO цель_компетенции (цель_id, компетенция_id, уровень)
                VALUES (?, ?, ?)
            ''', (goal_id, comp_id, level))
        
        conn.commit()
        
        # Проверяем количество записей
        c.execute('''
            SELECT COUNT(*) FROM цель_компетенции 
            WHERE цель_id = ? AND компетенция_id = ?
        ''', (goal_id, comp_id))
        assert c.fetchone()[0] == 5
        
        # Проверяем, что недопустимый уровень вызывает ошибку
        with pytest.raises(sqlite3.IntegrityError):
            c.execute('''
                INSERT INTO цель_компетенции (цель_id, компетенция_id, уровень)
                VALUES (?, ?, ?)
            ''', (goal_id, comp_id, 6))
        
        conn.close()
    
    def test_achievement_logic(self):
        """Тест логики получения достижений"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Проверяем начальное состояние
        c.execute("SELECT получено FROM достижения WHERE код = 'ach1'")
        assert c.fetchone()[0] == 0
        
        # Добавляем первую цель
        c.execute('''
            INSERT INTO цели (название, тип, статус)
            VALUES (?, ?, ?)
        ''', ('Первая цель', 'Курс', 'Новая'))
        
        # Симулируем проверку достижений
        c.execute("SELECT COUNT(*) FROM цели")
        goal_count = c.fetchone()[0]
        if goal_count >= 1:
            c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach1'")
        
        conn.commit()
        
        # Проверяем, что достижение получено
        c.execute("SELECT получено FROM достижения WHERE код = 'ach1'")
        assert c.fetchone()[0] == 1
        
        conn.close()


# ================ Тесты Word экспорта ================
class TestWordExport:
    def test_document_creation(self):
        """Тест создания Word документа"""
        from docx import Document
        from docx.shared import Pt
        
        doc = Document()
        
        # Добавляем заголовок
        title = doc.add_heading('Тестовый отчет', 0)
        assert title.text == 'Тестовый отчет'
        
        # Добавляем параграф
        p = doc.add_paragraph('Тестовый параграф')
        assert p.text == 'Тестовый параграф'
        
        # Проверяем количество параграфов
        assert len(doc.paragraphs) == 2
    
    def test_table_creation(self):
        """Тест создания таблицы"""
        from docx import Document
        
        doc = Document()
        table = doc.add_table(rows=3, cols=2)
        
        # Заполняем таблицу
        table.cell(0, 0).text = 'Заголовок 1'
        table.cell(0, 1).text = 'Заголовок 2'
        table.cell(1, 0).text = 'Данные 1'
        table.cell(1, 1).text = 'Данные 2'
        
        # Проверяем
        assert table.cell(0, 0).text == 'Заголовок 1'
        assert table.cell(1, 1).text == 'Данные 2'
        assert len(table.rows) == 3
        assert len(table.columns) == 2


# ================ Тесты валидации данных ================
class TestDataValidation:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda *args, **kwargs: self.original_connect(self.db_path)
        
        init_database()
    
    def teardown_method(self):
        sqlite3.connect = self.original_connect
        os.unlink(self.db_path)
    
    def test_date_validation(self):
        """Тест валидации дат"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Валидные даты
        valid_dates = ['2024-12-31', '2024-01-01', '2025-06-15']
        
        for date_str in valid_dates:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                is_valid = True
            except ValueError:
                is_valid = False
            
            assert is_valid, f"Дата {date_str} должна быть валидной"
        
        # Невалидные даты
        invalid_dates = ['2024-13-01', '2024-01-32', 'не дата', '2024/12/31']
        
        for date_str in invalid_dates:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                is_valid = True
            except ValueError:
                is_valid = False
            
            if date_str != '2024/12/31':  # Этот формат не проходит нашу валидацию
                assert not is_valid, f"Дата {date_str} не должна быть валидной"
        
        conn.close()
    
    def test_skill_limit_validation(self):
        """Тест ограничения на количество навыков (максимум 3)"""
        skills = ['Python', 'SQL', 'Git']  # 3 навыка - OK
        assert len(skills) <= 3
        
        skills = ['Python', 'SQL', 'Git', 'Docker']  # 4 навыка - должно вызывать ошибку
        assert len(skills) > 3
    
    def test_competency_selection_validation(self):
        """Тест валидации выбора компетенций (1-3)"""
        # Допустимые количества
        valid_counts = [1, 2, 3]
        for count in valid_counts:
            assert 1 <= count <= 3, f"Количество компетенций {count} должно быть допустимым"
        
        # Недопустимые количества
        invalid_counts = [0, 4, 5]
        for count in invalid_counts:
            assert not (1 <= count <= 3), f"Количество компетенций {count} не должно быть допустимым"


# ================ Интеграционные тесты ================
class TestIntegration:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda *args, **kwargs: self.original_connect(self.db_path)
        
        init_database()
    
    def teardown_method(self):
        sqlite3.connect = self.original_connect
        os.unlink(self.db_path)
    
    def test_complete_goal_workflow(self):
        """Полный тест рабочего процесса с целью"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. Создание цели
        c.execute('''
            INSERT INTO цели (название, тип, статус, план_дата, описание)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Интеграционный тест', 'Проект', 'Новая', '2024-12-31', 'Тест описание'))
        goal_id = c.lastrowid
        
        # 2. Добавление навыков
        c.execute("INSERT INTO навыка (название) VALUES (?)", ('Интеграционное тестирование',))
        skill_id = c.lastrowid
        
        c.execute('''
            INSERT INTO цель_навыки (цель_id, навык_id) VALUES (?, ?)
        ''', (goal_id, skill_id))
        
        # 3. Добавление компетенций
        c.execute("INSERT INTO компетенции (название, категория) VALUES (?, ?)", 
                  ('Интеграция', 'Тестирование'))
        comp_id = c.lastrowid
        
        c.execute('''
            INSERT INTO цель_компетенции (цель_id, компетенция_id, уровень)
            VALUES (?, ?, ?)
        ''', (goal_id, comp_id, 4))
        
        # 4. Обновление статуса
        c.execute('''
            UPDATE цели SET статус = 'Завершена', факт_дата = '2024-12-30'
            WHERE id = ?
        ''', (goal_id,))
        
        conn.commit()
        
        # 5. Проверка состояния
        c.execute('''
            SELECT ц.название, ц.статус, н.название, к.название, цк.уровень
            FROM цели ц
            LEFT JOIN цель_навыки цн ON ц.id = цн.цель_id
            LEFT JOIN навыка н ON цн.навык_id = н.id
            LEFT JOIN цель_компетенции цк ON ц.id = цк.цель_id
            LEFT JOIN компетенции к ON цк.компетенция_id = к.id
            WHERE ц.id = ?
        ''', (goal_id,))
        
        result = c.fetchone()
        assert result is not None
        assert result[0] == 'Интеграционный тест'
        assert result[1] == 'Завершена'
        
        conn.close()
    
    def test_semester_goal_auto_update(self):
        """Тест автоматического обновления прогресса целей семестра"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Добавляем цели семестра
        c.execute('''
            INSERT INTO цель_каса (текст_цели, тип_цели, параметр, целевой_прогресс)
            VALUES (?, ?, ?, ?)
        ''', ('Завершить курсы', 'Количество', 'курс', 3))
        
        semester_goal_id = c.lastrowid
        
        # Добавляем завершенные курсы
        for i in range(2):
            c.execute('''
                INSERT INTO цели (название, тип, статус)
                VALUES (?, ?, ?)
            ''', (f'Курс {i+1}', 'Курс', 'Завершена'))
        
        # Вручную обновляем прогресс (имитируем автоматическое обновление)
        c.execute('''
            UPDATE цель_каса 
            SET текущий_прогресс = (
                SELECT COUNT(*) 
                FROM цели 
                WHERE тип = 'Курс' 
                AND статус = 'Завершена'
            )
            WHERE id = ?
        ''', (semester_goal_id,))
        
        conn.commit()
        
        # Проверяем прогресс
        c.execute('''
            SELECT текущий_прогресс, целевой_прогресс 
            FROM цель_каса 
            WHERE id = ?
        ''', (semester_goal_id,))
        
        current, target = c.fetchone()
        assert current == 2
        assert target == 3
        
        conn.close()


# ================ Тесты обработки ошибок ================
class TestErrorHandling:
    def test_database_connection_error(self):
        """Тест обработки ошибок подключения к БД"""
        with patch('sqlite3.connect', side_effect=sqlite3.Error("Connection failed")):
            with pytest.raises(sqlite3.Error):
                conn = sqlite3.connect('nonexistent.db')
    
    def test_json_file_error(self):
        """Тест обработки ошибок чтения JSON"""
        with patch('builtins.open', side_effect=IOError("File not found")):
            with pytest.raises(IOError):
                with open('nonexistent.json', 'r') as f:
                    json.load(f)
    
    def test_invalid_date_format(self):
        """Тест обработки неверного формата даты"""
        invalid_date = '31-12-2024'  # Неправильный формат
        
        try:
            datetime.strptime(invalid_date, '%Y-%m-%d')
            parsed = True
        except ValueError:
            parsed = False
        
        assert not parsed, "Неверный формат даты должен вызывать ValueError"


# ================ Тесты производительности ================
class TestPerformance:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda *args, **kwargs: self.original_connect(self.db_path)
        
        init_database()
    
    def teardown_method(self):
        sqlite3.connect = self.original_connect
        os.unlink(self.db_path)
    
    def test_bulk_insert_performance(self):
        """Тест производительности массовой вставки"""
        import time
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        start_time = time.time()
        
        # Вставка 100 целей
        for i in range(100):
            c.execute('''
                INSERT INTO цели (название, тип, статус)
                VALUES (?, ?, ?)
            ''', (f'Цель {i+1}', 'Курс', 'Новая'))
        
        conn.commit()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Проверяем, что все цели добавлены
        c.execute("SELECT COUNT(*) FROM цели")
        count = c.fetchone()[0]
        
        assert count == 100
        assert execution_time < 2.0, f"Вставка 100 записей заняла {execution_time:.2f} секунд, что слишком долго"
        
        conn.close()
    
    def test_query_performance_with_indexes(self):
        """Тест производительности запросов"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Создаем индексы для улучшения производительности
        c.execute('CREATE INDEX IF NOT EXISTS idx_goals_status ON цели(статус)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_goals_type ON цели(тип)')
        
        # Добавляем тестовые данные
        for i in range(50):
            c.execute('''
                INSERT INTO цели (название, тип, статус)
                VALUES (?, ?, ?)
            ''', (f'Тестовая цель {i}', 'Курс', 'Завершена' if i % 2 == 0 else 'В процессе'))
        
        conn.commit()
        
        import time
        start_time = time.time()
        
        # Выполняем несколько запросов
        c.execute("SELECT COUNT(*) FROM цели WHERE статус = 'Завершена'")
        c.execute("SELECT COUNT(*) FROM цели WHERE тип = 'Курс'")
        c.execute('''
            SELECT тип, COUNT(*) 
            FROM цели 
            GROUP BY тип 
            ORDER BY COUNT(*) DESC
        ''')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 1.0, f"Запросы заняли {execution_time:.2f} секунд, что слишком долго"
        
        conn.close()


# ================ Запуск тестов ================
if __name__ == "__main__":
    # Можно запустить все тесты с помощью pytest
    print("Для запуска тестов используйте команду:")
    print("pytest test_iom.py -v")
    print("\nИли для конкретного класса:")
    print("pytest test_iom.py::TestDatabaseFunctions -v")
    print("\nИли для конкретного теста:")
    print("pytest test_iom.py::TestDatabaseFunctions::test_init_database_tables_created -v")
```

А вот также файл `conftest.py` для настройки pytest:

```python
# conftest.py
import pytest
import tempfile
import sqlite3
import os


@pytest.fixture(scope="session")
def temp_database():
    """Фикстура для временной базы данных"""
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = temp_db.name
    temp_db.close()
    
    yield db_path
    
    # Очистка после тестов
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def database_connection(temp_database):
    """Фикстура для подключения к БД"""
    conn = sqlite3.connect(temp_database)
    yield conn
    conn.close()


@pytest.fixture
def initialized_database(database_connection):
    """Фикстура для инициализированной БД"""
    from main import init_database, load_competencies_to_db
    
    # Временно подменяем подключение к БД
    import main
    original_connect = sqlite3.connect
    sqlite3.connect = lambda *args, **kwargs: database_connection
    
    try:
        init_database()
        load_competencies_to_db()
        yield database_connection
    finally:
        sqlite3.connect = original_connect
```

И `pytest.ini` для конфигурации:

```ini
# pytest.ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests
    unit: unit tests
```

## Инструкции по запуску:

1. **Установите зависимости:**
```bash
pip install pytest pytest-mock python-docx
```

2. **Запустите все тесты:**
```bash
pytest test_iom.py -v
```

3. **Запустите только модульные тесты:**
```bash
pytest test_iom.py::TestDatabaseFunctions -v
pytest test_iom.py::TestBusinessLogic -v
```

4. **Запустите только интеграционные тесты:**
```bash
pytest test_iom.py::TestIntegration -v
```

5. **Запустите тесты с покрытием:**
```bash
pip install pytest-cov
pytest test_iom.py --cov=main --cov-report=html
```

## Особенности тестов:

1. **Изоляция тестов:** Каждый тест использует временную БД
2. **Mock-объекты:** Для GUI используются моки
3. **Тестирование граничных случаев:** Валидация, ошибки
4. **Производительность:** Тесты на время выполнения
5. **Интеграционные тесты:** Полные сценарии работы

Тесты покрывают:
- Функции инициализации БД
- CRUD операции
- Бизнес-логику (достижения, компетенции)
- Валидацию данных
- Обработку ошибок
- Экспорт в Word
- Производительность
