# gui/user_gui.py
from database.db_common import create_connection
import tkinter as tk
from tkinter import messagebox, ttk
from database import user_db  # Импортируем user_db

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tip_window, text=self.text, background="#FFFFE0",
                          relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class UserDetailsForm(tk.Frame):
    def __init__(self, parent, user_list, user_data=None, form_window=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.user_list = user_list
        self.form_window = form_window
        self.user_data = user_data
        self.is_editing = user_data is not None

        self.user_id = user_data[0] if user_data else None
        self.username_var = tk.StringVar(value=user_data[1] if user_data else "")
        self.password_var = tk.StringVar() # Для ввода нового пароля (не для отображения существующего хеша)
        self.role_var = tk.StringVar(value=user_data[3] if user_data else "employee") # По умолчанию 'employee'

        form_title = "Редактирование пользователя" if self.is_editing else "Добавить нового пользователя"
        self.form_label = tk.Label(self, text=form_title, font=("Arial", 14))
        self.form_label.grid(row=0, column=0, columnspan=2, pady=10)

        row_num = 1

        self.username_label = tk.Label(self, text="Имя пользователя:")
        self.username_entry = tk.Entry(self, textvariable=self.username_var)
        self.username_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.username_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.username_entry, "Введите имя пользователя (логин)") # ToolTip corrected

        row_num += 1

        self.password_label = tk.Label(self, text="Пароль:") # Только для добавления нового пользователя, или смены пароля
        self.password_entry = tk.Entry(self, textvariable=self.password_var, show="*") # show="*" для скрытия пароля
        self.password_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.password_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.password_entry, "Введите пароль пользователя (только при добавлении или смене пароля)") # ToolTip corrected

        row_num += 1

        self.role_label = tk.Label(self, text="Роль:")
        self.role_combobox = ttk.Combobox(self, textvariable=self.role_var, values=['employee', 'manager', 'admin'])
        self.role_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.role_combobox.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.role_combobox, "Выберите роль пользователя") # ToolTip corrected
        row_num += 1

        button_text = "Сохранить изменения" if self.is_editing else "Добавить пользователя"
        self.save_button = tk.Button(self, text=button_text, command=self.save_user_details)
        self.cancel_button = tk.Button(self, text="Отмена", command=self.parent.destroy)
        ToolTip(self.save_button, "Сохранить данные пользователя") # ToolTip corrected
        ToolTip(self.cancel_button, "Отменить добавление/редактирование пользователя и закрыть форму") # ToolTip corrected


        self.save_button.grid(row=row_num, column=1, padx=5, pady=10, sticky="e")
        self.cancel_button.grid(row=row_num, column=0, padx=5, pady=10, sticky="e")

        self.grid_columnconfigure(1, weight=1)

    def save_user_details(self):
        """Сохраняет данные пользователя."""
        username = self.username_var.get()
        password = self.password_var.get() # Получаем пароль из поля ввода
        role = self.role_var.get()

        if not username:
            messagebox.showerror("Ошибка", "Имя пользователя обязательно!")
            return

        try:
            if self.is_editing:
                # При редактировании роли пароль обычно не меняют, но можно добавить функциональность смены пароля по желанию
                if user_db.update_user_role(self.user_id, role):
                    messagebox.showinfo("Успех", "Роль пользователя обновлена")
                else:
                    messagebox.showerror("Ошибка", "Ошибка обновления роли пользователя")
            else: # Добавление нового пользователя
                if not password: # Пароль обязателен при добавлении нового пользователя
                    messagebox.showerror("Ошибка", "Пароль обязателен при добавлении нового пользователя!")
                    return
                if user_db.add_user(username, password, role): # Передаем пароль в открытом виде, хеширование внутри user_db.py
                    messagebox.showinfo("Успех", "Пользователь добавлен")
                else:
                    messagebox.showerror("Ошибка", "Ошибка добавления пользователя")

            self.user_list.update_user_list()
            notebook = self.user_list.parent
            notebook.select(self.user_list)
            if self.form_window:
                self.form_window.withdraw()

        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла ошибка при сохранении данных пользователя: {e}")
            print(f"DEBUG: Ошибка в save_user_details: {e}")


