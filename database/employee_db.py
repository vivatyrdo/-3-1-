from database.db_common import create_connection
import sqlite3

def add_employee(last_name, first_name, employee_code, job_title, employee_status, department_id=None): # UPDATED: Добавлен параметр department_id=None
    """
    Добавляет нового сотрудника в таблицу Employees (с department_id).
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO Employees (
                last_name, first_name, employee_code, job_title, employee_status, department_id
            ) VALUES (?, ?, ?, ?, ?, ?)  -- UPDATED: Добавлено поле department_id в VALUES
            """
            data_tuple = (
                last_name, first_name, employee_code, job_title, employee_status, department_id # UPDATED: Добавлен department_id в data_tuple
            )
            cursor.execute(sql, data_tuple)
            conn.commit()
            employee_id = cursor.lastrowid
            print(f"Сотрудник '{first_name} {last_name}' успешно добавлен с ID: {employee_id}, department_id: {department_id}") # UPDATED: Добавлено department_id в сообщение
            return employee_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении сотрудника '{first_name} {last_name}': {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_all_employees():
    """Получает список всех сотрудников из таблицы Employees."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Employees")
            employees = cursor.fetchall()
            return employees
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка сотрудников: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def get_employee_by_id(employee_id):
    """Получает данные сотрудника по его ID из таблицы Employees."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Employees WHERE employee_id = ?"
            cursor.execute(sql, (employee_id,))
            employee = cursor.fetchone() # Используем fetchone, так как ожидаем один результат
            return employee
        except sqlite3.Error as e:
            print(f"Ошибка при получении сотрудника с ID {employee_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def update_employee(employee_id, last_name=None, first_name=None, employee_code=None, job_title=None, employee_status=None, department_id=None): # UPDATED: Добавлен параметр department_id=None
    """Обновляет данные сотрудника в таблице Employees."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            UPDATE Employees SET
                last_name = ?, first_name = ?, employee_code = ?, job_title = ?, employee_status = ?, department_id = ?, updated_at = CURRENT_TIMESTAMP -- UPDATED: Добавлено поле department_id в UPDATE
            WHERE employee_id = ?
            """
            data_tuple = (
                last_name, first_name, employee_code, job_title, employee_status, department_id, employee_id # UPDATED: Добавлен department_id в data_tuple
            )
            cursor.execute(sql, data_tuple)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении сотрудника с ID {employee_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def delete_employee(employee_id):
    """Удаляет сотрудника из таблицы Employees."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            DELETE FROM Employees
            WHERE employee_id = ?
            """
            cursor.execute(sql, (employee_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении сотрудника с ID {employee_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def get_employee_distribution_by_department():
    """
    Получает данные для диаграммы распределения сотрудников по отделам.
    Возвращает список кортежей: (название_отдела, количество_сотрудников).
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            SELECT 
                Departments.department_name,
                COUNT(Employees.employee_id)
            FROM Departments
            LEFT JOIN Employees ON Departments.department_id = Employees.department_id
            GROUP BY Departments.department_name;
            """
            cursor.execute(sql)
            distribution_data = cursor.fetchall()
            return distribution_data
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных для диаграммы распределения сотрудников: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []