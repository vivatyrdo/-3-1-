# gui/leave_request_gui.py
from database.db_common import create_connection
import tkinter as tk
from tkinter import messagebox, ttk
from database import leave_request_db
from database import employee_db  # Для получения имен сотрудников

class ToolTip: # Скопируйте класс ToolTip, если его еще нет в этом файле
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

class LeaveRequestDetailsForm(tk.Frame):
    def __init__(self, parent, leave_request_list, leave_request_data=None, form_window=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.leave_request_list = leave_request_list
        self.form_window = form_window
        self.leave_request_data = leave_request_data
        self.is_editing = leave_request_data is not None

        self.leave_request_id = leave_request_data[0] if leave_request_data else None
        self.employee_id_var = tk.IntVar(value=leave_request_data[1] if leave_request_data else "")
        self.leave_type_var = tk.StringVar(value=leave_request_data[2] if leave_request_data else "")
        self.start_date_var = tk.StringVar(value=leave_request_data[3] if leave_request_data else "")
        self.end_date_var = tk.StringVar(value=leave_request_data[4] if leave_request_data else "")
        self.reason_var = tk.StringVar(value=leave_request_data[5] if leave_request_data else "")

        form_title = "Редактирование запроса на отпуск" if self.is_editing else "Добавить запрос на отпуск"
        self.form_label = tk.Label(self, text=form_title, font=("Arial", 14))
        self.form_label.grid(row=0, column=0, columnspan=2, pady=10)

        row_num = 1

        self.employee_id_label = tk.Label(self, text="ID сотрудника:")
        self.employee_id_entry = tk.Entry(self, textvariable=self.employee_id_var)
        self.employee_id_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.employee_id_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.employee_id_entry, "Введите ID сотрудника")
        row_num += 1

        self.leave_type_label = tk.Label(self, text="Тип отпуска:")
        self.leave_type_combobox = ttk.Combobox(self, textvariable=self.leave_type_var, values=['Ежегодный отпуск', 'Больничный', 'Отпуск за свой счет', 'Отгул', 'Декретный отпуск', 'Учебный отпуск'])
        self.leave_type_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.leave_type_combobox.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.leave_type_combobox, "Выберите тип отпуска")
        row_num += 1

        self.start_date_label = tk.Label(self, text="Дата начала (YYYY-MM-DD):")
        self.start_date_entry = tk.Entry(self, textvariable=self.start_date_var)
        self.start_date_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.start_date_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.start_date_entry, "Введите дату начала отпуска в формате YYYY-MM-DD")
        row_num += 1

        self.end_date_label = tk.Label(self, text="Дата окончания (YYYY-MM-DD):")
        self.end_date_entry = tk.Entry(self, textvariable=self.end_date_var)
        self.end_date_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.end_date_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.end_date_entry, "Введите дату окончания отпуска в формате YYYY-MM-DD")
        row_num += 1

        self.reason_label = tk.Label(self, text="Причина:")
        self.reason_entry = tk.Entry(self, textvariable=self.reason_var)
        self.reason_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.reason_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.reason_entry, "Введите причину отпуска (необязательно)")
        row_num += 1

        button_text = "Сохранить изменения" if self.is_editing else "Добавить запрос"
        self.save_button = tk.Button(self, text=button_text, command=self.save_leave_request_details)
        self.cancel_button = tk.Button(self, text="Отмена", command=self.parent.destroy)
        ToolTip(self.save_button, "Сохранить данные запроса на отпуск")
        ToolTip(self.cancel_button, "Отменить добавление/редактирование запроса и закрыть форму")

        self.save_button.grid(row=row_num, column=1, padx=5, pady=10, sticky="e")
        self.cancel_button.grid(row=row_num, column=0, padx=5, pady=10, sticky="e")

        self.grid_columnconfigure(1, weight=1)

    def save_leave_request_details(self):
        """Сохраняет данные запроса на отпуск."""
        employee_id = self.employee_id_var.get()
        leave_type = self.leave_type_var.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        reason = self.reason_var.get()

        if not employee_id or not leave_type or not start_date or not end_date:
            messagebox.showerror("Ошибка", "Все поля, кроме 'Причины', обязательны для заполнения!")
            return

        try:
            employee_id = int(employee_id)
            # Here you can add date format validation if needed

            if self.is_editing:
                if leave_request_db.update_leave_request(self.leave_request_id, leave_type, start_date, end_date, reason):
                    messagebox.showinfo("Успех", "Запрос на отпуск обновлен")
                else:
                    messagebox.showerror("Ошибка", "Ошибка обновления запроса на отпуск")
            else:
                if leave_request_db.add_leave_request(employee_id, leave_type, start_date, end_date, reason):
                    messagebox.showinfo("Успех", "Запрос на отпуск добавлен")
                else:
                    messagebox.showerror("Ошибка", "Ошибка добавления запроса на отпуск")

            self.leave_request_list.update_leave_request_list()
            notebook = self.leave_request_list.parent
            notebook.select(self.leave_request_list)
            if self.form_window:
                self.form_window.withdraw()

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат данных. Проверьте ID сотрудника и даты.")
        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла ошибка при сохранении запроса на отпуск: {e}")
            print(f"DEBUG: Ошибка в save_leave_request_details: {e}")


