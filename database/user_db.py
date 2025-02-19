# database/user_db.py
from database.db_common import create_connection
import sqlite3
# import bcrypt # <--- Импортируем bcrypt для хеширования паролей (если используете bcrypt)
# import hashlib # <--- Или hashlib, если используете hashlib

def add_user(username, password, role='employee'): # Пароль принимаем в открытом виде, хешируем внутри функции
    """Добавляет нового пользователя в таблицу Users."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # --- Хеширование пароля ---
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # Пример с bcrypt
            # hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() # Пример с hashlib (SHA256 - менее безопасно для паролей, чем bcrypt/ Argon2)
            hashed_password = hash_password(password) # <--- Используем функцию hash_password (определим ниже)

            sql = """
            INSERT INTO Users (username, password_hash, role)
            VALUES (?, ?, ?)
            """
            data_tuple = (username, hashed_password, role)
            cursor.execute(sql, data_tuple)
            conn.commit()
            user_id = cursor.lastrowid
            print(f"Пользователь '{username}' успешно добавлен с ID: {user_id}")
            return user_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении пользователя '{username}': {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_user_by_username(username):
    """Получает данные пользователя по имени пользователя (username)."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Users WHERE username = ?"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            return user
        except sqlite3.Error as e:
            print(f"Ошибка при получении пользователя с именем '{username}': {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def get_user_by_id(user_id):
    """Получает данные пользователя по ID."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM Users WHERE user_id = ?"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            return user
        except sqlite3.Error as e:
            print(f"Ошибка при получении пользователя с ID {user_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return None

def update_user_role(user_id, role):
    """Обновляет роль пользователя."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = """
            UPDATE Users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
            """
            cursor.execute(sql, (role, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении роли пользователя ID {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def delete_user(user_id):
    """Удаляет пользователя по ID."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM Users WHERE user_id = ?"
            cursor.execute(sql, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении пользователя ID {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    return False

def verify_password(password, hashed_password): # Функция для проверки пароля
    """Проверяет, соответствует ли введенный пароль хешированному паролю."""
    # return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) # Пример с bcrypt
    # return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed_password # Пример с hashlib (SHA256)
    return hash_password(password, salt=hashed_password) == hashed_password # <--- Используем функцию hash_password для проверки

def hash_password(password, salt=None): # Функция для хеширования пароля
    """Хеширует пароль с использованием bcrypt (рекомендуется) или hashlib (менее безопасно)."""
    import bcrypt # <--- Импортируем bcrypt ВНУТРИ функции, чтобы не делать его обязательной зависимостью, если пока не нужен GUI для пользователей
    if salt is None:
        salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8') # Возвращаем хеш как строку
    # --- Альтернатива с hashlib (менее безопасно для паролей) ---
    # import hashlib
    # hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # return hashed_password