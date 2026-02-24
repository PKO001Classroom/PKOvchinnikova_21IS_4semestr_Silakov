# 📚 Учебная практика 2026
## Документация проекта "Приложение для оценок"

---

### 📋 Общая информация
- **Студент:** Силаков Макисм Андреевич
- **Группа:** 21ИС-24
- **Дисциплина:** Моделирование программных продуктов
- **Учебный план:** [План (УП.01)](./План%20(УП.01).md)
- **Документация:**  [docs](./docs) 
- **Преподаватель:** Бобошко Михаил Николаевич 
- **Дата выполнения:** 19 января 2026

---

## 👥 Группа 21ИС-24

| Номер | Студент | Ник-ссылка на репозиторий |
|---------|---------|-------------|
| 1 | **Курносенко Александр Сергеевич** | [Alixandros](https://github.com/Alixandros/PKOvchinnikova_21IS_4semestr_Kyrnosenko.A.C) |
| 2 | **Ларетина Дарья Алексеевна** | [Al-Daria](https://github.com/Al-Daria/PKOvchinnikova_21IS_4semestr_Laretina) |
| 3 | **Малиневский Егор Сергеевич** | [Leendeseqy](https://github.com/Leendeseqy/PKOvchinnikova_21IS_4semestr_Malinevskiy) |
| 4 | **Микштас Артурас Мариусо** | [Mrkirk1](https://github.com/Mrkirk1/PKOvchinnikova_21IS_4semestr_Mikshtas) |
| 5 | **Мирошкин Егор Денисович** | [SWaT-137](https://github.com/SWaT-137/PKOvchinnikova_21IS_4semestr_Miroshkin) |
| 6 | **Поздняков Владимир Романович** | [Voviy-ux](https://github.com/Voviy-ux/PKOvchinnikova_21IS_PozdnyakovVR) |
| 7 | **Поздняков Дмитрий Романович** | [Mitya1606](https://github.com/Mitya1606/PKOvchinnikova_21IS_4semestr_PozdnyakovD) |
| 8 | **Полсачев Матвей Анатольевич** | [⏳В Процессе...⏳]() |
| 9 | **Рукас Вероника Олеговна** | [Burnshtein](https://github.com/Burnshtein/PKOvchinnikova_21IS_4semestr_RukasV) |
| 10 | **Силаков Максим Андреевич** | [Grozard](https://github.com/Grozard/PKOvchinnikova_21IS_4semestr_Silakov) |
| 11 | **Тараканова Андрей Андреевич** | [andreitar3](https://github.com/PKO001Classroom/PKOvchinnikova_21IS_4semestr_Tarakanov) |
| 12 | **Удин Дмитрий Максимович** | [prostoflytre](https://github.com/prostoflytre/modelup) |
| 13 | **Фисенко Анна Андреевна** | [Fisai](https://github.com/Fisai/PKOvchinikova_21IS_4semestr_FisenkoAA) |
| 14 | **Шабанов Даниил Алексеевич** | [fertak08](https://github.com/fertak08/PKOvchinnikova_21IS_4semestr_Shabanov) |
| 15 | **Юхин Лавр Юрьевич** | [PananiXX](https://github.com/PananiXX/П.К.Овчинникова_21ИС_4семестр_Юхин) |

---

## 📁 Структура репозитория
*   **[`docs/`](docs/)** — Общая проектная документация (ТЗ, требования, планы, UML).
*   **[`projects/`](projects/)** — Исходный код и документация отдельных приложений.
*   **`requirements.txt`** — Общий файл со всеми зависимостями Python.
*   **`.gitignore`** — Настроен для исключения временных и служебных файлов.
*   **`setup.bat`** — Скрипт для быстрого создания виртуального окружения и установки зависимостей.

## 🚀 Проекты

Все проекты имеют модульную структуру (`src/`), собственные тесты и README с инструкциями.

1.  **[Achievements App](projects/achievements-app/)** — Учёт личных достижений (Python, SQLite, Tkinter).
2.  **[IOM Planner](projects/iom-planner/)** — Планировщик образовательного маршрута (Python, SQLite, Tkinter).
3.  **[Knowledge Journal](projects/knowledge-journal/)** — Аналитический журнал знаний (Python, PostgreSQL, Tkinter).
4.  **[Portfolio App](projects/portfolio-app/)** — Электронное портфолио студента (Python, PostgreSQL, Tkinter).
5.  **[Research Portfolio](projects/research-portfolio/)** — Улучшенная версия портфолио (Python, PostgreSQL, Tkinter).
6.  **[Academic Tracker](projects/academic-tracker/)** — Трекер академических достижений "МойТрекер" (Python, SQLite, Tkinter).
7.  **[Grading App Work](projects/grading-app-work/)** — Локальное веб-приложение для учёта оценок (HTML/JS, localStorage)

## 📄 Общая документация

Вся проектная документация находится в папке **[`docs/`](docs/)** и структурирована по этапам:
*   **Техническое задание:** [ТЗ.md](docs/ТЗ.md)
*   **Бизнес-требования:** [Business requirements.md](docs/Business%20requirements.md)
*   **План практики:** [Plan УП.01.md](docs/Plan%20УП.01.md)
*   **Проектирование (UML):** [Диаграммы](docs/Chart.ini), [Описание](docs/Designing.md)
*   **Тест-план:** [The test plan.md](docs/The%20test%20plan.md)
*   **Приемка:** [Acceptance.md](docs/Acceptance.md)
* **Эксплуатация:** [Exploitation.md](docs/Exploitation.md)

## ⚙️ Быстрый старт

Чтобы подготовить окружение для работы с проектами, выполните в корне репозитория:

```bash
# Запустить скрипт установки (Windows)
setup.bat
