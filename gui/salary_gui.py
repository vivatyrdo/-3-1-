import tkinter as tk
from tkinter import messagebox, ttk
from database import salary_db
from database import employee_db

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

class SalaryDetailsForm(tk.Frame):
    def __init__(self, parent, salary_list, salary_data=None, form_window=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.salary_list = salary_list
        self.form_window = form_window
        self.salary_data = salary_data
        self.is_editing = salary_data is not None

        self.salary_id = salary_data[0] if salary_data else None
        self.employee_id_var = tk.IntVar(value=salary_data[1] if salary_data else "")
        self.salary_amount_var = tk.DoubleVar(value=salary_data[2] if salary_data else "")
        self.salary_date_var = tk.StringVar(value=salary_data[3] if salary_data else "")

        form_title = "Редактирование зарплаты" if self.is_editing else "Добавить запись о зарплате"
        self.form_label = tk.Label(self, text=form_title, font=("Arial", 14))
        self.form_label.grid(row=0, column=0, columnspan=2, pady=10)

        row_num = 1

        self.employee_id_label = tk.Label(self, text="ID сотрудника:")
        self.employee_id_entry = tk.Entry(self, textvariable=self.employee_id_var)
        self.employee_id_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.employee_id_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.employee_id_entry, "Введите ID сотрудника")
        row_num += 1

        self.salary_amount_label = tk.Label(self, text="Сумма зарплаты:")
        self.salary_amount_entry = tk.Entry(self, textvariable=self.salary_amount_var)
        self.salary_amount_entry.config(validate="key")
        self.salary_amount_entry['validatecommand'] = (self.register(self.validate_amount_input), '%P')
        self.salary_amount_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.salary_amount_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.salary_amount_entry, "Введите сумму зарплаты (число)")
        row_num += 1

        self.salary_date_label = tk.Label(self, text="Дата выплаты (YYYY-MM-DD):")
        self.salary_date_entry = tk.Entry(self, textvariable=self.salary_date_var)
        self.salary_date_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.salary_date_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.salary_date_entry, "Введите дату выплаты зарплаты в формате YYYY-MM-DD")
        row_num += 1

        button_text = "Сохранить изменения" if self.is_editing else "Добавить зарплату"
        self.save_button = tk.Button(self, text=button_text, command=self.save_salary_details)
        self.cancel_button = tk.Button(self, text="Отмена", command=self.parent.destroy)

        self.save_button.grid(row=row_num, column=1, padx=5, pady=10, sticky="e")
        self.cancel_button.grid(row=row_num, column=0, padx=5, pady=10, sticky="e")

        self.grid_columnconfigure(1, weight=1)

    def validate_amount_input(self, value):
        """Валидация ввода суммы зарплаты - только цифры и точка."""
        if not value:
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False


    def save_salary_details(self):
        """Сохраняет данные о зарплате."""
        employee_id = self.employee_id_var.get()
        salary_amount = self.salary_amount_var.get()
        salary_date = self.salary_date_var.get()

        if not employee_id or not salary_amount or not salary_date:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            employee_id = int(employee_id)
            salary_amount = float(salary_amount)
            # Здесь можно добавить валидацию формата даты, но пока опустим для простоты

            if self.is_editing:
                if salary_db.update_salary(self.salary_id, employee_id, salary_amount, salary_date):
                    messagebox.showinfo("Успех", "Данные о зарплате обновлены")
                else:
                    messagebox.showerror("Ошибка", "Ошибка обновления данных о зарплате")
            else:
                if salary_db.add_salary(employee_id, salary_amount, salary_date):
                    messagebox.showinfo("Успех", "Запись о зарплате добавлена")
                else:
                    messagebox.showerror("Ошибка", "Ошибка добавления записи о зарплате")

            self.salary_list.update_salary_list()
            notebook = self.salary_list.parent
            notebook.select(self.salary_list)
            if self.form_window:
                self.form_window.withdraw()

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат данных. Проверьте ID сотрудника и сумму зарплаты.")
        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла ошибка при сохранении данных о зарплате: {e}")
            print(f"DEBUG: Ошибка в save_salary_details: {e}")