class UserList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.user_list_label = tk.Label(self, text="Список пользователей", font=("Arial", 14))
        self.user_list_label.pack(pady=5)

        self.users_tree = ttk.Treeview(self, columns=("ID", "Имя пользователя", "Роль", "Действия"), show="headings")
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Имя пользователя", text="Имя пользователя")
        self.users_tree.heading("Роль", text="Роль")
        self.users_tree.heading("Действия", text="Действия")

        self.users_tree.column("ID", width=50)
        self.users_tree.column("Имя пользователя", width=200)
        self.users_tree.column("Роль", width=100)
        self.users_tree.column("Действия", width=100)

        self.refresh_button = tk.Button(self, text="Обновить список", command=self.update_user_list)
        self.refresh_button.pack(pady=5)
        ToolTip(self.refresh_button, "Обновить список пользователей") # ToolTip corrected

        self.edit_user_button = ttk.Button(self, text="Редактировать роль", command=self.open_edit_form_from_button, state=tk.DISABLED) # Кнопка "Редактировать роль"
        self.edit_user_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.edit_user_button, "Редактировать роль выбранного пользователя") # ToolTip corrected


        self.delete_user_button = ttk.Button(self, text="Удалить пользователя", command=self.delete_user, state=tk.DISABLED)
        self.delete_user_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.delete_user_button, "Удалить выбранного пользователя") # ToolTip corrected

        self.users_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.users = []
        self.update_user_list()

        self.users_tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def update_treeview_with_users(self, users):
        """Обновляет Treeview списка пользователей заданным списком пользователей."""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        for user in users:
            self.users_tree.insert("", tk.END, values=(
                user[0], user[1], user[3], "Редактировать/Удалить"), tags=(str(user[0]),))

    def update_user_list(self):
        """Обновляет список пользователей в Treeview."""
        conn = create_connection() # Получаем соединение для прямого запроса, если get_all_users нет в user_db.py
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users")
                users = cursor.fetchall()
                self.update_treeview_with_users(users)
            except sqlite3.Error as e:
                print(f"Ошибка при получении списка пользователей: {e}")
            finally:
                conn.close()
        else:
            print("Не удалось установить соединение с базой данных.")


    def on_tree_select(self, event):
        if self.users_tree.selection():
            self.edit_user_button['state'] = tk.NORMAL
            self.delete_user_button['state'] = tk.NORMAL
        else:
            self.edit_user_button['state'] = tk.DISABLED
            self.delete_user_button['state'] = tk.DISABLED

        selected_item = self.users_tree.selection()
        if selected_item:
            user_id_tag = self.users_tree.item(selected_item[0], 'tags')[0]
            user_data = user_db.get_user_by_id(user_id_tag)
            if user_data and user_data[3] == 'admin': # Example: Disable delete for admin user
                self.delete_user_button['state'] = tk.DISABLED # Disable delete button for admin


    def open_add_user_form(self):
        add_user_window = tk.Toplevel(self.parent)
        add_user_window.title("Добавить нового пользователя")
        user_form = UserDetailsForm(add_user_window, user_list=self, form_window=add_user_window)
        user_form.pack(padx=10, pady=10)

    def open_edit_form_from_button(self):
        selected_item = self.users_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            user_id_tag = self.users_tree.item(item_id, 'tags')[0]
            self.open_edit_form(user_id_tag)
        else:
            messagebox.showinfo("Информация", "Выберите пользователя для редактирования.")

    def open_edit_form(self, user_id_tag):
        user_data = user_db.get_user_by_id(user_id_tag) # Получаем данные пользователя по ID
        if user_data:
            edit_window = tk.Toplevel(self.parent)
            edit_window.title(f"Редактирование пользователя: {user_data[1]}") # Используем username в заголовке
            detail_form = UserDetailsForm(edit_window, user_list=self, user_data=user_data, form_window=edit_window)
            detail_form.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти данные пользователя для редактирования.")

    def delete_user(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите пользователя для удаления.")
            return

        item_id = selected_item[0]
        user_id_tag = self.users_tree.item(item_id, 'tags')[0]
        username = self.users_tree.item(item_id, 'values')[1] # Получаем username для сообщения

        if int(user_id_tag) == 1: # Защита от случайного удаления первого пользователя (например, admin) - опционально
            messagebox.showerror("Ошибка", "Нельзя удалить первого пользователя (ID 1).") # Можно убрать или изменить логику
            return

        confirm_delete = messagebox.askyesno("Подтверждение удаления",
                                            f"Вы уверены, что хотите удалить пользователя '{username}'?",
                                            icon='warning')
        if confirm_delete:
            if user_db.delete_user(user_id_tag):
                messagebox.showinfo("Успех", f"Пользователь '{username}' удален.")
                self.update_user_list()
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя '{username}'.")