class LeaveRequestList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.leave_request_list_label = tk.Label(self, text="Список запросов на отпуск", font=("Arial", 14))
        self.leave_request_list_label.pack(pady=5)

        self.leave_requests_tree = ttk.Treeview(self, columns=("ID", "Сотрудник", "Тип отпуска", "Дата начала", "Дата окончания", "Статус", "Действия"), show="headings")
        self.leave_requests_tree.heading("ID", text="ID")
        self.leave_requests_tree.heading("Сотрудник", text="Сотрудник")
        self.leave_requests_tree.heading("Тип отпуска", text="Тип отпуска")
        self.leave_requests_tree.heading("Дата начала", text="Дата начала")
        self.leave_requests_tree.heading("Дата окончания", text="Дата окончания")
        self.leave_requests_tree.heading("Статус", text="Статус")
        self.leave_requests_tree.heading("Действия", text="Действия")

        self.leave_requests_tree.column("ID", width=50)
        self.leave_requests_tree.column("Сотрудник", width=150)
        self.leave_requests_tree.column("Тип отпуска", width=120)
        self.leave_requests_tree.column("Дата начала", width=100)
        self.leave_requests_tree.column("Дата окончания", width=100)
        self.leave_requests_tree.column("Статус", width=100)
        self.leave_requests_tree.column("Действия", width=100)

        self.refresh_button = tk.Button(self, text="Обновить список", command=self.update_leave_request_list)
        self.refresh_button.pack(pady=5)
        ToolTip(self.refresh_button, "Обновить список запросов на отпуск")

        self.edit_leave_request_button = ttk.Button(self, text="Редактировать", command=self.open_edit_form_from_button, state=tk.DISABLED)
        self.edit_leave_request_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.edit_leave_request_button, "Редактировать выбранный запрос на отпуск")

        self.delete_leave_request_button = ttk.Button(self, text="Удалить", command=self.delete_leave_request, state=tk.DISABLED)
        self.delete_leave_request_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.delete_leave_request_button, "Удалить выбранный запрос на отпуск")

        self.leave_requests_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.leave_requests = []
        self.update_leave_request_list()

        self.leave_requests_tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def update_treeview_with_leave_requests(self, leave_requests):
        """Обновляет Treeview списка запросов на отпуск."""
        for item in self.leave_requests_tree.get_children():
            self.leave_requests_tree.delete(item)

        for request in leave_requests:
            employee_id = request[1]
            employee_data = employee_db.get_employee_by_id(employee_id)
            employee_name = f"{employee_data[2]} {employee_data[1]}" if employee_data else f"Сотрудник ID: {employee_id} не найден" # Имя или ID, если не найден

            self.leave_requests_tree.insert("", tk.END, values=(
                request[0], employee_name, request[2], request[3], request[4], request[6], "Редактировать/Удалить"), tags=(str(request[0]),))

    def update_leave_request_list(self):
        """Обновляет список запросов на отпуск в Treeview."""
        leave_requests = leave_request_db.get_all_leave_requests()
        self.update_treeview_with_leave_requests(leave_requests)

    def on_tree_select(self, event):
        if self.leave_requests_tree.selection():
            self.edit_leave_request_button['state'] = tk.NORMAL
            self.delete_leave_request_button['state'] = tk.NORMAL
        else:
            self.edit_leave_request_button['state'] = tk.DISABLED
            self.delete_leave_request_button['state'] = tk.DISABLED

    def open_add_leave_request_form(self):
        add_leave_request_window = tk.Toplevel(self.parent)
        add_leave_request_window.title("Добавить запрос на отпуск")
        leave_request_form = LeaveRequestDetailsForm(add_leave_request_window, leave_request_list=self, form_window=add_leave_request_window)
        leave_request_form.pack(padx=10, pady=10)

    def open_edit_form_from_button(self):
        selected_item = self.leave_requests_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            leave_request_id_tag = self.leave_requests_tree.item(item_id, 'tags')[0]
            self.open_edit_form(leave_request_id_tag)
        else:
            messagebox.showinfo("Информация", "Выберите запрос на отпуск для редактирования.")

    def open_edit_form(self, leave_request_id_tag):
        leave_request_data = leave_request_db.get_leave_request_by_id(leave_request_id_tag)
        if leave_request_data:
            edit_window = tk.Toplevel(self.parent)
            edit_window.title(f"Редактирование запроса на отпуск ID: {leave_request_data[0]}")
            detail_form = LeaveRequestDetailsForm(edit_window, leave_request_list=self, leave_request_data=leave_request_data, form_window=edit_window)
            detail_form.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти данные запроса на отпуск для редактирования.")

    def delete_leave_request(self):
        selected_item = self.leave_requests_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите запрос на отпуск для удаления.")
            return

        item_id = selected_item[0]
        leave_request_id_tag = self.leave_requests_tree.item(item_id, 'tags')[0]

        confirm_delete = messagebox.askyesno("Подтверждение удаления",
                                            f"Вы уверены, что хотите удалить запрос на отпуск ID {leave_request_id_tag}?",
                                            icon='warning')
        if confirm_delete:
            if leave_request_db.delete_leave_request(leave_request_id_tag):
                messagebox.showinfo("Успех", f"Запрос на отпуск ID {leave_request_id_tag} удален.")
                self.update_leave_request_list()
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить запрос на отпуск ID {leave_request_id_tag}.")