import tkinter as tk
from tkinter import ttk
import random  # Импортируем модуль random
import datetime # Импортируем модуль datetime

from gui import department_gui, employee_gui, salary_gui, analytics_gui, user_gui, leave_request_gui # <--- Добавлен импорт leave_request_gui
from database import db_common, department_db, employee_db, salary_db, user_db, leave_request_db # <--- Добавлен импорт leave_request_db

def generate_random_department():
    """Генерирует случайные данные для отдела и добавляет в базу данных."""
    department_names = ["Разработка", "Маркетинг", "Продажи", "Бухгалтерия", "HR", "Техподдержка"]
    locations = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
    descriptions = ["Основной отдел", "Вспомогательный отдел", "Новый отдел", "Старый отдел"]

    name = random.choice(department_names) + " " + str(random.randint(1, 100))
    description = random.choice(descriptions) + " " + str(random.randint(1, 5))
    location = random.choice(locations)

    department_id = department_db.add_department(name, description, location)
    if department_id:
        print(f"Случайный отдел '{name}' успешно добавлен.")
        department_list_tab.update_department_list() # Обновляем список отделов в GUI
    else:
        print(f"Не удалось добавить случайный отдел '{name}'.")

def generate_random_employee():
    """Генерирует случайные данные для сотрудника и добавляет в базу данных."""
    first_names = ["Иван", "Петр", "Сергей", "Анна", "Елена", "Ольга"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнова", "Кузнецова", "Попова"]
    job_titles = ["Менеджер", "Разработчик", "Дизайнер", "Аналитик", "Тестировщик", "Маркетолог"]
    employee_statuses = ["Активный", "В отпуске", "Уволен", "Больничный"]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    employee_code = str(random.randint(1000, 9999)) # Просто случайный код
    job_title = random.choice(job_titles)
    employee_status = random.choice(employee_statuses)

    employee_id = employee_db.add_employee(last_name, first_name, employee_code, job_title, employee_status, department_id=random.choice(department_db.get_all_departments())[0] if department_db.get_all_departments() else None) # UPDATED: Случайный отдел
    if employee_id:
        print(f"Случайный сотрудник '{first_name} {last_name}' успешно добавлен.")
        employee_list_tab.update_employee_list() # Обновляем список сотрудников в GUI
    else:
        print(f"Не удалось добавить случайного сотрудника '{first_name} {last_name}'.")

# ---  Функция для генерации случайной зарплаты ---
def generate_random_salary():
    """Генерирует случайные данные для зарплаты и добавляет в базу данных."""
    employees = employee_db.get_all_employees() # Получаем список сотрудников для выбора случайного сотрудника
    if not employees:
        print("Нет сотрудников в базе данных для начисления зарплаты.")
        return

    random_employee = random.choice(employees)
    employee_id = random_employee[0] # Берем ID случайного сотрудника
    salary_amount = round(random.uniform(30000, 150000), 2) # Случайная зарплата от 30000 до 150000, 2 знака после запятой
    # Случайная дата за последние 12 месяцев
    start_date = datetime.date.today() - datetime.timedelta(days=365)
    random_days_ago = random.randint(0, 365)
    salary_date = start_date + datetime.timedelta(days=random_days_ago)
    salary_date_str = salary_date.strftime("%Y-%m-%d") # Форматируем дату в YYYY-MM-DD для SQLite

    salary_id = salary_db.add_salary(employee_id, salary_amount, salary_date_str)
    if salary_id:
        employee_name = f"{random_employee[2]} {random_employee[1]}" # Имя Фамилия сотрудника
        print(f"Случайная зарплата в размере {salary_amount} руб. для сотрудника '{employee_name}' за {salary_date_str} успешно добавлена.")
        salary_list_tab.update_salary_list() # Обновляем список зарплат в GUI
    else:
        employee_name = f"{random_employee[2]} {random_employee[1]}"
        print(f"Не удалось добавить случайную зарплату для сотрудника '{employee_name}'.")


def main():
    root = tk.Tk()
    root.title("Управление персоналом")
    root.geometry("800x600")
    root.minsize(600, 400)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    global department_list_tab # Объявляем как глобальные, чтобы функции generate_random... могли их видеть
    global employee_list_tab
    global salary_list_tab
    global analytics_tab
    global user_list_tab
    global user_form_tab
    global leave_request_list_tab # <--- Объявляем глобальную переменную для вкладки "Отпуска"
    global leave_request_form_tab # <--- Объявляем глобальную переменную для вкладки "Добавить отпуск"


    department_list_tab = department_gui.DepartmentList(notebook)
    notebook.add(department_list_tab, text="Список отделов")

    department_form_tab = department_gui.DepartmentDetailsForm(notebook, department_list=department_list_tab)
    notebook.add(department_form_tab, text="Добавить отдел")

    employee_list_tab = employee_gui.EmployeeList(notebook)
    notebook.add(employee_list_tab, text="Список сотрудников")

    employee_form_tab = employee_gui.EmployeeDetailsForm(notebook, employee_list=employee_list_tab)
    notebook.add(employee_form_tab, text="Добавить сотрудника")

    # ---  Добавляем вкладку "Зарплаты" ---
    salary_list_tab = salary_gui.SalaryList(notebook)
    notebook.add(salary_list_tab, text="Список зарплат")

    salary_form_tab = salary_gui.SalaryDetailsForm(notebook, salary_list=salary_list_tab)
    notebook.add(salary_form_tab, text="Добавить зарплату")

    # ---  Добавляем вкладку "Аналитика" ---
    analytics_tab = analytics_gui.AnalyticsTab(notebook)
    notebook.add(analytics_tab, text="Аналитика")

    # ---  Добавляем вкладку "Пользователи" ---
    user_list_tab = user_gui.UserList(notebook)
    notebook.add(user_list_tab, text="Список пользователей")

    user_form_tab = user_gui.UserDetailsForm(notebook, user_list=user_list_tab)
    notebook.add(user_form_tab, text="Добавить пользователя")

    # ---  Добавляем вкладку "Отпуска" ---
    leave_request_list_tab = leave_request_gui.LeaveRequestList(notebook) # <--- Создаем вкладку "Список отпусков"
    notebook.add(leave_request_list_tab, text="Список отпусков") # <--- Добавляем вкладку в notebook

    leave_request_form_tab = leave_request_gui.LeaveRequestDetailsForm(notebook, leave_request_list=leave_request_list_tab) # <--- Создаем вкладку "Добавить отпуск"
    notebook.add(leave_request_form_tab, text="Добавить отпуск") # <--- Добавляем вкладку в notebook


    # --- Кнопки для добавления тестовых данных ---
    test_data_frame = ttk.Frame(root, padding=10) # Фрейм для кнопок тестовых данных
    test_data_frame.pack(pady=5)

    add_random_department_button = ttk.Button(test_data_frame, text="Добавить случайный отдел", command=generate_random_department)
    add_random_department_button.pack(side=tk.LEFT, padx=5)

    add_random_employee_button = ttk.Button(test_data_frame, text="Добавить случайного сотрудника", command=generate_random_employee)
    add_random_employee_button.pack(side=tk.LEFT, padx=5)

    # --- Кнопка для добавления случайной зарплаты ---
    add_random_salary_button = ttk.Button(test_data_frame, text="Добавить случайную зарплату", command=generate_random_salary)
    add_random_salary_button.pack(side=tk.LEFT, padx=5)

    # --- Кнопка для добавления тестового пользователя (пример) ---
    add_test_user_button = ttk.Button(test_data_frame, text="Добавить тестового пользователя", command=lambda: user_db.add_user("testuser", "password123", "employee")) # Пример добавления тестового пользователя
    add_test_user_button.pack(side=tk.LEFT, padx=5) # <--- Размещаем кнопку

    # --- Кнопка для добавления тестового запроса на отпуск (пример) ---
    add_test_leave_request_button = ttk.Button(test_data_frame, text="Добавить тестовый отпуск", command=lambda: leave_request_db.add_leave_request(employee_id=1, leave_type="Ежегодный отпуск", start_date="2024-01-15", end_date="2024-01-29", reason="Тестовый отпуск")) # Пример добавления тестового отпуска
    add_test_leave_request_button.pack(side=tk.LEFT, padx=5) # <--- Размещаем кнопку


    root.mainloop()

if __name__ == "__main__":
    db_common.create_tables()
    main()