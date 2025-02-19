# database/leave_request_db.py
from database.db_common import create_connection
import sqlite3

def add_leave_request(employee_id, leave_type, start_date, end_date, reason=None, status='pending', approved_by_user_id=None, notes=None):
    """Добавляет новый запрос на отпуск в таблицу LeaveRequests."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO LeaveRequests (
                employee_id, leave_type, start_date, end_date, reason, status, approved_by_user_id, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            data_tuple = (employee_id, leave_type, start_date, end_date, reason, status, approved_by_user_id, notes)
            cursor.execute(sql, data_tuple)
            conn.commit()
            leave_request_id = cursor.lastrowid
            print(f"Запрос на отпуск для сотрудника ID {employee_id} добавлен, ID запроса: {leave_request_id}")
            return leave_request_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении запроса на отпуск для сотрудника ID {employee_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_leave_request_by_id(leave_request_id):
    """Получает запрос на отпуск по ID."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM LeaveRequests WHERE leave_request_id = ?"
            cursor.execute(sql, (leave_request_id,))
            leave_request = cursor.fetchone()
            return leave_request
        except sqlite3.Error as e:
            print(f"Ошибка при получении запроса на отпуск ID {leave_request_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_leave_requests_by_employee_id(employee_id):
    """Получает все запросы на отпуск для конкретного сотрудника по employee_id."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM LeaveRequests WHERE employee_id = ?"
            cursor.execute(sql, (employee_id,))
            leave_requests = cursor.fetchall()
            return leave_requests
        except sqlite3.Error as e:
            print(f"Ошибка при получении запросов на отпуск для сотрудника ID {employee_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def get_all_leave_requests():
    """Получает список всех запросов на отпуск из таблицы LeaveRequests."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM LeaveRequests")
            leave_requests = cursor.fetchall()
            return leave_requests
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка всех запросов на отпуск: {e}")
            return []
        finally:
            if conn:
                conn.close()
    return []

def update_leave_request(leave_request_id, leave_type=None, start_date=None, end_date=None, reason=None, status=None, approved_by_user_id=None, notes=None):
    """Обновляет данные запроса на отпуск в таблице LeaveRequests."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            UPDATE LeaveRequests SET
                leave_type = ?, start_date = ?, end_date = ?, reason = ?, status = ?, approved_by_user_id = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE leave_request_id = ?
            """
            data_tuple = (leave_type, start_date, end_date, reason, status, approved_by_user_id, notes, leave_request_id)
            cursor.execute(sql, data_tuple)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении запроса на отпуск ID {leave_request_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def delete_leave_request(leave_request_id):
    """Удаляет запрос на отпуск из таблицы LeaveRequests."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM LeaveRequests WHERE leave_request_id = ?"
            cursor.execute(sql, (leave_request_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении запроса на отпуск ID {leave_request_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False