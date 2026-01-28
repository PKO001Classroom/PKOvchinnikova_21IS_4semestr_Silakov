# gui.py - ЭЛЕКТРОННЫЙ ПОРТФОЛИО СТУДЕНТА-ИССЛЕДОВАТЕЛЯ
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import traceback

# Добавляем текущую папку в путь поиска
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from database import Database
from file_handler import FileHandler


class PortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Электронный портфолио студента-исследователя")
        self.root.geometry("1200x750")

        # Устанавливаем иконку если есть
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

        # Центрирование окна
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Инициализация
        print("Инициализация приложения...")
        self.db = Database()
        self.file_handler = FileHandler()
        self.current_entry_id = None
        self.current_filepath = None

        # Создаем необходимые папки
        self.create_folders()

        self.create_widgets()
        self.load_entries()

        # Бинд на закрытие
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        print("✅ Приложение готово к работе")

    def create_folders(self):
        """Создание необходимых папок"""
        folders = ["reports", "portfolio_md", "screenshots"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✅ Создана папка: {folder}")

    def create_widgets(self):
        # Стиль
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Success.TLabel', foreground='green')

        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== ЛЕВАЯ ПАНЕЛЬ =====
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Панель управления записью
        control_frame = ttk.LabelFrame(left_panel, text="📋 Управление записью", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Поля ввода - сетка
        row = 0

        # Название
        ttk.Label(control_frame, text="Название:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky="w", pady=(0, 5))
        self.title_entry = ttk.Entry(control_frame, width=28, font=('Arial', 10))
        self.title_entry.grid(row=row, column=1, pady=(0, 5), padx=(10, 0))
        row += 1

        # Тип записи
        ttk.Label(control_frame, text="Тип:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky="w", pady=5)
        self.type_combo = ttk.Combobox(control_frame, values=[
            "Публикация", "Конференция", "Грант", "Преподавание", "Достижение"
        ], width=25, font=('Arial', 10), state="readonly")
        self.type_combo.grid(row=row, column=1, pady=5, padx=(10, 0))
        self.type_combo.current(0)
        row += 1

        # Год
        ttk.Label(control_frame, text="Год:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky="w", pady=5)
        self.year_entry = ttk.Entry(control_frame, width=28, font=('Arial', 10))
        self.year_entry.grid(row=row, column=1, pady=5, padx=(10, 0))
        self.year_entry.insert(0, "2024")
        row += 1

        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="➕ Создать", command=self.create_entry,
                   width=12).grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="💾 Сохранить", command=self.save_entry,
                   width=12).grid(row=0, column=1, padx=2)

        ttk.Button(button_frame, text="❌ Удалить", command=self.delete_entry,
                   width=12).grid(row=1, column=0, pady=5, padx=2)
        ttk.Button(button_frame, text="📄 Открыть", command=self.open_description,
                   width=12).grid(row=1, column=1, pady=5, padx=2)

        row += 1

        # Панель отчетов
        report_frame = ttk.LabelFrame(left_panel, text="📊 Отчеты", padding=15)
        report_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(report_frame, text="📈 Excel отчет", command=self.generate_excel_report,
                   width=25).pack(pady=3)
        ttk.Button(report_frame, text="📝 Word отчет", command=self.generate_word_report,
                   width=25).pack(pady=3)
        ttk.Button(report_frame, text="📋 Текстовый отчет", command=self.create_simple_report,
                   width=25).pack(pady=3)

        # Панель соавторов
        coauthor_frame = ttk.LabelFrame(left_panel, text="👥 Соавторы", padding=15)
        coauthor_frame.pack(fill=tk.X)

        ttk.Label(coauthor_frame, text="Добавить соавтора:",
                  font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))

        input_frame = ttk.Frame(coauthor_frame)
        input_frame.pack(fill=tk.X, pady=5)

        self.coauthor_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.coauthor_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(input_frame, text="➕ Добавить", command=self.add_coauthor,
                   width=10).pack(side=tk.RIGHT)

        self.coauthors_label = ttk.Label(coauthor_frame, text="Соавторы не добавлены",
                                         wraplength=250, font=('Arial', 9),
                                         foreground="blue", justify=tk.LEFT)
        self.coauthors_label.pack(anchor="w", pady=10)

        # ===== ПРАВАЯ ПАНЕЛЬ =====
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Панель списка записей
        list_frame = ttk.LabelFrame(right_panel, text="📚 Все записи", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Таблица записей с прокруткой
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем Treeview с колонками
        columns = ("ID", "Название", "Тип", "Год", "Создано")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        # Настройка колонок
        col_configs = [
            ("ID", 50, tk.CENTER),
            ("Название", 250, tk.W),
            ("Тип", 100, tk.CENTER),
            ("Год", 70, tk.CENTER),
            ("Создано", 150, tk.CENTER)
        ]

        for i, (col_text, width, anchor) in enumerate(col_configs):
            self.tree.heading(columns[i], text=col_text)
            self.tree.column(columns[i], width=width, anchor=anchor)

        # Прокрутка
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Бинд события выбора
        self.tree.bind("<<TreeviewSelect>>", self.on_entry_select)

        # Панель редактирования описания
        edit_frame = ttk.LabelFrame(right_panel, text="✏️ Редактирование описания (Markdown)", padding=10)
        edit_frame.pack(fill=tk.BOTH, expand=True)

        # Текстовое поле с прокруткой
        self.text_area = scrolledtext.ScrolledText(edit_frame, wrap=tk.WORD,
                                                   font=('Consolas', 10),
                                                   undo=True, maxundo=-1)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Подсказки по синтаксису
        help_frame = ttk.Frame(edit_frame)
        help_frame.pack(fill=tk.X, pady=(5, 0))

        help_text = "💡 Подсказки:  # Заголовок  ## Подзаголовок  > Цитата  ```код```  [ссылка](url)  **жирный**"
        ttk.Label(help_frame, text=help_text, font=('Arial', 9),
                  foreground="gray").pack(anchor="w")

    def load_entries(self):
        """Загрузка записей в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            entries = self.db.get_all_entries()

            if not entries:
                # Добавляем сообщение если нет записей
                self.tree.insert("", "end", values=("", "Нет записей", "", "", ""))
                return

            for entry in entries:
                # Форматируем дату
                created_at = entry['created_at']
                if created_at:
                    if isinstance(created_at, str):
                        date_str = created_at[:19].replace('T', ' ')
                    else:
                        date_str = created_at.strftime("%d.%m.%Y %H:%M")
                else:
                    date_str = ""

                # Вставляем запись
                self.tree.insert("", "end", values=(
                    entry['id'],
                    entry['title'][:50] + "..." if len(entry['title']) > 50 else entry['title'],
                    entry['entry_type'],
                    entry['year'] if entry['year'] else "",
                    date_str
                ))

            print(f"✅ Загружено {len(entries)} записей")

        except Exception as e:
            print(f"❌ Ошибка загрузки записей: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить записи:\n{str(e)}")

    def create_entry(self):
        """Создание новой записи"""
        title = self.title_entry.get().strip()
        entry_type = self.type_combo.get()
        year_text = self.year_entry.get().strip()

        # Валидация
        if not title:
            messagebox.showerror("Ошибка", "Введите название записи!")
            return

        if not entry_type:
            messagebox.showerror("Ошибка", "Выберите тип записи!")
            return

        # Проверка года
        year = None
        if year_text:
            try:
                year = int(year_text)
                if year < 1900 or year > 2100:
                    messagebox.showerror("Ошибка", "Год должен быть между 1900 и 2100")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Год должен быть числом!")
                return

        try:
            print(f"Создание записи: {title} ({entry_type}, {year})")

            # Создаем файл с описанием
            content = self.text_area.get(1.0, tk.END).strip()
            filepath = self.file_handler.create_md_file(title, content)
            print(f"Создан файл: {filepath}")

            # Добавляем в БД
            entry_id = self.db.create_entry(title, entry_type, year, filepath)
            print(f"Создана запись в БД, ID: {entry_id}")

            messagebox.showinfo("Успех", f"Запись создана!\nID: {entry_id}")

            # Обновляем список и очищаем поля
            self.load_entries()
            self.clear_fields()

        except Exception as e:
            print(f"❌ Ошибка создания записи: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка создания записи:\n{str(e)}")

    def clear_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, "2024")
        self.text_area.delete(1.0, tk.END)
        self.coauthors_label.config(text="Соавторы не добавлены")
        self.coauthor_entry.delete(0, tk.END)
        self.current_entry_id = None
        self.current_filepath = None

    def on_entry_select(self, event):
        """Выбор записи из таблицы"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        # Пропускаем сообщение "Нет записей"
        if not values[0]:
            return

        self.current_entry_id = values[0]
        print(f"Выбрана запись ID: {self.current_entry_id}")

        try:
            # Получаем полные данные записи
            entries = self.db.get_all_entries()
            for entry in entries:
                if entry['id'] == self.current_entry_id:
                    # Заполняем поля
                    self.title_entry.delete(0, tk.END)
                    self.title_entry.insert(0, entry['title'])

                    # Устанавливаем тип
                    for i, val in enumerate(self.type_combo['values']):
                        if val == entry['entry_type']:
                            self.type_combo.current(i)
                            break

                    # Год
                    self.year_entry.delete(0, tk.END)
                    if entry['year']:
                        self.year_entry.insert(0, str(entry['year']))
                    else:
                        self.year_entry.insert(0, "2024")

                    # Описание
                    self.current_filepath = entry['file_path']
                    content = self.file_handler.read_md_file(self.current_filepath)
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)

                    # Соавторы
                    coauthors = self.db.get_coauthors(self.current_entry_id)
                    if coauthors:
                        self.coauthors_label.config(text=f"Соавторы: {', '.join(coauthors)}")
                    else:
                        self.coauthors_label.config(text="Соавторы не добавлены")

                    print(f"Загружено описание из: {self.current_filepath}")
                    break

            # Логируем просмотр
            self.db.cursor.execute(
                "INSERT INTO activity_log (entry_id, event_type) VALUES (%s, 'VIEW')",
                (self.current_entry_id,)
            )
            self.db.conn.commit()

        except Exception as e:
            print(f"❌ Ошибка при выборе записи: {e}")
            traceback.print_exc()

    def save_entry(self):
        """Сохранение изменений"""
        if not self.current_entry_id:
            messagebox.showerror("Ошибка", "Сначала выберите запись для редактирования!")
            return

        title = self.title_entry.get().strip()
        entry_type = self.type_combo.get()
        year_text = self.year_entry.get().strip()

        # Валидация
        if not title:
            messagebox.showerror("Ошибка", "Введите название записи!")
            return

        if not entry_type:
            messagebox.showerror("Ошибка", "Выберите тип записи!")
            return

        # Проверка года
        year = None
        if year_text:
            try:
                year = int(year_text)
                if year < 1900 or year > 2100:
                    messagebox.showerror("Ошибка", "Год должен быть между 1900 и 2100")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Год должен быть числом!")
                return

        try:
            print(f"Сохранение записи ID: {self.current_entry_id}")

            # Обновляем в БД
            self.db.update_entry(self.current_entry_id, title, entry_type, year)

            # Обновляем файл
            if self.current_filepath and os.path.exists(self.current_filepath):
                content = self.text_area.get(1.0, tk.END).strip()
                self.file_handler.update_md_file(self.current_filepath, content)
                print(f"Обновлен файл: {self.current_filepath}")

            messagebox.showinfo("Успех", "Изменения сохранены!")
            self.load_entries()

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def delete_entry(self):
        """Удаление записи"""
        if not self.current_entry_id:
            messagebox.showerror("Ошибка", "Сначала выберите запись для удаления!")
            return

        title = self.title_entry.get()
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить запись '{title}'?\nЭто действие нельзя отменить!"):
            return

        try:
            print(f"Удаление записи ID: {self.current_entry_id}")

            # Удаляем файл если существует
            if self.current_filepath and os.path.exists(self.current_filepath):
                try:
                    os.remove(self.current_filepath)
                    print(f"Удален файл: {self.current_filepath}")
                except Exception as e:
                    print(f"Не удалось удалить файл: {e}")

            # Удаляем из БД
            self.db.delete_entry(self.current_entry_id)

            # Очищаем поля
            self.clear_fields()

            messagebox.showinfo("Успех", "Запись удалена!")
            self.load_entries()

        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка удаления:\n{str(e)}")

    def add_coauthor(self):
        """Добавление соавтора"""
        if not self.current_entry_id:
            messagebox.showerror("Ошибка", "Сначала выберите запись!")
            return

        name = self.coauthor_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите имя соавтора!")
            return

        try:
            print(f"Добавление соавтора '{name}' к записи ID: {self.current_entry_id}")

            self.db.add_coauthor(self.current_entry_id, name)

            # Обновляем список соавторов
            coauthors = self.db.get_coauthors(self.current_entry_id)
            if coauthors:
                self.coauthors_label.config(text=f"Соавторы: {', '.join(coauthors)}")

            self.coauthor_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", f"Соавтор '{name}' добавлен!")

        except Exception as e:
            print(f"❌ Ошибка добавления соавтора: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка добавления соавтора:\n{str(e)}")

    def open_description(self):
        """Открытие .md файла"""
        if not self.current_filepath:
            messagebox.showerror("Ошибка", "Сначала выберите запись!")
            return

        try:
            if os.path.exists(self.current_filepath):
                print(f"Открытие файла: {self.current_filepath}")
                self.file_handler.open_file(self.current_filepath)
            else:
                messagebox.showerror("Ошибка", f"Файл не найден:\n{self.current_filepath}")
        except Exception as e:
            print(f"❌ Ошибка открытия файла: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка открытия файла:\n{str(e)}")

    def generate_excel_report(self):
        """Генерация Excel отчета"""
        try:
            print("Создание Excel отчета...")

            # Проверяем наличие модуля
            try:
                from exporter import ReportGenerator
                generator = ReportGenerator(self.db)
                filename = generator.generate_excel_report()

                if filename and os.path.exists(filename):
                    abs_path = os.path.abspath(filename)
                    messagebox.showinfo("Успех",
                                        f"Excel отчет создан!\n\n"
                                        f"Файл: {os.path.basename(filename)}\n"
                                        f"Папка: {os.path.dirname(abs_path)}")

                    # Пробуем открыть
                    try:
                        os.startfile(abs_path)
                    except:
                        pass  # Не критично
                else:
                    # Пробуем создать текстовый отчет
                    messagebox.showinfo("Информация",
                                        "Не удалось создать Excel отчет.\n"
                                        "Создаю текстовый отчет...")
                    self.create_simple_report()

            except ImportError:
                messagebox.showinfo("Информация",
                                    "Библиотеки для Excel отчета не установлены.\n"
                                    "Используйте текстовый отчет.")
            except Exception as e:
                print(f"Ошибка Excel отчета: {e}")
                traceback.print_exc()
                self.create_simple_report()

        except Exception as e:
            print(f"❌ Общая ошибка Excel отчета: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка создания Excel отчета:\n{str(e)}")

    def generate_word_report(self):
        """Генерация Word отчета"""
        try:
            print("Создание Word отчета...")

            # Проверяем наличие модуля
            try:
                from exporter import ReportGenerator
                generator = ReportGenerator(self.db)
                filename = generator.generate_word_report()

                if filename and os.path.exists(filename):
                    abs_path = os.path.abspath(filename)
                    messagebox.showinfo("Успех",
                                        f"Word отчет создан!\n\n"
                                        f"Файл: {os.path.basename(filename)}\n"
                                        f"Папка: {os.path.dirname(abs_path)}")

                    # Пробуем открыть
                    try:
                        os.startfile(abs_path)
                    except:
                        pass  # Не критично
                else:
                    # Пробуем создать текстовый отчет
                    messagebox.showinfo("Информация",
                                        "Не удалось создать Word отчет.\n"
                                        "Создаю текстовый отчет...")
                    self.create_simple_report()

            except ImportError:
                messagebox.showinfo("Информация",
                                    "Библиотеки для Word отчета не установлены.\n"
                                    "Используйте текстовый отчет.")
            except Exception as e:
                print(f"Ошибка Word отчета: {e}")
                traceback.print_exc()
                self.create_simple_report()

        except Exception as e:
            print(f"❌ Общая ошибка Word отчета: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка создания Word отчета:\n{str(e)}")

    def create_simple_report(self):
        """Создание текстового отчета (гарантированно работает)"""
        try:
            from datetime import datetime

            print("Создание текстового отчета...")

            # Убеждаемся, что папка существует
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                print(f"✅ Создана папка: {reports_dir}")

            # Получаем данные
            entries = self.db.get_all_entries()
            stats = self.db.get_statistics()

            # Создаем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"portfolio_report_{timestamp}.txt")

            # Абсолютный путь для надежности
            abs_filename = os.path.abspath(filename)

            # Создаем отчет
            with open(abs_filename, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write("ЭЛЕКТРОННЫЙ ПОРТФОЛИО СТУДЕНТА-ИССЛЕДОВАТЕЛЯ\n")
                f.write("=" * 70 + "\n")
                f.write(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Всего записей: {stats.get('total', 0)}\n")
                f.write(f"Уникальных соавторов: {stats.get('unique_coauthors', 0)}\n")
                f.write("-" * 70 + "\n\n")

                # Статистика по типам
                f.write("СТАТИСТИКА ПО ТИПАМ ЗАПИСЕЙ:\n")
                f.write("-" * 40 + "\n")
                by_type = stats.get('by_type', [])
                if by_type:
                    for item in by_type:
                        entry_type = item.get('entry_type', 'Неизвестно')
                        count = item.get('count', 0)
                        f.write(f"{entry_type:20} | {count:3} записей\n")
                else:
                    f.write("Нет данных\n")
                f.write(f"{'ВСЕГО':20} | {stats.get('total', 0):3} записей\n\n")

                # Распределение по годам
                f.write("РАСПРЕДЕЛЕНИЕ ПО ГОДАМ:\n")
                f.write("-" * 40 + "\n")
                by_year = stats.get('by_year', [])
                if by_year:
                    for item in by_year:
                        year = item.get('year', '')
                        count = item.get('count', 0)
                        f.write(f"{year:6} год | {count:3} записей\n")
                else:
                    f.write("Нет данных\n\n")

                # Последние записи
                f.write("СПИСОК ЗАПИСЕЙ:\n")
                f.write("-" * 70 + "\n")
                if entries:
                    for entry in entries:
                        f.write(f"ID: {entry.get('id', '')}\n")
                        f.write(f"Название: {entry.get('title', '')}\n")
                        f.write(f"Тип: {entry.get('entry_type', '')}\n")
                        f.write(f"Год: {entry.get('year', 'Не указан')}\n")

                        # Соавторы
                        coauthors = self.db.get_coauthors(entry.get('id'))
                        if coauthors:
                            f.write(f"Соавторы: {', '.join(coauthors)}\n")

                        created = entry.get('created_at', '')
                        if created:
                            if isinstance(created, str):
                                f.write(f"Создано: {created[:19]}\n")
                            else:
                                f.write(f"Создано: {created.strftime('%d.%m.%Y %H:%M')}\n")

                        f.write("-" * 50 + "\n")
                else:
                    f.write("Записей нет\n")

                f.write("\n" + "=" * 70 + "\n")
                f.write("КОНЕЦ ОТЧЕТА\n")
                f.write("=" * 70 + "\n")

            print(f"✅ Текстовый отчет создан: {abs_filename}")

            # Проверяем, что файл действительно создан
            if os.path.exists(abs_filename):
                file_size = os.path.getsize(abs_filename)
                print(f"Размер файла: {file_size} байт")

                messagebox.showinfo("Успех",
                                    f"✅ Текстовый отчет создан!\n\n"
                                    f"📄 Файл: portfolio_report_{timestamp}.txt\n"
                                    f"📁 Папка: {reports_dir}\n"
                                    f"📊 Записей в отчете: {len(entries)}\n\n"
                                    f"Отчет содержит:\n"
                                    f"- Статистику по типам записей\n"
                                    f"- Распределение по годам\n"
                                    f"- Полный список записей с соавторами")

                # Предлагаем открыть файл
                if messagebox.askyesno("Открыть отчет", "Открыть созданный отчет?"):
                    try:
                        os.startfile(abs_filename)
                    except Exception as open_error:
                        print(f"Не удалось открыть файл: {open_error}")
                        # Показываем путь к файлу
                        messagebox.showinfo("Путь к файлу",
                                            f"Файл находится по адресу:\n{abs_filename}")
            else:
                # Создаем простейший отчет в текущей папке
                simple_filename = f"portfolio_report_{timestamp}.txt"
                with open(simple_filename, "w", encoding="utf-8") as f:
                    f.write(f"Отчет портфолио\n")
                    f.write(f"Создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                    f.write(f"Записей: {len(entries)}\n")

                simple_path = os.path.abspath(simple_filename)
                messagebox.showinfo("Успех",
                                    f"✅ Отчет создан!\n\n"
                                    f"Файл: {simple_filename}\n"
                                    f"Путь: {simple_path}")

        except Exception as e:
            print(f"❌ Ошибка создания текстового отчета: {e}")
            traceback.print_exc()

            # Пробуем создать максимально простой отчет
            try:
                simple_name = f"report_error_{datetime.now().strftime('%H%M%S')}.txt"
                with open(simple_name, "w") as f:
                    f.write("Отчет портфолио\n")
                    f.write(f"Ошибка: {str(e)[:100]}\n")

                messagebox.showinfo("Информация",
                                    f"Создан простой отчет:\n{simple_name}")
            except:
                messagebox.showerror("Критическая ошибка",
                                     f"Не удалось создать отчет:\n{str(e)}")

    def on_closing(self):
        """Закрытие приложения"""
        try:
            print("Закрытие приложения...")
            self.db.close()
            print("✅ Соединение с БД закрыто")
            self.root.destroy()
            print("✅ Приложение закрыто")
        except Exception as e:
            print(f"❌ Ошибка при закрытии: {e}")
            self.root.destroy()


# Точка входа
if __name__ == "__main__":
    try:
        print("=" * 50)
        print("ЗАПУСК ПРИЛОЖЕНИЯ 'ЭЛЕКТРОННЫЙ ПОРТФОЛИО'")
        print("=" * 50)

        root = tk.Tk()
        app = PortfolioApp(root)

        # Запуск главного цикла
        root.mainloop()

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()

        # Показываем ошибку пользователю
        error_msg = f"Не удалось запустить приложение:\n\n{str(e)}"
        tk.messagebox.showerror("Критическая ошибка", error_msg)

        input("Нажмите Enter для выхода...")