class SalaryList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.salary_list_label = tk.Label(self, text="Список зарплат", font=("Arial", 14))
        self.salary_list_label.pack(pady=5)

        # ---  Добавляем элементы для поиска ---
        self.search_frame = ttk.Frame(self) # Фрейм для строки поиска
        self.search_frame.pack(pady=5, fill=tk.X, padx=10) # Размещаем фрейм

        self.search_label = ttk.Label(self.search_frame, text="Поиск сотрудника:") # Метка "Поиск сотрудника:"
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry_var = tk.StringVar() # StringVar для хранения текста поиска
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_entry_var) # Поле ввода для поиска
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_button = ttk.Button(self.search_frame, text="Поиск", command=self.search_salary) # Кнопка "Поиск"
        self.search_button.pack(side=tk.LEFT, padx=5)
        # ---  Конец блока добавления элементов поиска ---


        self.salaries_tree = ttk.Treeview(self, columns=("ID", "Сотрудник", "Сумма", "Дата выплаты", "Действия"), show="headings") # UPDATED: Заголовок колонки "Сотрудник ID" изменен на "Сотрудник"
        self.salaries_tree.heading("ID", text="ID")
        self.salaries_tree.heading("Сотрудник", text="Сотрудник") # UPDATED: Заголовок колонки "Сотрудник ID" изменен на "Сотрудник"
        self.salaries_tree.heading("Сумма", text="Сумма")
        self.salaries_tree.heading("Дата выплаты", text="Дата выплаты")
        self.salaries_tree.heading("Действия", text="Действия")

        self.salaries_tree.column("ID", width=50)
        self.salaries_tree.column("Сотрудник", width=200) # UPDATED: Увеличена ширина колонки "Сотрудник"
        self.salaries_tree.column("Сумма", width=100)
        self.salaries_tree.column("Дата выплаты", width=120)
        self.salaries_tree.column("Действия", width=100)

        self.refresh_button = tk.Button(self, text="Обновить список", command=self.update_salary_list)
        self.refresh_button.pack(pady=5)

        self.edit_salary_button = ttk.Button(self, text="Редактировать", command=self.open_edit_form_from_button, state=tk.DISABLED) # Используем ttk.Button вместо tk.Button для единообразия
        self.edit_salary_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.delete_salary_button = ttk.Button(self, text="Удалить", command=self.delete_salary, state=tk.DISABLED) # Используем ttk.Button
        self.delete_salary_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.salaries_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.salaries = []
        self.update_salary_list()

        self.salaries_tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def update_treeview_with_salaries(self, salaries): # NEW: Вспомогательный метод для обновления Treeview
        """Обновляет Treeview списка зарплат заданным списком зарплат."""
        for item in self.salaries_tree.get_children():
            self.salaries_tree.delete(item) # Очищаем Treeview

        for salary in salaries:
            employee_id = salary[1]
            employee_data = employee_db.get_employee_by_id(employee_id)
            if employee_data:
                employee_name = f"{employee_data[2]} {employee_data[1]}"
            else:
                employee_name = f"Сотрудник не найден (ID: {employee_id})"

            self.salaries_tree.insert("", tk.END, values=(
                salary[0], employee_name, salary[2], salary[3], "Редактировать/Удалить"), tags=(str(salary[0]),))


    def search_salary(self):
        """Выполняет поиск записей о зарплате по имени сотрудника."""
        search_query = self.search_entry_var.get().strip().lower() # Получаем текст поиска и приводим к нижнему регистру

        if not search_query: # Если поле поиска пустое, показываем все зарплаты
            self.update_salary_list()
            return

        all_salaries = salary_db.get_all_salaries() # Получаем все записи о зарплатах
        filtered_salaries = []

        for salary in all_salaries:
            employee_id = salary[1]
            employee_data = employee_db.get_employee_by_id(employee_id)
            if employee_data:
                employee_name = f"{employee_data[2]} {employee_data[1]}".lower() # ФИО сотрудника в нижнем регистре
                if search_query in employee_name: # Проверяем, содержится ли текст поиска в имени сотрудника
                    filtered_salaries.append(salary) # Если содержится, добавляем зарплату в отфильтрованный список

        self.update_treeview_with_salaries(filtered_salaries) # Обновляем Treeview отфильтрованными зарплатами


    def update_salary_list(self): # UPDATED: Теперь вызывает update_treeview_with_salaries
        """Обновляет список зарплат в Treeview, отображая имя сотрудника."""
        salaries = salary_db.get_all_salaries()
        self.update_treeview_with_salaries(salaries) # Используем новый вспомогательный метод


    def on_tree_select(self, event):
        if self.salaries_tree.selection():
            self.edit_salary_button['state'] = tk.NORMAL
            self.delete_salary_button['state'] = tk.NORMAL
        else:
            self.edit_salary_button['state'] = tk.DISABLED
            self.delete_salary_button['state'] = tk.DISABLED

    def open_add_salary_form(self):
        add_salary_window = tk.Toplevel(self.parent)
        add_salary_window.title("Добавить запись о зарплате")
        salary_form = SalaryDetailsForm(add_salary_window, salary_list=self, form_window=add_salary_window)
        salary_form.pack(padx=10, pady=10)

    def open_edit_form_from_button(self):
        selected_item = self.salaries_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            salary_id_tag = self.salaries_tree.item(item_id, 'tags')[0]
            self.open_edit_form(salary_id_tag)
        else:
            messagebox.showinfo("Информация", "Выберите запись о зарплате для редактирования.")

    def open_edit_form(self, salary_id_tag):
        salary_data = None
        for sal in self.salaries:
            if str(sal[0]) == salary_id_tag:
                salary_data = sal
                break
        if salary_data:
            edit_window = tk.Toplevel(self.parent)
            edit_window.title(f"Редактирование записи о зарплате ID: {salary_data[0]}")
            detail_form = SalaryDetailsForm(edit_window, salary_list=self, salary_data=salary_data, form_window=edit_window)
            detail_form.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти данные о зарплате для редактирования.")

    def delete_salary(self):
        selected_item = self.salaries_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите запись о зарплате для удаления.")
            return

        item_id = selected_item[0]
        salary_id_tag = self.salaries_tree.item(item_id, 'tags')[0]

        confirm_delete = messagebox.askyesno("Подтверждение удаления",
                                            f"Вы уверены, что хотите удалить запись о зарплате ID {salary_id_tag}?",
                                            icon='warning')
        if confirm_delete:
            if salary_db.delete_salary(salary_id_tag):
                messagebox.showinfo("Успех", f"Запись о зарплате ID {salary_id_tag} удалена.")
                self.update_salary_list()
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить запись о зарплате ID {salary_id_tag}.")