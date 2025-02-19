from database.db_common import create_connection
import sqlite3

def add_department(department_name, description=None, location=None):
    """Добавляет новый отдел в таблицу Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO Departments (department_name, description, location) VALUES (?, ?, ?)"
            cursor.execute(sql, (department_name, description, location))
            conn.commit()
            department_id = cursor.lastrowid
            print(f"Отдел '{department_name}' добавлен, ID: {department_id}")
            return department_id
        except sqlite3.Error as e:
            print(f"Ошибка добавления отдела '{department_name}': {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_all_departments():
    """Получает список всех отделов из таблицы Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Departments")
            departments = cursor.fetchall()
            return departments
        except sqlite3.Error as e:
            print(f"Ошибка получения списка отделов: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def get_department_by_id(department_id):
    """Получает данные отдела по его ID из таблицы Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Departments WHERE department_id = ?"
            cursor.execute(sql, (department_id,))
            department = cursor.fetchone() # Используем fetchone, так как ожидаем один результат
            return department
        except sqlite3.Error as e:
            print(f"Ошибка при получении отдела с ID {department_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_department_by_name(department_name):
    """Получает данные отдела по его имени из таблицы Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Departments WHERE department_name = ?"
            cursor.execute(sql, (department_name,))
            department = cursor.fetchone()
            return department
        except sqlite3.Error as e:
            print(f"Ошибка при получении отдела с именем {department_name}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None


def update_department(department_id, department_name=None, description=None, location=None):
    """Обновляет данные отдела в таблице Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            UPDATE Departments SET department_name = ?, description = ?, location = ?, updated_at = CURRENT_TIMESTAMP WHERE department_id = ?
            """
            cursor.execute(sql, (department_name, description, location, department_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка обновления отдела ID {department_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def delete_department(department_id):
    """Удаляет отдел из таблицы Departments."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM Departments WHERE department_id = ?"
            cursor.execute(sql, (department_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка удаления отдела ID {department_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False