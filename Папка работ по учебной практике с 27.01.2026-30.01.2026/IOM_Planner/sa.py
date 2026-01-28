import tkinter as tk
from tkinter import ttk, messagebox
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import sqlite3
import json
import os
from datetime import datetime


# Функции для работы с базой данных
def init_database():
    conn = sqlite3.connect('iom.db')
    c = conn.cursor()

    # Таблица цели
    c.execute('''
        CREATE TABLE IF NOT EXISTS цели (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT NOT NULL,
            тип TEXT NOT NULL,
            статус TEXT DEFAULT 'Новая',
            план_дата TEXT,
            факт_дата TEXT,
            темп TEXT,
            описание TEXT
        )
    ''')

    # Таблица навыка
    c.execute('''
        CREATE TABLE IF NOT EXISTS навыка (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT UNIQUE NOT NULL
        )
    ''')

    # Таблица цель_навыки
    c.execute('''
        CREATE TABLE IF NOT EXISTS цель_навыки (
            цель_id INTEGER,
            навык_id INTEGER,
            FOREIGN KEY (цель_id) REFERENCES цели (id),
            FOREIGN KEY (навык_id) REFERENCES навыка (id)
        )
    ''')

    # Таблица компетенции
    c.execute('''
        CREATE TABLE IF NOT EXISTS компетенции (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT NOT NULL,
            категория TEXT
        )
    ''')

    # Таблица цель_компетенции
    c.execute('''
        CREATE TABLE IF NOT EXISTS цель_компетенции (
            цель_id INTEGER,
            компетенция_id INTEGER,
            уровень INTEGER CHECK (уровень BETWEEN 1 AND 5),
            FOREIGN KEY (цель_id) REFERENCES цели (id),
            FOREIGN KEY (компетенция_id) REFERENCES компетенции (id)
        )
    ''')

    # Таблица достижения
    c.execute('''
        CREATE TABLE IF NOT EXISTS достижения (
            код TEXT PRIMARY KEY,
            название TEXT NOT NULL,
            описание TEXT,
            получено INTEGER DEFAULT 0
        )
    ''')

    # Таблица цель_каса
    c.execute('''
        CREATE TABLE IF NOT EXISTS цель_каса (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            текст_цели TEXT NOT NULL,
            тип_цели TEXT,
            параметр TEXT,
            текущий_прогресс INTEGER DEFAULT 0,
            целевой_прогресс INTEGER NOT NULL
        )
    ''')

    # Заполняем достижения начальными данными
    achievements = [
        ('ach1', 'Старт', 'Создана первая цель', 0),
        ('ach2', 'Пунктуальный', 'Три или более завершённых целей в срок', 0),
        ('ach3', 'Многогранный', 'Есть цели минимум трёх разных типов', 0),
        ('ach4', 'Навыковый рост', 'У одного навыка четыре или более связанных завершённых целей', 0),
        ('ach5', 'Планирование', 'Одновременно в статусе "В процессе" пять или более целей', 0)
    ]

    c.execute("SELECT COUNT(*) FROM достижения")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO достижения VALUES (?, ?, ?, ?)", achievements)

    conn.commit()
    conn.close()


