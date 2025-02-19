import tkinter as tk
from tkinter import messagebox, ttk
from database import employee_db
from database import department_db  # Импорт department_db для получения списка отделов
import datetime


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


class EmployeeDetailsForm(tk.Frame):
    def __init__(self, parent, employee_list, employee_data=None, form_window=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.employee_list = employee_list
        self.form_window = form_window

        self.employee_data = employee_data
        self.is_editing = employee_data is not None

        self.employee_id = employee_data[0] if employee_data else None
        self.last_name_var = tk.StringVar(value=employee_data[1] if employee_data else "")
        self.first_name_var = tk.StringVar(value=employee_data[2] if employee_data else "")
        self.employee_code_var = tk.StringVar(value=employee_data[3] if employee_data else "")
        self.job_title_var = tk.StringVar(value=employee_data[4] if employee_data else "")
        self.employee_status_var = tk.StringVar(value=employee_data[5] if employee_data else "")
        self.department_var = tk.StringVar()  # StringVar для хранения отдела

        form_title = "Редактирование сотрудника" if self.is_editing else "Добавить нового сотрудника"
        self.form_label = tk.Label(self, text=form_title, font=("Arial", 14))
        self.form_label.grid(row=0, column=0, columnspan=2, pady=10)

        row_num = 1

        self.last_name_label = tk.Label(self, text="Фамилия:")
        self.last_name_entry = tk.Entry(self, textvariable=self.last_name_var)
        self.last_name_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.last_name_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.last_name_entry, "Введите фамилию сотрудника")

        row_num += 1

        self.first_name_label = tk.Label(self, text="Имя:")
        self.first_name_entry = tk.Entry(self, textvariable=self.first_name_var)
        self.first_name_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.first_name_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.first_name_entry, "Введите имя сотрудника")

        row_num += 1

        self.employee_code_label = tk.Label(self, text="Код сотрудника:")
        self.employee_code_entry = tk.Entry(self, textvariable=self.employee_code_var)
        self.employee_code_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.employee_code_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.employee_code_entry, "Введите уникальный код сотрудника")

        row_num += 1

        self.job_title_label = tk.Label(self, text="Должность:")
        self.job_title_entry = tk.Entry(self, textvariable=self.job_title_var)
        self.job_title_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.job_title_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.job_title_entry, "Введите должность сотрудника")

        row_num += 1

        self.employee_status_label = tk.Label(self, text="Статус сотрудника:")
        self.employee_status_entry = ttk.Combobox(self, textvariable=self.employee_status_var,
                                                  values=['Активный', 'В отпуске', 'Уволен', 'В декретном отпуске',
                                                          'Больничный'])
        self.employee_status_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.employee_status_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.employee_status_entry, "Выберите статус сотрудника")
        row_num += 1

        # --- Добавляем поле "Отдел" ---
        self.department_label = tk.Label(self, text="Отдел:")
        self.department_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.department_combobox = ttk.Combobox(self, textvariable=self.department_var) # Combobox для выбора отдела
        self.department_combobox.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.department_combobox, "Выберите отдел сотрудника (необязательно)")
        row_num += 1
        self.update_department_combobox() # Заполняем Combobox отделами


        if self.is_editing and employee_data:  # Заполняем поля данными для редактирования
            self.last_name_var.set(employee_data[1] or "")
            self.first_name_var.set(employee_data[2] or "")
            self.employee_code_var.set(employee_data[3] or "")
            self.job_title_var.set(employee_data[4] or "")
            self.employee_status_var.set(employee_data[5] or "")
            if employee_data[6]: # Если department_id есть в данных сотрудника
                department = department_db.get_department_by_id(employee_data[6]) # Получаем данные отдела по ID
                if department:
                    self.department_var.set(department[1]) # Устанавливаем название отдела в Combobox


        button_text = "Сохранить изменения" if self.is_editing else "Сохранить"
        self.save_button = tk.Button(self, text=button_text, command=self.save_employee_details)
        self.cancel_button = tk.Button(self, text="Отмена", command=self.parent.destroy)
        ToolTip(self.save_button, "Сохранить введенные данные о сотруднике")
        ToolTip(self.cancel_button, "Отменить добавление/редактирование сотрудника и закрыть форму")

        self.save_button.grid(row=row_num, column=1, padx=5, pady=10, sticky="e")
        self.cancel_button.grid(row=row_num, column=0, padx=5, pady=10, sticky="e")

        self.grid_columnconfigure(1, weight=1)


    def update_department_combobox(self):
        """Заполняет Combobox отделами из базы данных."""
        departments = department_db.get_all_departments()
        department_names = [dept[1] for dept in departments] # Извлекаем только названия отделов
        self.department_combobox['values'] = department_names


    def save_employee_details(self):
        """Сохраняет данные сотрудника."""
        last_name = self.last_name_var.get()
        first_name = self.first_name_var.get()
        employee_code = self.employee_code_var.get()
        job_title = self.job_title_var.get()
        employee_status = self.employee_status_var.get()
        department_name = self.department_var.get() # Получаем название отдела из Combobox

        department_id = None # Изначально department_id = None
        if department_name: # Если название отдела выбрано
            department = department_db.get_department_by_name(department_name) # Ищем отдел по названию
            if department:
                department_id = department[0] # Получаем ID отдела, если отдел найден

        if not last_name or not first_name or not employee_code:
            messagebox.showerror("Ошибка",
                                 "Поля 'Фамилия', 'Имя' и 'Код сотрудника' обязательны для заполнения!")
            return

        if self.is_editing:
            updated = employee_db.update_employee(
                self.employee_id,
                last_name=last_name,
                first_name=first_name,
                employee_code=employee_code,
                job_title=job_title,
                employee_status=employee_status,
                department_id=department_id # <---  Передаем department_id в функцию обновления
            )
            if updated:
                messagebox.showinfo("Успех",
                                    f"Данные сотрудника '{first_name} {last_name}' успешно обновлены.")
            else:
                messagebox.showerror("Ошибка",
                                     f"Не удалось обновить данные сотрудника '{first_name} {last_name}'. Проверьте консоль для деталей.")

        else:
            employee_id = employee_db.add_employee(
                last_name=last_name,
                first_name=first_name,
                employee_code=employee_code,
                job_title=job_title,
                employee_status=employee_status,
                department_id=department_id # <---  Передаем department_id в функцию добавления
            )
            if employee_id:
                messagebox.showinfo("Успех",
                                    f"Сотрудник '{first_name} {last_name}' успешно добавлен с ID: {employee_id}")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить сотрудника. Проверьте консоль для деталей.")

        print(
            "DEBUG: EmployeeDetailsForm.save_employee_details - перед вызовом update_employee_list, self.employee_list:",
            self.employee_list)
        self.employee_list.update_employee_list()
        print("DEBUG: EmployeeDetailsForm.save_employee_details - после вызова update_employee_list")
        if self.form_window:
            self.form_window.withdraw()
        notebook = self.employee_list.parent
        notebook.select(self.employee_list)


