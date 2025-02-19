from database.db_common import create_connection
import sqlite3
import numpy as np  # <--- Импортируем numpy

def add_salary(employee_id, salary_amount, salary_date):
    """Добавляет новую запись о зарплате в таблицу Salaries."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO Salaries (employee_id, salary_amount, salary_date)
            VALUES (?, ?, ?)
            """
            data_tuple = (employee_id, salary_amount, salary_date)
            cursor.execute(sql, data_tuple)
            conn.commit()
            salary_id = cursor.lastrowid
            print(f"Запись о зарплате для сотрудника ID {employee_id} добавлена, ID записи: {salary_id}")
            return salary_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи о зарплате для сотрудника ID {employee_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_salary_by_id(salary_id):
    """Получает запись о зарплате по salary_id."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Salaries WHERE salary_id = ?"
            cursor.execute(sql, (salary_id,))
            salary = cursor.fetchone()
            return salary
        except sqlite3.Error as e:
            print(f"Ошибка при получении записи о зарплате ID {salary_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_salaries_by_employee_id(employee_id):
    """Получает все записи о зарплате для конкретного сотрудника по employee_id."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Salaries WHERE employee_id = ?"
            cursor.execute(sql, (employee_id,))
            salaries = cursor.fetchall()
            return salaries
        except sqlite3.Error as e:
            print(f"Ошибка при получении записей о зарплате для сотрудника ID {employee_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def get_all_salaries():
    """Получает список всех записей о зарплатах из таблицы Salaries."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Salaries")
            salaries = cursor.fetchall()
            return salaries
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка всех записей о зарплатах: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def update_salary(salary_id, employee_id=None, salary_amount=None, salary_date=None):
    """Обновляет запись о зарплате в таблице Salaries."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            UPDATE Salaries SET
                employee_id = ?, salary_amount = ?, salary_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE salary_id = ?
            """
            data_tuple = (employee_id, salary_amount, salary_date, salary_id)
            cursor.execute(sql, data_tuple)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи о зарплате ID {salary_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def delete_salary(salary_id):
    """Удаляет запись о зарплате из таблицы Salaries."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM Salaries WHERE salary_id = ?"
            cursor.execute(sql, (salary_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении записи о зарплате ID {salary_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def get_salary_distribution(num_bins=10): # NEW: Функция для получения данных гистограммы зарплат
    """
    Получает данные для гистограммы распределения зарплат сотрудников.
    Возвращает кортеж: (bins, hist), где bins - границы "корзин", hist - высоты столбцов гистограммы.
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT salary_amount FROM Salaries") # Получаем только суммы зарплат
            salaries = cursor.fetchall()
            salary_values = [salary[0] for salary in salaries if salary[0] is not None] # Извлекаем значения зарплат из кортежей, игнорируя None

            if not salary_values: # Если нет данных о зарплатах
                return None, None

            hist, bins = np.histogram(salary_values, bins=num_bins) # Используем numpy.histogram для расчета гистограммы
            return bins, hist
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных для гистограммы зарплат: {e}")
            return None, None
        finally:
            if conn:
                conn.close()
    return None, None