import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import Database
from achievements import AchievementTracker
from export import ReportExporter
import json
from datetime import datetime


class AcademicTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Личный трекер академической школы")
        self.root.geometry("1100x750")

        # Инициализация компонентов
        self.db = Database()
        self.achievement_tracker = AchievementTracker(self.db)
        self.exporter = ReportExporter(self.db)

        # Загрузка компетенций
        self.competencies = self.load_competencies()
        self.specialty_var = tk.StringVar(value="Информационные системы")

        # Создание интерфейса
        self.create_menu()
        self.create_notebook()
        self.update_achievements()

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт отчёта", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню Настройки
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Выбор специальности", command=self.select_specialty)

    def create_notebook(self):
        """Создание вкладок"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Создание всех вкладок
        self.create_add_entry_tab()
        self.create_entries_tab()
        self.create_research_map_tab()
        self.create_achievements_tab()
        self.create_competencies_tab()
        self.create_goals_tab()

    # ============ ВКЛАДКА 1: ДОБАВЛЕНИЕ ЗАПИСИ ============
    def create_add_entry_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📝 Добавить запись")

        row = 0

        # Название
        ttk.Label(frame, text="Название:*").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        self.title_entry = ttk.Entry(frame, width=60)
        self.title_entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
        row += 1

        # Тип
        ttk.Label(frame, text="Тип:*").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        self.type_var = tk.StringVar()
        types = ['Проект', 'Публикация', 'Конференция', 'Практика', 'Грант']
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=types, state='readonly', width=57)
        self.type_combo.grid(row=row, column=1, padx=10, pady=5, sticky='w')
        row += 1

        # Дата
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):*").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        self.date_entry = ttk.Entry(frame, width=20)
        self.date_entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        row += 1

        # Соавторы
        ttk.Label(frame, text="Соавторы (через запятую):").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        self.authors_entry = ttk.Entry(frame, width=60)
        self.authors_entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
        row += 1

        # Ключевые слова
        ttk.Label(frame, text="Ключевые слова (до 5, через запятую):").grid(row=row, column=0, sticky='w', padx=10,
                                                                            pady=5)
        keywords_frame = ttk.Frame(frame)
        keywords_frame.grid(row=row, column=1, padx=10, pady=5, sticky='ew')

        self.keywords_entry = ttk.Entry(keywords_frame, width=50)
        self.keywords_entry.pack(side='left', fill='x', expand=True)

        # Кнопка подсказки ключевых слов
        ttk.Button(keywords_frame, text="📋", width=3,
                   command=self.show_keywords_suggestions).pack(side='right', padx=(5, 0))
        row += 1

        # Описание
        ttk.Label(frame, text="Описание:").grid(row=row, column=0, sticky='nw', padx=10, pady=5)
        self.description_text = scrolledtext.ScrolledText(frame, width=60, height=10)
        self.description_text.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # Компетенции
        ttk.Label(frame, text="Компетенции (выберите 1-3):").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        comp_frame = ttk.Frame(frame)
        comp_frame.grid(row=row, column=1, padx=10, pady=5, sticky='ew')

        self.competency_vars = []
        self.competency_levels = []

        # 3 строки для компетенций
        for i in range(3):
            var = tk.StringVar()
            level_var = tk.StringVar(value="1")

            combo = ttk.Combobox(comp_frame, textvariable=var, width=40, state='readonly')
            combo['values'] = self.get_current_competencies()
            combo.grid(row=i, column=0, padx=(0, 5), pady=2, sticky='w')

            level_combo = ttk.Combobox(comp_frame, textvariable=level_var, width=10, state='readonly')
            level_combo['values'] = ['1', '2', '3', '4', '5']
            level_combo.grid(row=i, column=1, pady=2, sticky='w')

            self.competency_vars.append(var)
            self.competency_levels.append(level_var)
        row += 1

        # Кнопка сохранения
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сохранить запись", command=self.save_entry).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)

        # Настройка расширения колонок
        frame.columnconfigure(1, weight=1)

    # ============ ВКЛАДКА 2: ВСЕ ЗАПИСИ ============
    def create_entries_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Все записи")

        # Панель поиска
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side='left', padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=(0, 5))
        ttk.Button(search_frame, text="Найти", command=self.search_entries).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Очистить", command=self.load_entries).pack(side='left')

        # Таблица записей
        columns = ("ID", "Название", "Тип", "Дата", "Соавторы", "Ключевые слова")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)

        # Настройка колонок
        col_widths = [50, 200, 100, 100, 150, 150]
        for idx, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[idx])

        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Размещение
        self.tree.pack(side="top", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Кнопки управления
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Обновить", command=self.load_entries).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить выбранное", command=self.delete_selected_entry).pack(side='left', padx=5)

        # Загрузка данных
        self.load_entries()

    # ============ ВКЛАДКА 3: ИССЛЕДОВАТЕЛЬСКАЯ КАРТА ============
    def create_research_map_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🗺️ Исследовательская карта")

        # Панель с двумя колонками
        paned = ttk.PanedWindow(frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая панель: ключевые слова
        left_frame = ttk.Frame(paned)
        ttk.Label(left_frame, text="📊 Ключевые слова", font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        self.keywords_text = scrolledtext.ScrolledText(left_frame, width=40, height=25)
        self.keywords_text.pack(fill='both', expand=True)

        # Правая панель: соавторы
        right_frame = ttk.Frame(paned)
        ttk.Label(right_frame, text="👥 Соавторы", font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        self.authors_text = scrolledtext.ScrolledText(right_frame, width=40, height=25)
        self.authors_text.pack(fill='both', expand=True)

        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=1)

        # Кнопка обновления
        ttk.Button(frame, text="Обновить статистику", command=self.update_research_map).pack(pady=10)

        # Первоначальная загрузка
        self.update_research_map()

    # ============ ВКЛАДКА 4: ДОСТИЖЕНИЯ ============
    def create_achievements_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏆 Достижения")

        ttk.Label(frame, text="Ваши достижения", font=('Arial', 14, 'bold')).pack(pady=10)

        # Область для отображения достижений
        self.achievements_text = scrolledtext.ScrolledText(frame, width=80, height=25, font=('Arial', 10))
        self.achievements_text.pack(fill='both', expand=True, padx=10, pady=5)

        # Кнопка проверки
        ttk.Button(frame, text="Проверить новые достижения", command=self.check_new_achievements).pack(pady=10)

        # Загрузка достижений
        self.load_achievements()

    # ============ ВКЛАДКА 5: КОМПЕТЕНЦИИ ============
    def create_competencies_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📈 Мои компетенции")

        # Верхняя часть: статистика
        stats_frame = ttk.LabelFrame(frame, text="Статистика компетенций")
        stats_frame.pack(fill='x', padx=10, pady=10)

        self.competencies_stats_text = scrolledtext.ScrolledText(stats_frame, height=10, width=80)
        self.competencies_stats_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Нижняя часть: рекомендации
        rec_frame = ttk.LabelFrame(frame, text="Рекомендации")
        rec_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.recommendations_text = scrolledtext.ScrolledText(rec_frame, height=10, width=80)
        self.recommendations_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Кнопка обновления
        ttk.Button(frame, text="Обновить профиль компетенций", command=self.update_competencies_profile).pack(pady=10)

        # Первоначальная загрузка
        self.update_competencies_profile()

    # ============ ВКЛАДКА 6: ЦЕЛИ НА СЕМЕСТР ============
    def create_goals_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎯 Цели на семестр")

        # Левая часть: добавление целей
        left_frame = ttk.Frame(frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left_frame, text="Новая цель", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        # Тип цели
        ttk.Label(left_frame, text="Тип цели:").pack(anchor='w')
        self.goal_type_var = tk.StringVar()
        goal_types = ['Количество записей', 'Уровень компетенции', 'Достижение', 'Другое']
        goal_combo = ttk.Combobox(left_frame, textvariable=self.goal_type_var, values=goal_types, state='readonly',
                                  width=30)
        goal_combo.pack(anchor='w', pady=(0, 10))

        # Описание цели
        ttk.Label(left_frame, text="Описание цели:").pack(anchor='w')
        self.goal_desc_entry = ttk.Entry(left_frame, width=40)
        self.goal_desc_entry.pack(anchor='w', pady=(0, 10))

        # Целевое значение
        ttk.Label(left_frame, text="Целевое значение:").pack(anchor='w')
        self.goal_target_entry = ttk.Entry(left_frame, width=20)
        self.goal_target_entry.pack(anchor='w', pady=(0, 10))

        # Кнопка добавления
        ttk.Button(left_frame, text="Добавить цель", command=self.add_goal).pack(pady=10)

        # Правая часть: список целей
        right_frame = ttk.Frame(frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Текущие цели", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

        self.goals_text = scrolledtext.ScrolledText(right_frame, width=50, height=20)
        self.goals_text.pack(fill='both', expand=True)

        # Кнопка обновления
        ttk.Button(right_frame, text="Обновить цели", command=self.load_goals).pack(pady=10)

        # Загрузка целей
        self.load_goals()

    # ============ ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ============

    def save_entry(self):
        """Сохранение новой записи"""
        try:
            # Получение данных из формы
            title = self.title_entry.get().strip()
            entry_type = self.type_var.get()
            date = self.date_entry.get().strip()
            authors = self.authors_entry.get().strip()
            description = self.description_text.get("1.0", tk.END).strip()
            keywords_str = self.keywords_entry.get().strip()

            # Валидация
            if not title or not entry_type or not date:
                messagebox.showerror("Ошибка", "Заполните обязательные поля (название, тип, дата)!")
                return

            # Проверка даты
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return

            # Сохранение записи в БД
            entry_id = self.db.add_entry(title, entry_type, date, description, authors)

            # Сохранение ключевых слов
            if keywords_str:
                keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
                if len(keywords) > 5:
                    keywords = keywords[:5]
                    messagebox.showwarning("Предупреждение", "Сохраняется только первые 5 ключевых слов")

                for keyword in keywords:
                    self.db.add_keyword_to_entry(entry_id, keyword)

            # Сохранение компетенций
            for i in range(3):
                comp_name = self.competency_vars[i].get().strip()
                level_str = self.competency_levels[i].get().strip()

                if comp_name and level_str:
                    try:
                        level = int(level_str)
                        if 1 <= level <= 5:
                            self.db.add_competency_to_entry(entry_id, comp_name, level)
                    except ValueError:
                        pass

            # Проверка достижений
            new_achievements = self.achievement_tracker.check_achievements()
            if new_achievements:
                achievements_text = "\n".join([f"🏆 {a}" for a in new_achievements])
                messagebox.showinfo("Новые достижения!", f"Разблокированы:\n{achievements_text}")

            messagebox.showinfo("Успех", "Запись успешно сохранена!")
            self.clear_form()
            self.load_entries()
            self.update_research_map()
            self.update_competencies_profile()
            self.load_achievements()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")

    def clear_form(self):
        """Очистка формы добавления записи"""
        self.title_entry.delete(0, tk.END)
        self.type_var.set('')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.authors_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.keywords_entry.delete(0, tk.END)

        for var in self.competency_vars:
            var.set('')
        for level_var in self.competency_levels:
            level_var.set('1')

    def load_entries(self):
        """Загрузка записей в таблицу"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение данных из БД
        entries = self.db.get_all_entries_with_keywords()

        # Заполнение таблицы
        for entry in entries:
            entry_id, title, entry_type, date, description, authors, keywords = entry
            short_desc = description[:50] + "..." if len(description) > 50 else description
            keywords_display = keywords if keywords else "нет"

            self.tree.insert("", "end", values=(
                entry_id,
                title,
                entry_type,
                date,
                authors if authors else "нет",
                keywords_display
            ))

    def search_entries(self):
        """Поиск записей"""
        search_text = self.search_entry.get().strip().lower()
        if not search_text:
            self.load_entries()
            return

        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Поиск в БД
        entries = self.db.search_entries(search_text)

        # Заполнение таблицы
        for entry in entries:
            entry_id, title, entry_type, date, description, authors, keywords = entry
            short_desc = description[:50] + "..." if len(description) > 50 else description
            keywords_display = keywords if keywords else "нет"

            self.tree.insert("", "end", values=(
                entry_id,
                title,
                entry_type,
                date,
                authors if authors else "нет",
                keywords_display
            ))

    def delete_selected_entry(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            item = self.tree.item(selected[0])
            entry_id = item['values'][0]

            self.db.delete_entry(entry_id)
            messagebox.showinfo("Успех", "Запись удалена")
            self.load_entries()
            self.update_research_map()
            self.update_competencies_profile()
            self.load_achievements()

    def update_research_map(self):
        """Обновление исследовательской карты"""
        # Ключевые слова
        keywords_stats = self.db.get_keywords_statistics()
        self.keywords_text.delete("1.0", tk.END)

        if keywords_stats:
            for keyword, count in keywords_stats:
                self.keywords_text.insert(tk.END, f"{keyword} — {count} записей\n")
        else:
            self.keywords_text.insert(tk.END, "Нет данных о ключевых словах\n")

        # Соавторы
        authors_stats = self.db.get_authors_statistics()
        self.authors_text.delete("1.0", tk.END)

        if authors_stats:
            for author, count in authors_stats:
                self.authors_text.insert(tk.END, f"{author} — {count} работ\n")
        else:
            self.authors_text.insert(tk.END, "Нет данных о соавторах\n")

    def load_achievements(self):
        """Загрузка достижений"""
        achievements = self.db.get_achievements()
        self.achievements_text.delete("1.0", tk.END)

        if achievements:
            for ach_id, name, description, obtained, date_obtained in achievements:
                status = "✅ ПОЛУЧЕНО" if obtained else "❌ Не получено"
                date_str = f" ({date_obtained})" if date_obtained else ""
                self.achievements_text.insert(tk.END, f"【{status}】 {name}\n")
                self.achievements_text.insert(tk.END, f"   {description}{date_str}\n\n")
        else:
            self.achievements_text.insert(tk.END, "Достижения еще не загружены\n")

    def check_new_achievements(self):
        """Проверка новых достижений"""
        new_achievements = self.achievement_tracker.check_achievements()
        if new_achievements:
            messagebox.showinfo("Поздравляем!", f"Получены новые достижения!\n" + "\n".join(new_achievements))
            self.load_achievements()
        else:
            messagebox.showinfo("Информация", "Новых достижений пока нет")

    def update_competencies_profile(self):
        """Обновление профиля компетенций"""
        stats = self.db.get_competencies_statistics()
        recommendations = self.db.get_recommendations()

        # Статистика
        self.competencies_stats_text.delete("1.0", tk.END)
        if stats:
            for comp_name, avg_level, count in stats:
                status = "⚠️ СЛАБАЯ ЗОНА" if avg_level < 3 else "✅"
                self.competencies_stats_text.insert(tk.END,
                                                    f"{status} {comp_name}: средний уровень {avg_level:.1f} ({count} оценок)\n")
        else:
            self.competencies_stats_text.insert(tk.END, "Нет данных о компетенциях\n")

        # Рекомендации
        self.recommendations_text.delete("1.0", tk.END)
        if recommendations:
            for rec in recommendations:
                self.recommendations_text.insert(tk.END, f"• {rec}\n")
        else:
            self.recommendations_text.insert(tk.END, "Пока нет рекомендаций. Добавьте больше записей!\n")

    def load_goals(self):
        """Загрузка целей"""
        goals = self.db.get_goals()
        self.goals_text.delete("1.0", tk.END)

        if goals:
            for goal_id, goal_type, description, target, current, completed in goals:
                status = "✅ ВЫПОЛНЕНО" if completed else "🔄 В процессе"
                progress = f"{current}/{target}"
                self.goals_text.insert(tk.END, f"【{status}】 {description}\n")
                self.goals_text.insert(tk.END, f"   Прогресс: {progress}\n\n")
        else:
            self.goals_text.insert(tk.END, "Цели еще не установлены\n")

    def add_goal(self):
        """Добавление новой цели"""
        goal_type = self.goal_type_var.get()
        description = self.goal_desc_entry.get().strip()
        target = self.goal_target_entry.get().strip()

        if not goal_type or not description or not target:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        try:
            target_value = int(target)
            self.db.add_goal(goal_type, description, target_value)
            messagebox.showinfo("Успех", "Цель добавлена")
            self.load_goals()

            # Очистка формы
            self.goal_desc_entry.delete(0, tk.END)
            self.goal_target_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Целевое значение должно быть числом!")

    def show_keywords_suggestions(self):
        """Показать подсказки по ключевым словам"""
        keywords = self.db.get_all_keywords()
        if keywords:
            suggestions = ", ".join(keywords[:10])  # Первые 10 ключевых слов
            messagebox.showinfo("Предыдущие ключевые слова",
                                f"Используемые ранее:\n{suggestions}")
        else:
            messagebox.showinfo("Информация", "Ключевые слова еще не использовались")

    def get_current_competencies(self):
        """Получение списка компетенций для текущей специальности"""
        specialty = self.specialty_var.get()
        if specialty in self.competencies:
            comp_list = []
            for category, comps in self.competencies[specialty].items():
                comp_list.extend(comps)
            return comp_list
        return []

    def select_specialty(self):
        """Окно выбора специальности"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор специальности")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Выберите вашу специальность:",
                  font=('Arial', 11, 'bold')).pack(pady=20)

        # Радиокнопки для выбора
        specialty_var = tk.StringVar(value=self.specialty_var.get())

        for specialty in self.competencies.keys():
            rb = ttk.Radiobutton(dialog, text=specialty,
                                 variable=specialty_var, value=specialty)
            rb.pack(anchor='w', padx=50, pady=5)

        def save_specialty():
            self.specialty_var.set(specialty_var.get())
            messagebox.showinfo("Сохранено", f"Специальность изменена на: {specialty_var.get()}")
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_specialty).pack(pady=20)

    def export_report(self):
        """Экспорт отчета в Word"""
        try:
            filename = f"отчет_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            self.exporter.export_to_word(filename)
            messagebox.showinfo("Успех", f"Отчёт сохранён в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчёт: {str(e)}")

    def load_competencies(self):
        """Загрузка компетенций из JSON файла"""
        try:
            with open('data/competencies.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Возвращаем демо-данные если файла нет
            return {
                "Информационные системы": {
                    "Технические": ["Программирование", "Базы данных", "Веб-разработка"],
                    "Soft Skills": ["Командная работа", "Презентация"]
                }
            }

    def update_achievements(self):
        """Проверка достижений при запуске"""
        self.achievement_tracker.check_achievements()