class EmployeeList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.employee_list_label = tk.Label(self, text="Список сотрудников", font=("Arial", 14))
        self.employee_list_label.pack(pady=5)

        # ---  Добавляем элементы для поиска ---
        self.search_frame = ttk.Frame(self) # Фрейм для строки поиска
        self.search_frame.pack(pady=5, fill=tk.X, padx=10) # Размещаем фрейм

        self.search_label = ttk.Label(self.search_frame, text="Поиск сотрудника:") # Метка "Поиск сотрудника:"
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry_var = tk.StringVar() # StringVar для хранения текста поиска
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_entry_var) # Поле ввода для поиска
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_button = ttk.Button(self.search_frame, text="Поиск", command=self.search_employee) # Кнопка "Поиск"
        self.search_button.pack(side=tk.LEFT, padx=5)
        # ---  Конец блока добавления элементов поиска ---


        # --- UPDATED: Columns, headings и widths для разделения ФИО на Фамилию и Имя + колонка "Отдел" ---
        self.employees_tree = ttk.Treeview(self,
                                           columns=("ID", "Фамилия", "Имя", "Код сотрудника", "Должность", "Статус", "Отдел", "Действия"), # <--- Добавлена колонка "Отдел"
                                           show="headings")
        self.employees_tree.heading("ID", text="ID")
        self.employees_tree.heading("Фамилия", text="Фамилия")
        self.employees_tree.heading("Имя", text="Имя")
        self.employees_tree.heading("Код сотрудника", text="Код сотрудника")
        self.employees_tree.heading("Должность", text="Должность")
        self.employees_tree.heading("Статус", text="Статус")
        self.employees_tree.heading("Отдел", text="Отдел") # <--- Заголовок для колонки "Отдел"
        self.employees_tree.heading("Действия", text="Действия")

        self.employees_tree.column("ID", width=50)
        self.employees_tree.column("Фамилия", width=150)
        self.employees_tree.column("Имя", width=150)
        self.employees_tree.column("Код сотрудника", width=100)
        self.employees_tree.column("Должность", width=150)
        self.employees_tree.column("Статус", width=100)
        self.employees_tree.column("Отдел", width=150) # <--- Ширина для колонки "Отдел"
        self.employees_tree.column("Действия", width=100)
        # Колонка "Дата приема на работу" удалена

        self.refresh_button = tk.Button(self, text="Обновить список", command=self.update_employee_list)
        self.refresh_button.pack(pady=5,
                                 anchor=tk.NW)
        ToolTip(self.refresh_button, "Обновить список сотрудников, загрузив данные из базы данных")

        self.edit_employee_button = ttk.Button(self, text="Редактировать",
                                              command=self.open_edit_employee_form_from_button, state=tk.DISABLED)
        self.edit_employee_button.pack(pady=5, side=tk.LEFT, padx=5, anchor=tk.NW)
        ToolTip(self.edit_employee_button, "Редактировать данные выбранного сотрудника")

        self.delete_employee_button = ttk.Button(self, text="Удалить", command=self.delete_employee, state=tk.DISABLED)
        self.delete_employee_button.pack(pady=5, side=tk.LEFT, padx=5,
                                         anchor=tk.NW)
        ToolTip(self.delete_employee_button, "Удалить выбранного сотрудника из списка и базы данных")

        self.employees_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.employees = []
        self.update_employee_list()

        self.employees_tree.bind("<ButtonRelease-1>", self.on_tree_select)


    def search_employee(self):
        """Выполняет поиск сотрудников по имени, фамилии или должности."""
        search_query = self.search_entry_var.get().strip().lower()

        if not search_query:
            self.update_employee_list()
            return

        all_employees = employee_db.get_all_employees()
        filtered_employees = []

        for employee in all_employees:
            first_name = employee[2].lower() # Имя сотрудника в нижнем регистре
            last_name = employee[1].lower() # Фамилия сотрудника в нижнем регистре
            job_title = employee[4].lower() if employee[4] else "" # Должность сотрудника в нижнем регистре (если есть)

            if search_query in first_name or search_query in last_name or search_query in job_title: # Поиск по имени, фамилии и должности
                filtered_employees.append(employee)

        self.update_treeview_with_employees(filtered_employees) # Обновляем Treeview отфильтрованными сотрудниками


    def update_treeview_with_employees(self, employees): # UPDATED: Отображаем название отдела
        """Обновляет Treeview списка сотрудников заданным списком сотрудников, отображая название отдела."""
        # Очищаем таблицу перед обновлением
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)

        for employee in employees:
            employee_id = employee[0]
            department_id = employee[6] # Получаем department_id из данных сотрудника (employee[6] - department_id)
            department_name = "" # По умолчанию название отдела пустое
            if department_id: # Если department_id не None
                department = department_db.get_department_by_id(department_id) # Получаем данные отдела по ID
                if department:
                    department_name = department[1] # Берем название отдела

            self.employees_tree.insert("", tk.END, values=(
                employee_id, employee[1], employee[2], employee[3], employee[4], employee[5], department_name, "Редактировать/Удалить"), tags=( # Вставляем department_name (название отдела)
                                            str(employee_id),))

    def update_employee_list(self): # UPDATED: Теперь вызывает update_treeview_with_employees
        """Обновляет список сотрудников в Treeview."""
        print("DEBUG: EmployeeList.update_employee_list - начало")
        employees = employee_db.get_all_employees()
        self.update_treeview_with_employees(employees) # Используем новый вспомогательный метод


    def on_tree_select(self, event):
        """Обработчик выбора строки в Treeview."""
        if self.employees_tree.selection():
            self.edit_employee_button[
                'state'] = tk.NORMAL  # Включаем кнопки "Редактировать" и "Удалить" при выборе строки
            self.delete_employee_button['state'] = tk.NORMAL
        else:
            self.edit_employee_button['state'] = tk.DISABLED  # Отключаем кнопки, если строка не выбрана
            self.delete_employee_button['state'] = tk.DISABLED

    def open_add_employee_form(self):
        """Открывает форму добавления нового сотрудника."""
        add_employee_window = tk.Toplevel(self.parent)
        add_employee_window.title("Добавить нового сотрудника")
        employee_form = EmployeeDetailsForm(add_employee_window, employee_list=self, form_window=add_employee_window)
        employee_form.pack(padx=10, pady=10)

    def open_edit_employee_form_from_button(self):
        """Открывает форму редактирования для сотрудника, выбранного в Treeview (вызывается кнопкой)."""
        selected_item = self.employees_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            employee_id_tag = self.employees_tree.item(item_id, 'tags')[0]
            self.open_edit_employee_form(employee_id_tag)
        else:
            messagebox.showinfo("Информация", "Выберите сотрудника для редактирования в списке.")

    def open_edit_employee_form(self, employee_id):
        """Открывает форму редактирования для выбранного сотрудника."""
        employee_data = employee_db.get_employee_by_id(employee_id)  # Получаем данные сотрудника по ID
        if employee_data:  # Проверяем, что данные получены
            edit_employee_window = tk.Toplevel(self.parent)
            edit_employee_window.title(
                f"Редактирование сотрудника: {employee_data[2]} {employee_data[1]}")  # ФИО в заголовке окна
            employee_form = EmployeeDetailsForm(edit_employee_window, employee_list=self,
                                                employee_data=employee_data, form_window=edit_employee_window)  # Передаем form_window
            employee_form.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти данные сотрудника для редактирования.")

    def delete_employee(self):
        """Удаляет выбранного сотрудника после подтверждения."""
        selected_item = self.employees_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите сотрудника для удаления.")
            return

        item_id = selected_item[0]
        employee_id_tag = self.employees_tree.item(item_id, 'tags')[0]
        employee_name = self.employees_tree.item(item_id, 'values')[1]  # Получаем Фамилию для сообщения

        confirm_delete = messagebox.askyesno("Подтверждение удаления",
                                             f"Вы уверены, что хотите удалить сотрудника '{employee_name}'?",
                                             icon='warning')
        if confirm_delete:
            if employee_db.delete_employee(employee_id_tag):  # Удаляем из базы данных
                messagebox.showinfo("Успех", f"Сотрудник '{employee_name}' успешно удален.")
                self.update_employee_list() # <--- FIXED: Вызываем update_employee_list вместо recreate_employee_list_tab
            else:
                messagebox.showerror("Ошибка",
                                     f"Не удалось удалить сотрудника '{employee_name}'. Проверьте консоль.") # employee_name теперь фамилия