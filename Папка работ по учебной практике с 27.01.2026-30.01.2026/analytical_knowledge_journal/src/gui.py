# src/gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import logging
from datetime import datetime
from typing import Optional, List
import webbrowser
import tempfile
import os

logger = logging.getLogger(__name__)


class KnowledgeJournalGUI:
    """Основной класс графического интерфейса"""

    def __init__(self, db_manager, file_manager):
        """
        Инициализация GUI

        Args:
            db_manager: Объект для работы с БД
            file_manager: Объект для работы с файлами
        """
        self.db = db_manager
        self.fm = file_manager

        # Текущий выбранный конспект
        self.current_note = None
        self.status_bar = None  # Инициализация status_bar

        # Создание главного окна
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()

        # Загрузка конспектов
        self.load_notes()

    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("Аналитический журнал знаний")
        self.root.geometry("1200x700")

        # Центрирование окна
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Иконка (опционально)
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Создание Notebook (вкладок)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка 1: Конспекты
        self.notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.notes_tab, text="📝 Конспекты")
        self.create_notes_tab()

        # Вкладка 2: Аналитика
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="📊 Аналитика")
        self.create_analytics_tab()

        # Вкладка 3: Теги
        self.tags_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tags_tab, text="🏷️ Теги")
        self.create_tags_tab()

        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_notes_tab(self):
        """Создание вкладки конспектов"""
        # Разделение на две части
        paned = ttk.PanedWindow(self.notes_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Левая панель - список конспектов
        left_frame = ttk.Frame(paned)

        # Панель управления
        control_frame = ttk.LabelFrame(left_frame, text="Управление конспектами")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Поля ввода
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.category_entry = ttk.Entry(input_frame, width=30)
        self.category_entry.grid(row=1, column=1, padx=2, pady=2)

        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Создать", command=self.create_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Сохранить", command=self.save_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Удалить", command=self.delete_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Просмотреть", command=self.view_note).pack(side=tk.LEFT, padx=2)

        # Список конспектов
        list_frame = ttk.LabelFrame(left_frame, text="Список конспектов")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview для отображения конспектов
        columns = ("ID", "Название", "Категория", "Обновлён")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)

        # Настройка колонок
        self.tree.heading("ID", text="ID", anchor=tk.W)
        self.tree.heading("Название", text="Название", anchor=tk.W)
        self.tree.heading("Категория", text="Категория", anchor=tk.W)
        self.tree.heading("Обновлён", text="Обновлён", anchor=tk.W)

        self.tree.column("ID", width=50, minwidth=50)
        self.tree.column("Название", width=200, minwidth=200)
        self.tree.column("Категория", width=150, minwidth=150)
        self.tree.column("Обновлён", width=120, minwidth=120)

        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка события выбора
        self.tree.bind('<<TreeviewSelect>>', self.on_note_select)

        # Правая панель - редактор и теги
        right_frame = ttk.Frame(paned)

        # Редактор Markdown
        editor_frame = ttk.LabelFrame(right_frame, text="Редактор Markdown")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Подсказки по синтаксису
        syntax_frame = ttk.Frame(editor_frame)
        syntax_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(syntax_frame,
                  text="Подсказки: **жирный** *курсив* `код` # Заголовок",
                  font=('Arial', 9)).pack(side=tk.LEFT)

        # Текстовый редактор
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            undo=True
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель теги
        tags_frame = ttk.LabelFrame(right_frame, text="Теги конспекта")
        tags_frame.pack(fill=tk.X, padx=5, pady=5)

        # Управление тегами
        tag_control_frame = ttk.Frame(tags_frame)
        tag_control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(tag_control_frame, text="Новый тег:").pack(side=tk.LEFT, padx=2)
        self.tag_entry = ttk.Entry(tag_control_frame, width=20)
        self.tag_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(tag_control_frame, text="Добавить", command=self.add_tag).pack(side=tk.LEFT, padx=2)
        ttk.Button(tag_control_frame, text="Удалить", command=self.remove_tag).pack(side=tk.LEFT, padx=2)

        # Отображение тегов
        self.tags_display = tk.Text(
            tags_frame,
            height=3,
            wrap=tk.WORD,
            font=('Arial', 10),
            state='disabled'
        )
        self.tags_display.pack(fill=tk.X, padx=5, pady=5)

        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=2)

    def create_analytics_tab(self):
        """Создание вкладки аналитики"""
        # Основной фрейм
        main_frame = ttk.Frame(self.analytics_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="📊 Аналитика активности",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)

        # Кнопки экспорта
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            export_frame,
            text="📈 Сформировать Excel отчёт",
            command=self.generate_excel_report,
            width=25
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="📄 Сформировать PDF отчёт",
            command=self.generate_pdf_report,
            width=25
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="🔄 Обновить статистику",
            command=self.load_analytics,
            width=25
        ).pack(side=tk.LEFT, padx=5)

        # Область для отображения статистики
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Текстовая область для статистики
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Загрузка начальной статистики
        self.load_analytics()

    def create_tags_tab(self):
        """Создание вкладки тегов"""
        main_frame = ttk.Frame(self.tags_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        ttk.Label(
            main_frame,
            text="🏷️ Управление тегами",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)

        # Статистика тегов
        self.tags_stats_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=15
        )
        self.tags_stats_text.pack(fill=tk.BOTH, expand=True, pady=10)

        # Кнопка обновления
        ttk.Button(
            main_frame,
            text="🔄 Обновить статистику тегов",
            command=self.load_tags_stats
        ).pack(pady=5)

        # Загрузка статистики тегов
        self.load_tags_stats()

    def load_notes(self):
        """Загрузка списка конспектов из БД"""
        try:
            # Очистка текущего списка
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получение конспектов из БД
            notes = self.db.get_all_notes()

            # Добавление в Treeview
            for note in notes:
                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        note['id'],
                        note['title'],
                        note['category'],
                        note['updated']
                    )
                )

            self.update_status(f"Загружено конспектов: {len(notes)}")

        except Exception as e:
            self.show_error(f"Ошибка загрузки конспектов: {e}")

    def on_note_select(self, event):
        """Обработка выбора конспекта"""
        try:
            # Получение выбранного элемента
            selection = self.tree.selection()
            if not selection:
                return

            # Получение ID конспекта
            item = self.tree.item(selection[0])
            note_id = item['values'][0]

            # Загрузка конспекта
            self.current_note = self.db.get_note(note_id)
            if not self.current_note:
                return

            # Загрузка содержимого файла
            content = self.fm.read_md_file(self.current_note['file_path'])

            # Обновление редактора
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content)

            # Обновление полей ввода
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.current_note['title'])

            self.category_entry.delete(0, tk.END)
            if self.current_note['category']:
                self.category_entry.insert(0, self.current_note['category'])

            # Загрузка тегов
            self.load_note_tags()

            # Логирование просмотра
            self.db.log_view(note_id)

            self.update_status(f"Выбран конспект: {self.current_note['title']}")

        except Exception as e:
            self.show_error(f"Ошибка загрузки конспекта: {e}")

    def load_note_tags(self):
        """Загрузка тегов выбранного конспекта"""
        try:
            if not self.current_note:
                return

            # Получение тегов из БД
            tags = self.db.get_note_tags(self.current_note['id'])

            # Обновление отображения
            self.tags_display.config(state='normal')
            self.tags_display.delete(1.0, tk.END)

            if tags:
                tags_text = ", ".join(tags)
                self.tags_display.insert(1.0, tags_text)
            else:
                self.tags_display.insert(1.0, "Нет тегов")

            self.tags_display.config(state='disabled')

        except Exception as e:
            self.show_error(f"Ошибка загрузки тегов: {e}")

    def create_note(self):
        """Создание нового конспекта"""
        try:
            # Получение данных из полей
            title = self.title_entry.get().strip()
            category = self.category_entry.get().strip()

            # Валидация
            if not title:
                self.show_error("Введите название конспекта")
                return

            if not category:
                category = "Без категории"

            # Создание файла
            filepath = self.fm.create_md_file(title)

            # Создание записи в БД
            note_id = self.db.create_note(title, category, filepath)

            # Обновление интерфейса
            self.load_notes()

            # Очистка полей
            self.title_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.text_editor.delete(1.0, tk.END)
            self.tags_display.config(state='normal')
            self.tags_display.delete(1.0, tk.END)
            self.tags_display.config(state='disabled')

            self.update_status(f"Конспект создан: {title}")
            messagebox.showinfo("Успех", f"Конспект '{title}' успешно создан!")

        except Exception as e:
            self.show_error(f"Ошибка создания конспекта: {e}")

    def save_note(self):
        """Сохранение изменений конспекта"""
        try:
            if not self.current_note:
                self.show_error("Выберите конспект для сохранения")
                return

            # Получение данных
            title = self.title_entry.get().strip()
            category = self.category_entry.get().strip()
            content = self.text_editor.get(1.0, tk.END).strip()

            if not title:
                self.show_error("Введите название конспекта")
                return

            if not category:
                category = "Без категории"

            # Обновление файла
            self.fm.write_md_file(self.current_note['file_path'], content)

            # Обновление записи в БД
            self.db.update_note(self.current_note['id'], title, category)

            # Обновление списка
            self.load_notes()

            self.update_status(f"Конспект сохранён: {title}")
            messagebox.showinfo("Успех", "Изменения сохранены!")

        except Exception as e:
            self.show_error(f"Ошибка сохранения: {e}")

    def delete_note(self):
        """Удаление конспекта"""
        try:
            if not self.current_note:
                self.show_error("Выберите конспект для удаления")
                return

            # Подтверждение
            confirm = messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите удалить конспект '{self.current_note['title']}'?\n"
                "Это действие нельзя отменить."
            )

            if not confirm:
                return

            # Удаление файла
            self.fm.delete_md_file(self.current_note['file_path'])

            # Удаление из БД (каскадное удаление через CASCADE)
            self.db.delete_note(self.current_note['id'])

            # Сброс текущего конспекта
            self.current_note = None

            # Очистка полей
            self.title_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.text_editor.delete(1.0, tk.END)
            self.tags_display.config(state='normal')
            self.tags_display.delete(1.0, tk.END)
            self.tags_display.config(state='disabled')

            # Обновление списка
            self.load_notes()

            self.update_status("Конспект удалён")

        except Exception as e:
            self.show_error(f"Ошибка удаления: {e}")

    def view_note(self):
        """Просмотр конспекта во внешнем редакторе"""
        try:
            if not self.current_note:
                self.show_error("Выберите конспект для просмотра")
                return

            # Открытие файла
            self.fm.open_in_external_editor(self.current_note['file_path'])

            self.update_status(f"Открыт конспект: {self.current_note['title']}")

        except Exception as e:
            self.show_error(f"Ошибка открытия файла: {e}")

    def add_tag(self):
        """Добавление тега к конспекту"""
        try:
            if not self.current_note:
                self.show_error("Выберите конспект")
                return

            tag = self.tag_entry.get().strip()
            if not tag:
                self.show_error("Введите название тега")
                return

            # Добавление тега
            self.db.add_tag(self.current_note['id'], tag)

            # Обновление отображения
            self.load_note_tags()

            # Очистка поля ввода
            self.tag_entry.delete(0, tk.END)

            self.update_status(f"Добавлен тег: {tag}")

        except Exception as e:
            self.show_error(f"Ошибка добавления тега: {e}")

    def remove_tag(self):
        """Удаление тега из конспекта"""
        try:
            if not self.current_note:
                self.show_error("Выберите конспект")
                return

            tag = self.tag_entry.get().strip()
            if not tag:
                self.show_error("Введите название тега для удаления")
                return

            # Удаление тега
            self.db.remove_tag(self.current_note['id'], tag)

            # Обновление отображения
            self.load_note_tags()

            # Очистка поля ввода
            self.tag_entry.delete(0, tk.END)

            self.update_status(f"Удалён тег: {tag}")

        except Exception as e:
            self.show_error(f"Ошибка удаления тега: {e}")

    def load_analytics(self):
        """Загрузка аналитики"""
        try:
            # Получение статистики
            stats = self.db.get_total_stats()

            # Формирование текста
            text = "📊 ОБЩАЯ СТАТИСТИКА\n"
            text += "=" * 40 + "\n\n"

            text += f"📚 Всего конспектов: {stats['total_notes']}\n"
            text += f"🏷️ Всего тегов: {stats['total_tags']}\n"
            text += f"📈 Активность сегодня: {stats['today_activity']} действий\n\n"

            # Конспекты по категориям
            text += "📂 КОНСПЕКТЫ ПО КАТЕГОРИЯМ\n"
            text += "-" * 30 + "\n"
            for category, count in stats['notes_by_category'].items():
                text += f"  {category}: {count}\n"
            text += "\n"

            # Популярные теги
            text += "🔥 ПОПУЛЯРНЫЕ ТЕГИ\n"
            text += "-" * 30 + "\n"
            for tag, count in stats['top_tags']:
                text += f"  #{tag}: {count} использований\n"

            # Активность
            activity = self.db.get_activity_stats(7)
            text += "\n📅 АКТИВНОСТЬ ЗА НЕДЕЛЮ\n"
            text += "-" * 30 + "\n"

            if activity and 'daily_activity' in activity:
                daily_data = activity['daily_activity']
                if daily_data:
                    for day in daily_data[-7:]:  # Последние 7 дней
                        if isinstance(day, (list, tuple)) and len(day) > 0:
                            date_str = str(day[0])  # Просто выводим как строку
                            text += f"  {date_str}: {day[1] if len(day) > 1 else 0} действий\n"

            # Обновление текстового поля
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, text)

            self.update_status("Статистика обновлена")

        except Exception as e:
            self.show_error(f"Ошибка загрузки статистики: {e}")

    def load_tags_stats(self):
        """Загрузка статистики тегов"""
        try:
            # Получение популярных тегов
            top_tags = self.db.get_top_tags(10)

            # Формирование текста
            text = "🏷️ СТАТИСТИКА ТЕГОВ\n"
            text += "=" * 40 + "\n\n"

            if top_tags:
                for i, (tag, count) in enumerate(top_tags, 1):
                    text += f"{i}. #{tag}: {count} использований\n"
            else:
                text += "Теги ещё не добавлены\n"

            # Обновление текстового поля
            self.tags_stats_text.delete(1.0, tk.END)
            self.tags_stats_text.insert(1.0, text)

        except Exception as e:
            self.show_error(f"Ошибка загрузки статистики тегов: {e}")

    def generate_excel_report(self):
        """Генерация Excel отчёта"""
        try:
            # Импортируем здесь, чтобы не замедлять запуск
            from reporting import ReportGenerator

            generator = ReportGenerator(self.db, self.fm)
            filepath = generator.generate_excel_report()

            self.update_status(f"Excel отчёт создан: {filepath}")
            messagebox.showinfo(
                "Успех",
                f"Excel отчёт успешно создан!\n{filepath}"
            )

        except ImportError as e:
            self.show_error(f"Модуль reporting.py не найден или содержит ошибки: {e}")
        except Exception as e:
            self.show_error(f"Ошибка генерации Excel отчёта: {e}")

    def generate_pdf_report(self):
        """Генерация PDF отчёта"""
        try:
            # Импортируем здесь, чтобы не замедлять запуск
            from reporting import ReportGenerator

            generator = ReportGenerator(self.db, self.fm)
            filepath = generator.generate_pdf_report()

            self.update_status(f"PDF отчёт создан: {filepath}")
            messagebox.showinfo(
                "Успех",
                f"PDF отчёт успешно создан!\n{filepath}"
            )

        except ImportError as e:
            self.show_error(f"Модуль reporting.py не найден или содержит ошибки: {e}")
        except Exception as e:
            self.show_error(f"Ошибка генерации PDF отчёта: {e}")

    def update_status(self, message: str):
        """Обновление статус бара"""
        if self.status_bar is None:
            print(f"Статус: {message}")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")

    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        logger.error(message)
        messagebox.showerror("Ошибка", message)
        self.update_status(f"Ошибка: {message}")

    def run(self):
        """Запуск главного цикла приложения"""
        self.root.mainloop()