def load_competencies_to_db():
    conn = sqlite3.connect('iom.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM компетенции")
    if c.fetchone()[0] == 0 and os.path.exists('competencies.json'):
        with open('competencies.json', 'r', encoding='utf-8') as f:
            competencies = json.load(f)
            for comp in competencies:
                c.execute("INSERT INTO компетенции (название, категория) VALUES (?, ?)",
                          (comp['название'], comp['категория']))

    conn.commit()
    conn.close()


class IOMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Планировщик индивидуального образовательного маршрута")
        self.root.geometry("1000x700")

        # Инициализация БД
        init_database()
        load_competencies_to_db()

        # Создание виджетов
        self.create_widgets()
        self.update_stats()

    def create_widgets(self):
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Вкладка 1: Мои цели
        self.tab_goals = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_goals, text='Мои цели')
        self.create_goals_tab()

        # Вкладка 2: Мой профиль
        self.tab_profile = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_profile, text='Мой профиль')
        self.create_profile_tab()

        # Вкладка 3: Компетенции
        self.tab_competencies = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_competencies, text='Компетенции')
        self.create_competencies_tab()

        # Вкладка 4: Достижения
        self.tab_achievements = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_achievements, text='Достижения')
        self.create_achievements_tab()

        # Вкладка 5: Цели на семестр
        self.tab_semester = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_semester, text='Цели на семестр')
        self.create_semester_tab()

        # Вкладка 6: Настройки
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text='Настройки')
        self.create_settings_tab()

    def create_goals_tab(self):
        # Фрейм для списка целей
        list_frame = ttk.Frame(self.tab_goals)
        list_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Treeview для отображения целей
        self.goals_tree = ttk.Treeview(list_frame, columns=('ID', 'Название', 'Тип', 'Статус'), show='headings')
        self.goals_tree.heading('ID', text='ID')
        self.goals_tree.heading('Название', text='Название')
        self.goals_tree.heading('Тип', text='Тип')
        self.goals_tree.heading('Статус', text='Статус')
        self.goals_tree.pack(fill='both', expand=True)

        # Добавление кнопок
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text='Добавить', command=self.add_goal).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='Редактировать', command=self.edit_goal).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='Удалить', command=self.delete_goal).pack(side='left', padx=2)
        ttk.Button(btn_frame, text='Обновить', command=self.refresh_goals).pack(side='left', padx=2)

        # Фрейм для формы
        form_frame = ttk.Frame(self.tab_goals)
        form_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        # Здесь будут поля для ввода (название, тип, статус, даты и т.д.)
        # ...

        self.refresh_goals()

    def add_goal(self):
        # Создаем окно для добавления цели
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Добавить цель")

        # Поля ввода
        ttk.Label(self.add_window, text="Название:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.name_entry = ttk.Entry(self.add_window, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.add_window, text="Тип:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.type_combo = ttk.Combobox(self.add_window,
                                       values=['Курс', 'Проект', 'Самообразование', 'Семинар', 'Другое'])
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.add_window, text="Статус:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.status_combo = ttk.Combobox(self.add_window,
                                         values=['Новая', 'В процессе', 'Завершена', 'Отменена'])
        self.status_combo.grid(row=2, column=1, padx=5, pady=5)
        self.status_combo.set('Новая')

        ttk.Label(self.add_window, text="Плановая дата (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky='w', padx=5,
                                                                            pady=5)
        self.plan_date_entry = ttk.Entry(self.add_window)
        self.plan_date_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.add_window, text="Фактическая дата (ГГГГ-ММ-ДД):").grid(row=4, column=0, sticky='w',
                                                                               padx=5, pady=5)
        self.fact_date_entry = ttk.Entry(self.add_window)
        self.fact_date_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.add_window, text="Описание (простая разметка):").grid(row=5, column=0, sticky='nw',
                                                                             padx=5, pady=5)
        self.desc_text = tk.Text(self.add_window, width=40, height=10)
        self.desc_text.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(self.add_window, text="Сохранить", command=self.save_goal).grid(row=6, column=1, sticky='e', padx=5,
                                                                                   pady=10)

    def parse_simple_markdown(self, text):
        lines = text.split('\n')
        result_lines = []
        for line in lines:
            if line.startswith('- '):
                result_lines.append('• ' + line[2:])
            elif line.startswith('# '):
                result_lines.append('ЗАГОЛОВОК: ' + line[2:])
            else:
                # Обработка **текст** (жирный)
                line = line.replace('**', '')  # В Tkinter просто убираем звёздочки
                # Обработка [текст](ссылка)
                if '[' in line and ']' in line and '(' in line and ')' in line:
                    start = line.find('[')
                    end = line.find(']')
                    link_start = line.find('(')
                    link_end = line.find(')')
                    text = line[start + 1:end]
                    link = line[link_start + 1:link_end]
                    line = line[:start] + text + ' (' + link + ')' + line[link_end + 1:]
                result_lines.append(line)
        return '\n'.join(result_lines)

    def refresh_goals(self):
        # Очищаем дерево
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)

        # Загружаем данные из БД
        conn = sqlite3.connect('iom.db')
        c = conn.cursor()
        c.execute("SELECT id, название, тип, статус FROM цели")
        goals = c.fetchall()

        for goal in goals:
            self.goals_tree.insert('', 'end', values=goal)

        conn.close()

    def save_goal(self):
        # Получаем данные из полей ввода
        name = self.name_entry.get()
        goal_type = self.type_combo.get()
        status = self.status_combo.get()
        plan_date = self.plan_date_entry.get()
        fact_date = self.fact_date_entry.get()
        description = self.desc_text.get("1.0", tk.END).strip()

        if not name or not goal_type or not status:
            messagebox.showerror("Ошибка", "Заполните обязательные поля: Название, Тип, Статус")
            return

        # Сохраняем в БД
        conn = sqlite3.connect('iom.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO цели (название, тип, статус, план_дата, факт_дата, описание)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, goal_type, status, plan_date, fact_date, description))

        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Цель добавлена")
        self.add_window.destroy()
        self.refresh_goals()
        self.check_achievements()

    def edit_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите цель для редактирования")
            return

        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]

        # Открываем окно редактирования
        self.edit_goal_window(goal_id)

    def delete_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите цель для удаления")
            return

        item = self.goals_tree.item(selected[0])
        goal_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Удалить выбранную цель?"):
            conn = sqlite3.connect('iom.db')
            c = conn.cursor()
            c.execute("DELETE FROM цели WHERE id = ?", (goal_id,))
            conn.commit()
            conn.close()

            self.refresh_goals()
            self.check_achievements()

    def edit_goal_window(self, goal_id):
        # Загружаем данные цели
        conn = sqlite3.connect('iom.db')
        c = conn.cursor()
        c.execute("SELECT * FROM цели WHERE id = ?", (goal_id,))
        goal = c.fetchone()
        conn.close()

        if not goal:
            return

        # Создаем окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать цель")

        ttk.Label(edit_window, text="Название:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        name_entry = ttk.Entry(edit_window, width=40)
        name_entry.insert(0, goal[1])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Тип:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        type_combo = ttk.Combobox(edit_window, values=['Курс', 'Проект', 'Самообразование', 'Семинар', 'Другое'])
        type_combo.set(goal[2])
        type_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Статус:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        status_combo = ttk.Combobox(edit_window, values=['Новая', 'В процессе', 'Завершена', 'Отменена'])
        status_combo.set(goal[3])
        status_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Плановая дата (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        plan_date_entry = ttk.Entry(edit_window)
        plan_date_entry.insert(0, goal[4] if goal[4] else '')
        plan_date_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Фактическая дата (ГГГГ-ММ-ДД):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        fact_date_entry = ttk.Entry(edit_window)
        fact_date_entry.insert(0, goal[5] if goal[5] else '')
        fact_date_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Описание:").grid(row=5, column=0, sticky='nw', padx=5, pady=5)
        desc_text = tk.Text(edit_window, width=40, height=10)
        desc_text.insert("1.0", goal[7] if goal[7] else '')
        desc_text.grid(row=5, column=1, padx=5, pady=5)

        def save_changes():
            conn = sqlite3.connect('iom.db')
            c = conn.cursor()
            c.execute('''
                UPDATE цели 
                SET название = ?, тип = ?, статус = ?, план_дата = ?, факт_дата = ?, описание = ?
                WHERE id = ?
            ''', (
                name_entry.get(),
                type_combo.get(),
                status_combo.get(),
                plan_date_entry.get(),
                fact_date_entry.get(),
                desc_text.get("1.0", tk.END).strip(),
                goal_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Цель обновлена")
            edit_window.destroy()
            self.refresh_goals()
            self.check_achievements()

        ttk.Button(edit_window, text="Сохранить", command=save_changes).grid(row=6, column=1, sticky='e', padx=5,
                                                                             pady=10)

    def check_achievements(self):
        # Проверяем и обновляем достижения
        conn = sqlite3.connect('iom.db')
        c = conn.cursor()

        # 1. Проверка на первую цель
        c.execute("SELECT COUNT(*) FROM цели")
        goal_count = c.fetchone()[0]
        if goal_count >= 1:
            c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach1'")

        conn.commit()
        conn.close()

    def update_stats(self):
        # Обновление статистики (заглушка)
        pass

    def create_profile_tab(self):
        ttk.Label(self.tab_profile, text="Мой профиль", font=("Arial", 14, "bold")).pack(pady=10)
        # Здесь будет статистика

    def create_competencies_tab(self):
        ttk.Label(self.tab_competencies, text="Компетенции", font=("Arial", 14, "bold")).pack(pady=10)
        # Здесь будет список компетенций

    def create_achievements_tab(self):
        ttk.Label(self.tab_achievements, text="Достижения", font=("Arial", 14, "bold")).pack(pady=10)
        # Здесь будет список достижений

    def create_semester_tab(self):
        ttk.Label(self.tab_semester, text="Цели на семестр", font=("Arial", 14, "bold")).pack(pady=10)
        # Здесь будут цели на семестр

    def create_settings_tab(self):
        ttk.Label(self.tab_settings, text="Настройки", font=("Arial", 14, "bold")).pack(pady=10)
        # Здесь будут настройки


if __name__ == "__main__":
    root = tk.Tk()
    app = IOMApp(root)
    root.mainloop()


    def create_profile_tab(self):
        # Заголовок
        title_frame = ttk.Frame(self.tab_profile)
        title_frame.pack(fill='x', pady=10)
        ttk.Label(title_frame, text="Мой профиль", font=("Arial", 14, "bold")).pack()

        # Фрейм для статистики
        stats_frame = ttk.LabelFrame(self.tab_profile, text="Статистика")
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Навыки
        skills_frame = ttk.LabelFrame(stats_frame, text="Навыки")
        skills_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.skills_tree = ttk.Treeview(skills_frame, columns=('Навык', 'Количество целей'), show='headings', height=8)
        self.skills_tree.heading('Навык', text='Навык')
        self.skills_tree.heading('Количество целей', text='Количество целей')
        self.skills_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Статистика по типам целей
        types_frame = ttk.LabelFrame(stats_frame, text="Статистика по типам целей")
        types_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.types_tree = ttk.Treeview(types_frame, columns=('Тип', 'Завершено', 'Всего'), show='headings', height=5)
        self.types_tree.heading('Тип', text='Тип')
        self.types_tree.heading('Завершено', text='Завершено')
        self.types_tree.heading('Всего', text='Всего')
        self.types_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Процент целей, завершённых в срок
        timely_frame = ttk.Frame(stats_frame)
        timely_frame.pack(fill='x', padx=5, pady=5)
        self.timely_label = ttk.Label(timely_frame, text="Процент целей, завершённых в срок: 0%")
        self.timely_label.pack()

        # Кнопка обновления
        ttk.Button(stats_frame, text="Обновить статистику", command=self.update_profile_stats).pack(pady=10)

        # Первоначальное обновление
        self.update_profile_stats()


    def update_profile_stats(self):
        # Очищаем деревья
        for tree in [self.skills_tree, self.types_tree]:
            for item in tree.get_children():
                tree.delete(item)

        conn = sqlite3.connect('iom.db')
        c = conn.cursor()

        # 1. Статистика по навыкам
        c.execute('''
            SELECT н.название, COUNT(цн.цель_id) as количество
            FROM навыка н
            LEFT JOIN цель_навыки цн ON н.id = цн.навык_id
            LEFT JOIN цели ц ON цн.цель_id = ц.id AND ц.статус = 'Завершена'
            GROUP BY н.id
            HAVING количество > 0
        ''')
        skills = c.fetchall()
        for skill in skills:
            self.skills_tree.insert('', 'end', values=skill)

        # 2. Статистика по типам целей
        c.execute('''
            SELECT тип, 
                   SUM(CASE WHEN статус = 'Завершена' THEN 1 ELSE 0 END) as завершено,
                   COUNT(*) as всего
            FROM цели
            GROUP BY тип
        ''')
        types = c.fetchall()
        for type_stat in types:
            self.types_tree.insert('', 'end', values=type_stat)

        # 3. Процент целей, завершённых в срок
        c.execute("SELECT COUNT(*) FROM цели WHERE статус = 'Завершена' AND факт_дата IS NOT NULL")
        completed_total = c.fetchone()[0]

        c.execute('''
            SELECT COUNT(*) FROM цели 
            WHERE статус = 'Завершена' 
            AND факт_дата IS NOT NULL 
            AND план_дата IS NOT NULL
            AND факт_дата <= план_дата
        ''')
        timely_completed = c.fetchone()[0]

        if completed_total > 0:
            percentage = (timely_completed / completed_total) * 100
            self.timely_label.config(text=f"Процент целей, завершённых в срок: {percentage:.1f}%")
        else:
            self.timely_label.config(text="Процент целей, завершённых в срок: 0%")

        conn.close()

        def create_competencies_tab(self):
            # Заголовок
            title_frame = ttk.Frame(self.tab_competencies)
            title_frame.pack(fill='x', pady=10)
            ttk.Label(title_frame, text="Компетенции", font=("Arial", 14, "bold")).pack()

            # Фрейм для компетенций
            comp_frame = ttk.LabelFrame(self.tab_competencies, text="Компетенции и уровни")
            comp_frame.pack(fill='both', expand=True, padx=10, pady=10)

            self.competencies_tree = ttk.Treeview(comp_frame, columns=('Компетенция', 'Категория', 'Средний уровень'),
                                                  show='headings', height=10)
            self.competencies_tree.heading('Компетенция', text='Компетенция')
            self.competencies_tree.heading('Категория', text='Категория')
            self.competencies_tree.heading('Средний уровень', text='Средний уровень')
            self.competencies_tree.pack(fill='both', expand=True, padx=5, pady=5)

            # Слабые зоны
            weak_frame = ttk.LabelFrame(self.tab_competencies, text="Слабые зоны (уровень < 3)")
            weak_frame.pack(fill='both', expand=True, padx=10, pady=10)

            self.weak_zones_text = tk.Text(weak_frame, height=5, width=50)
            self.weak_zones_text.pack(fill='both', expand=True, padx=5, pady=5)

            # Рекомендации
            rec_frame = ttk.LabelFrame(self.tab_competencies, text="Рекомендации")
            rec_frame.pack(fill='both', expand=True, padx=10, pady=10)

            self.recommendations_text = tk.Text(rec_frame, height=5, width=50)
            self.recommendations_text.pack(fill='both', expand=True, padx=5, pady=5)

            # Кнопка обновления
            ttk.Button(self.tab_competencies, text="Обновить компетенции", command=self.update_competencies_stats).pack(
                pady=10)

            # Первоначальное обновление
            self.update_competencies_stats()

        def update_competencies_stats(self):
            # Очищаем дерево и текстовые поля
            for item in self.competencies_tree.get_children():
                self.competencies_tree.delete(item)

            self.weak_zones_text.delete('1.0', tk.END)
            self.recommendations_text.delete('1.0', tk.END)

            conn = sqlite3.connect('iom.db')
            c = conn.cursor()

            # Средний уровень по компетенциям
            c.execute('''
                SELECT к.название, к.категория, ROUND(AVG(цк.уровень), 1) as средний_уровень
                FROM компетенции к
                LEFT JOIN цель_компетенции цк ON к.id = цк.компетенция_id
                LEFT JOIN цели ц ON цк.цель_id = ц.id AND ц.статус = 'Завершена'
                GROUP BY к.id
            ''')
            competencies = c.fetchall()

            weak_zones = []
            recommendations = []

            for comp in competencies:
                self.competencies_tree.insert('', 'end', values=comp)

                # Проверяем слабые зоны
                if comp[2] is not None and comp[2] < 3:
                    weak_zones.append(f"{comp[0]} - {comp[2]}")

                    # Добавляем рекомендации для слабых зон
                    if comp[0] == "Презентация результатов":
                        recommendations.append(
                            "Вы почти не развиваете компетенцию 'Презентация результатов'. Рекомендуем выступить на студенческой конференции.")
                    elif comp[0] == "Работа с БД":
                        recommendations.append(
                            "Для развития компетенции 'Работа с БД' пройдите курс по SQL или поработайте над проектом с базами данных.")
                    elif comp[0] == "Управление проектами":
                        recommendations.append(
                            "Для развития 'Управления проектами' возьмите на себя роль тимлида в учебном проекте.")

            # Выводим слабые зоны
            if weak_zones:
                self.weak_zones_text.insert('1.0', '\n'.join(weak_zones))
            else:
                self.weak_zones_text.insert('1.0', "Слабых зон не обнаружено")

            # Выводим рекомендации
            if recommendations:
                self.recommendations_text.insert('1.0', '\n\n'.join(recommendations))
            else:
                self.recommendations_text.insert('1.0',
                                                 "Все компетенции развиваются хорошо. Продолжайте в том же духе!")

            conn.close()

            def create_achievements_tab(self):
                # Заголовок
                title_frame = ttk.Frame(self.tab_achievements)
                title_frame.pack(fill='x', pady=10)
                ttk.Label(title_frame, text="Достижения", font=("Arial", 14, "bold")).pack()

                # Дерево для достижений
                self.achievements_tree = ttk.Treeview(self.tab_achievements,
                                                      columns=('Получено', 'Название', 'Описание'), show='headings',
                                                      height=10)
                self.achievements_tree.heading('Получено', text='Получено')
                self.achievements_tree.heading('Название', text='Название')
                self.achievements_tree.heading('Описание', text='Описание')

                # Настраиваем колонки
                self.achievements_tree.column('Получено', width=80)
                self.achievements_tree.column('Название', width=150)
                self.achievements_tree.column('Описание', width=400)

                self.achievements_tree.pack(fill='both', expand=True, padx=10, pady=10)

                # Кнопка обновления
                ttk.Button(self.tab_achievements, text="Обновить достижения",
                           command=self.update_achievements_list).pack(pady=10)

                # Первоначальное обновление
                self.update_achievements_list()

            def update_achievements_list(self):
                # Очищаем дерево
                for item in self.achievements_tree.get_children():
                    self.achievements_tree.delete(item)

                conn = sqlite3.connect('iom.db')
                c = conn.cursor()
                c.execute("SELECT * FROM достижения ORDER BY получено DESC, название")
                achievements = c.fetchall()

                for ach in achievements:
                    status = "✓ Получено" if ach[3] == 1 else "✗ Не получено"
                    self.achievements_tree.insert('', 'end', values=(status, ach[1], ach[2]))

                conn.close()

                def create_semester_tab(self):
                    # Заголовок
                    title_frame = ttk.Frame(self.tab_semester)
                    title_frame.pack(fill='x', pady=10)
                    ttk.Label(title_frame, text="Цели на семестр", font=("Arial", 14, "bold")).pack()

                    # Фрейм для целей
                    goals_frame = ttk.LabelFrame(self.tab_semester, text="Цели семестра")
                    goals_frame.pack(fill='both', expand=True, padx=10, pady=10)

                    self.semester_tree = ttk.Treeview(goals_frame, columns=('ID', 'Цель', 'Тип', 'Прогресс'),
                                                      show='headings', height=10)
                    self.semester_tree.heading('ID', text='ID')
                    self.semester_tree.heading('Цель', text='Цель')
                    self.semester_tree.heading('Тип', text='Тип')
                    self.semester_tree.heading('Прогресс', text='Прогресс')
                    self.semester_tree.pack(fill='both', expand=True, padx=5, pady=5)

                    # Кнопки
                    btn_frame = ttk.Frame(goals_frame)
                    btn_frame.pack(fill='x', pady=5)

                    ttk.Button(btn_frame, text="Добавить цель", command=self.add_semester_goal).pack(side='left',
                                                                                                     padx=2)
                    ttk.Button(btn_frame, text="Удалить цель", command=self.delete_semester_goal).pack(side='left',
                                                                                                       padx=2)
                    ttk.Button(btn_frame, text="Обновить прогресс", command=self.update_semester_goals).pack(
                        side='left', padx=2)
                    ttk.Button(btn_frame, text="Обновить все цели", command=self.check_semester_progress).pack(
                        side='left', padx=2)

                    # Кнопка экспорта
                    ttk.Button(self.tab_semester, text="Сформировать отчёт", command=self.export_to_word).pack(pady=10)

                    # Первоначальное обновление
                    self.update_semester_goals()

                def add_semester_goal(self):
                    add_window = tk.Toplevel(self.root)
                    add_window.title("Добавить цель на семестр")

                    ttk.Label(add_window, text="Текст цели:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
                    goal_entry = ttk.Entry(add_window, width=40)
                    goal_entry.grid(row=0, column=1, padx=5, pady=5)

                    ttk.Label(add_window, text="Тип цели:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
                    type_combo = ttk.Combobox(add_window, values=['Количество', 'Повышение компетенции', 'Другое'])
                    type_combo.grid(row=1, column=1, padx=5, pady=5)

                    ttk.Label(add_window, text="Параметр (опционально):").grid(row=2, column=0, sticky='w', padx=5,
                                                                               pady=5)
                    param_entry = ttk.Entry(add_window, width=40)
                    param_entry.grid(row=2, column=1, padx=5, pady=5)

                    ttk.Label(add_window, text="Целевой прогресс:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
                    target_spinbox = ttk.Spinbox(add_window, from_=1, to=100, width=10)
                    target_spinbox.grid(row=3, column=1, padx=5, pady=5)
                    target_spinbox.set(1)

                    def save_semester_goal():
                        conn = sqlite3.connect('iom.db')
                        c = conn.cursor()
                        c.execute('''
                            INSERT INTO цель_каса (текст_цели, тип_цели, параметр, целевой_прогресс)
                            VALUES (?, ?, ?, ?)
                        ''', (goal_entry.get(), type_combo.get(), param_entry.get(), int(target_spinbox.get())))
                        conn.commit()
                        conn.close()

                        messagebox.showinfo("Успех", "Цель на семестр добавлена")
                        add_window.destroy()
                        self.update_semester_goals()

                    ttk.Button(add_window, text="Сохранить", command=save_semester_goal).grid(row=4, column=1,
                                                                                              sticky='e', padx=5,
                                                                                              pady=10)

                    def create_settings_tab(self):
                        # Заголовок
                        title_frame = ttk.Frame(self.tab_settings)
                        title_frame.pack(fill='x', pady=10)
                        ttk.Label(title_frame, text="Настройки", font=("Arial", 14, "bold")).pack()

                        # Выбор специальности
                        spec_frame = ttk.LabelFrame(self.tab_settings, text="Специальность")
                        spec_frame.pack(fill='x', padx=10, pady=10)

                        ttk.Label(spec_frame, text="Выберите специальность:").pack(anchor='w', padx=5, pady=5)

                        self.specialty_combo = ttk.Combobox(spec_frame,
                                                            values=['Информационные системы',
                                                                    'Программная инженерия',
                                                                    'Прикладная информатика',
                                                                    'Другая'])
                        self.specialty_combo.pack(fill='x', padx=5, pady=5)
                        self.specialty_combo.set('Информационные системы')

                        ttk.Button(spec_frame, text="Сохранить специальность",
                                   command=self.save_specialty).pack(pady=5)

                        # Настройки базы данных
                        db_frame = ttk.LabelFrame(self.tab_settings, text="База данных")
                        db_frame.pack(fill='x', padx=10, pady=10)

                        ttk.Label(db_frame, text="Текущая БД: SQLite (iom.db)").pack(anchor='w', padx=5, pady=5)

                        # Кнопка очистки данных (для тестирования)
                        ttk.Button(db_frame, text="Очистить все данные",
                                   command=self.clear_all_data).pack(pady=5)

                        # Информация о программе
                        info_frame = ttk.LabelFrame(self.tab_settings, text="О программе")
                        info_frame.pack(fill='x', padx=10, pady=10)

                        ttk.Label(info_frame, text="Планировщик индивидуального образовательного маршрута").pack(
                            anchor='w', padx=5, pady=2)
                        ttk.Label(info_frame, text="Версия 1.0").pack(anchor='w', padx=5, pady=2)
                        ttk.Label(info_frame, text="Работает автономно, без подключения к интернету").pack(anchor='w',
                                                                                                           padx=5,
                                                                                                           pady=2)

                    def save_specialty(self):
                        specialty = self.specialty_combo.get()
                        messagebox.showinfo("Сохранено", f"Специальность '{specialty}' сохранена")

                    def clear_all_data(self):
                        if messagebox.askyesno("Подтверждение",
                                               "Вы уверены, что хотите удалить все данные?\nЭто действие нельзя отменить."):
                            conn = sqlite3.connect('iom.db')
                            c = conn.cursor()

                            # Очищаем все таблицы
                            tables = ['цели', 'навыка', 'цель_навыки', 'компетенции',
                                      'цель_компетенции', 'цель_каса']

                            for table in tables:
                                c.execute(f"DELETE FROM {table}")

                            # Сбрасываем достижения
                            c.execute("UPDATE достижения SET получено = 0")

                            # Загружаем компетенции заново
                            if os.path.exists('competencies.json'):
                                with open('competencies.json', 'r', encoding='utf-8') as f:
                                    competencies = json.load(f)
                                    for comp in competencies:
                                        c.execute("INSERT INTO компетенции (название, категория) VALUES (?, ?)",
                                                  (comp['название'], comp['категория']))

                            conn.commit()
                            conn.close()

                            messagebox.showinfo("Очищено", "Все данные удалены")

                            # Обновляем интерфейс
                            self.refresh_goals()
                            self.update_profile_stats()
                            self.update_competencies_stats()
                            self.update_achievements_list()
                            self.update_semester_goals()

                            def update_semester_goals(self):
                                # Очищаем дерево
                                for item in self.semester_tree.get_children():
                                    self.semester_tree.delete(item)

                                conn = sqlite3.connect('iom.db')
                                c = conn.cursor()
                                c.execute(
                                    "SELECT id, текст_цели, тип_цели, текущий_прогресс, целевой_прогресс FROM цель_каса")
                                goals = c.fetchall()

                                for goal in goals:
                                    progress_text = f"{goal[3]} из {goal[4]}"
                                    self.semester_tree.insert('', 'end',
                                                              values=(goal[0], goal[1], goal[2], progress_text))

                                conn.close()

                            def delete_semester_goal(self):
                                selected = self.semester_tree.selection()
                                if not selected:
                                    messagebox.showwarning("Предупреждение", "Выберите цель для удаления")
                                    return

                                item = self.semester_tree.item(selected[0])
                                goal_id = item['values'][0]

                                if messagebox.askyesno("Подтверждение", "Удалить выбранную цель?"):
                                    conn = sqlite3.connect('iom.db')
                                    c = conn.cursor()
                                    c.execute("DELETE FROM цель_каса WHERE id = ?", (goal_id,))
                                    conn.commit()
                                    conn.close()

                                    self.update_semester_goals()

                            def check_semester_progress(self):
                                conn = sqlite3.connect('iom.db')
                                c = conn.cursor()

                                # Обновляем прогресс для целей типа "Количество"
                                c.execute('''
                                    UPDATE цель_каса 
                                    SET текущий_прогресс = (
                                        SELECT COUNT(*) 
                                        FROM цели 
                                        WHERE тип = 'Курс' 
                                        AND статус = 'Завершена'
                                    )
                                    WHERE тип_цели = 'Количество' 
                                    AND (текст_цели LIKE '%курс%' OR текст_цели LIKE '%Курс%')
                                ''')

                                conn.commit()
                                conn.close()

                                messagebox.showinfo("Обновлено", "Прогресс целей обновлён")
                                self.update_semester_goals()

                                def check_achievements(self):
                                    conn = sqlite3.connect('iom.db')
                                    c = conn.cursor()

                                    # 1. Проверка на первую цель
                                    c.execute("SELECT COUNT(*) FROM цели")
                                    goal_count = c.fetchone()[0]
                                    if goal_count >= 1:
                                        c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach1'")

                                    # 2. Пунктуальный - три или более завершённых целей в срок
                                    c.execute('''
                                        SELECT COUNT(*) FROM цели 
                                        WHERE статус = 'Завершена' 
                                        AND факт_дата IS NOT NULL 
                                        AND план_дата IS NOT NULL
                                        AND факт_дата <= план_дата
                                    ''')
                                    timely_goals = c.fetchone()[0]
                                    if timely_goals >= 3:
                                        c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach2'")

                                    # 3. Многогранный - цели минимум трёх разных типов
                                    c.execute("SELECT COUNT(DISTINCT тип) FROM цели WHERE статус = 'Завершена'")
                                    distinct_types = c.fetchone()[0]
                                    if distinct_types >= 3:
                                        c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach3'")

                                    # 4. Навыковый рост - у одного навыка четыре или более связанных завершённых целей
                                    c.execute('''
                                        SELECT н.название, COUNT(цн.цель_id) 
                                        FROM навыка н
                                        JOIN цель_навыки цн ON н.id = цн.навык_id
                                        JOIN цели ц ON цн.цель_id = ц.id AND ц.статус = 'Завершена'
                                        GROUP BY н.id
                                        HAVING COUNT(цн.цель_id) >= 4
                                    ''')
                                    if c.fetchone():
                                        c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach4'")

                                    # 5. Планирование - одновременно в статусе "В процессе" пять или более целей
                                    c.execute("SELECT COUNT(*) FROM цели WHERE статус = 'В процессе'")
                                    in_progress = c.fetchone()[0]
                                    if in_progress >= 5:
                                        c.execute("UPDATE достижения SET получено = 1 WHERE код = 'ach5'")

                                    conn.commit()
                                    conn.close()

                                    # Обновляем список достижений
                                    self.update_achievements_list()