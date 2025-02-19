import sqlite3
import os

DATABASE_DIR = 'database'  # Папка, где будет база данных
DATABASE_NAME = os.path.join(DATABASE_DIR, 'hrm_database.db') # Полный путь к файлу БД

def create_connection():
    """
    Создает соединение с базой данных SQLite.
    Если файл базы данных не существует, он будет создан.
    """
    conn = None
    try:
        # Ensure the database directory exists
        os.makedirs(DATABASE_DIR, exist_ok=True) # Create directory if it doesn't exist
        conn = sqlite3.connect(DATABASE_NAME)
        print(f"Успешное подключение к базе данных SQLite: {DATABASE_NAME}")
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return conn

def create_tables():
    """
    Создает таблицы в базе данных, если они еще не существуют.
    Здесь определены таблицы: Departments, Positions, Employees, Salaries, Users, LeaveRequests.
    """
    conn = create_connection() # Получаем соединение с базой данных
    if conn is not None:
        try:
            cursor = conn.cursor()

            # SQL запрос для создания таблицы Departments
            create_departments_table_sql = """
            CREATE TABLE IF NOT EXISTS Departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Первичный ключ, автоинкремент
                department_name VARCHAR(100) UNIQUE NOT NULL, -- Название отдела, уникальное, не null
                description TEXT,                             -- Описание отдела
                location VARCHAR(100),                          -- Местоположение
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата создания, по умолчанию текущая
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата обновления, по умолчанию текущая
            );
            """

            # SQL запрос для создания таблицы Positions
            create_positions_table_sql = """
            CREATE TABLE IF NOT EXISTS Positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_name VARCHAR(100) UNIQUE NOT NULL,
                job_description TEXT,
                department_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES Departments (department_id)
            );
            """

            # ---  ОБНОВЛЕННЫЙ SQL запрос для создания таблицы Employees с department_id и внешним ключом ---
            create_employees_table_sql = """
            CREATE TABLE IF NOT EXISTS Employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name VARCHAR(50) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                employee_code VARCHAR(20) UNIQUE NOT NULL,
                job_title VARCHAR(100),
                employee_status VARCHAR(50),
                department_id INTEGER,  -- <--- ДОБАВЛЕНО поле department_id
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES Departments (department_id) -- <--- ДОБАВЛЕН внешний ключ
            );
            """

            # SQL запрос для создания таблицы Salaries
            create_salaries_table_sql = """
            CREATE TABLE IF NOT EXISTS Salaries (
                salary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                salary_amount REAL NOT NULL,
                salary_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees (employee_id)
            );
            """

            # --- SQL запрос для создания таблицы Users ---
            create_users_table_sql = """
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,  -- Храним хеш пароля, не сам пароль!
                role VARCHAR(50) DEFAULT 'employee', -- Роль пользователя (например, 'admin', 'manager', 'employee')
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            # --- SQL запрос для создания таблицы LeaveRequests ---
            create_leave_requests_table_sql = """
            CREATE TABLE IF NOT EXISTS LeaveRequests (
                leave_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                leave_type VARCHAR(50) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                approval_date TIMESTAMP,
                approved_by_user_id INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees (employee_id),
                FOREIGN KEY (approved_by_user_id) REFERENCES Users (user_id)
            );
            """


            table_creation_sql_commands = [
                create_departments_table_sql,
                create_positions_table_sql,
                create_employees_table_sql,
                create_salaries_table_sql,
                create_users_table_sql,
                create_leave_requests_table_sql, # <--- Добавляем команду создания таблицы LeaveRequests
                # Здесь можно добавить SQL запросы для создания других таблиц (Payroll, Training, etc.)
            ]

            for sql_command in table_creation_sql_commands:
                cursor.execute(sql_command)

            conn.commit()
            print("Таблицы успешно созданы или обновлены (если их не было).")

        except sqlite3.Error as e:
            print(f"Ошибка при создании или обновлении таблиц: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("Не удалось установить соединение с базой данных, создание/обновление таблиц отменено.")

if __name__ == '__main__':
    create_tables() # Example of how to run create_tables directly
    print("Проверка: Таблицы базы данных должны быть созданы (или уже существовали).")