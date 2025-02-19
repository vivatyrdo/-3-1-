import tkinter as tk
from tkinter import messagebox, ttk
from database import department_db  # !!! Изменен импорт на department_db

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
        self.tip_window.wm_overrideredirect(True)  # Убираем рамку окна подсказки
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tip_window, text=self.text, background="#FFFFE0",
                          relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class DepartmentDetailsForm(tk.Frame):
    def __init__(self, parent, department_list, department_data=None, form_window=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.department_list = department_list
        self.form_window = form_window # Сохраняем ссылку на Toplevel окно

        self.department_data = department_data
        self.is_editing = department_data is not None

        self.department_id = department_data[0] if department_data else None
        self.department_name_var = tk.StringVar(value=department_data[1] if department_data else "")
        self.description_var = tk.StringVar(value=department_data[2] if department_data and department_data[2] else "")
        self.location_var = tk.StringVar(value=department_data[3] if department_data and department_data[3] else "")

        form_title = "Редактирование отдела" if self.is_editing else "Добавить новый отдел"
        self.form_label = tk.Label(self, text=form_title, font=("Arial", 14))
        self.form_label.grid(row=0, column=0, columnspan=2, pady=10)

        row_num = 1
        button_text = "Сохранить изменения" if self.is_editing else "Добавить отдел"

        self.department_name_label = tk.Label(self, text="Название отдела:")
        self.department_name_entry = tk.Entry(self, textvariable=self.department_name_var)
        self.department_name_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.department_name_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.department_name_entry, "Введите название отдела")
        row_num += 1

        self.description_label = tk.Label(self, text="Описание:")
        self.description_entry = tk.Entry(self, textvariable=self.description_var)
        self.description_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.description_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.description_entry, "Введите описание отдела (необязательно)")
        row_num += 1

        self.location_label = tk.Label(self, text="Местоположение:")
        self.location_entry = tk.Entry(self, textvariable=self.location_var)
        self.location_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        self.location_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.location_entry, "Введите местоположение отдела (необязательно)")
        row_num += 1

        self.save_button = tk.Button(self, text=button_text, command=self.save_department_details)
        self.cancel_button = tk.Button(self, text="Отмена", command=self.parent.destroy)
        ToolTip(self.save_button, "Сохранить данные отдела")
        ToolTip(self.cancel_button, "Отменить добавление/редактирование отдела и закрыть форму")

        self.save_button.grid(row=row_num, column=1, padx=5, pady=10, sticky="e")
        self.cancel_button.grid(row=row_num, column=0, padx=5, pady=10, sticky="e")

        self.grid_columnconfigure(1, weight=1)

    def save_department_details(self):
        """Сохраняет данные отдела."""
        department_name = self.department_name_var.get()
        description = self.description_var.get()
        location = self.location_var.get()

        if not department_name:
            messagebox.showerror("Ошибка", "Название отдела обязательно!")
            return

        try:
            if self.is_editing:
                if department_db.update_department(self.department_id, department_name, description, location):
                    messagebox.showinfo("Успех", "Отдел обновлен")
                else:
                    messagebox.showerror("Ошибка", "Ошибка обновления отдела")
            else:
                if department_db.add_department(department_name, description, location):
                    messagebox.showinfo("Успех", "Отдел добавлен")
                else:
                    messagebox.showerror("Ошибка", "Ошибка добавления отдела")

            self.department_list.update_department_list()

            # --- Код для переключения на вкладку "Список отделов" ---
            notebook = self.department_list.parent # Получаем notebook через department_list.parent
            notebook.select(self.department_list) # Выбираем вкладку department_list (она же "Список отделов")

            if self.form_window: # Проверка на всякий случай
                self.form_window.withdraw() # Используем self.form_window для withdraw

        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла ошибка при сохранении отдела: {e}")
            print(f"DEBUG: Ошибка в save_department_details: {e}")


class DepartmentList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.department_list_label = tk.Label(self, text="Список отделов", font=("Arial", 14))
        self.department_list_label.pack(pady=5)

        # ---  Добавляем элементы для поиска ---
        self.search_frame = ttk.Frame(self) # Фрейм для строки поиска
        self.search_frame.pack(pady=5, fill=tk.X, padx=10) # Размещаем фрейм

        self.search_label = ttk.Label(self.search_frame, text="Поиск отдела:") # Метка "Поиск отдела:"
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry_var = tk.StringVar() # StringVar для хранения текста поиска
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_entry_var) # Поле ввода для поиска
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.search_button = ttk.Button(self.search_frame, text="Поиск", command=self.search_department) # Кнопка "Поиск"
        self.search_button.pack(side=tk.LEFT, padx=5)
        # ---  Конец блока добавления элементов поиска ---


        self.departments_tree = ttk.Treeview(self, columns=("ID", "Название", "Описание", "Местоположение", "Действия"), show="headings")
        self.departments_tree.heading("ID", text="ID")
        self.departments_tree.heading("Название", text="Название отдела")
        self.departments_tree.heading("Описание", text="Описание")
        self.departments_tree.heading("Местоположение", text="Местоположение")
        self.departments_tree.heading("Действия", text="Действия")

        self.departments_tree.column("ID", width=50)
        self.departments_tree.column("Название", width=150)
        self.departments_tree.column("Описание", width=200)
        self.departments_tree.column("Местоположение", width=100)
        self.departments_tree.column("Действия", width=100)

        self.refresh_button = tk.Button(self, text="Обновить список", command=self.update_department_list)
        self.refresh_button.pack(pady=5)
        ToolTip(self.refresh_button, "Обновить список отделов")

        self.edit_department_button = tk.Button(self, text="Редактировать отдел", command=self.open_edit_form_from_button, state=tk.DISABLED)
        self.edit_department_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.edit_department_button, "Редактировать выбранный отдел")

        self.delete_department_button = tk.Button(self, text="Удалить отдел", command=self.delete_department, state=tk.DISABLED)
        self.delete_department_button.pack(pady=5, side=tk.LEFT, padx=5)
        ToolTip(self.delete_department_button, "Удалить выбранный отдел")

        self.departments_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.departments = []
        self.update_department_list()

        self.departments_tree.bind("<ButtonRelease-1>", self.on_tree_select)


    def search_department(self):
        """Выполняет поиск отделов по названию или местоположению."""
        search_query = self.search_entry_var.get().strip().lower()

        if not search_query:
            self.update_department_list()
            return

        all_departments = department_db.get_all_departments()
        filtered_departments = []

        for department in all_departments:
            department_name = department[1].lower() # Название отдела в нижнем регистре
            department_location = department[3].lower() if department[3] else "" # Местоположение отдела в нижнем регистре (если есть)
            if search_query in department_name or search_query in department_location: # Поиск по названию и местоположению
                filtered_departments.append(department)

        self.update_treeview_with_departments(filtered_departments) # Обновляем Treeview отфильтрованными отделами


    def update_treeview_with_departments(self, departments): # NEW: Вспомогательный метод
        """Обновляет Treeview списка отделов заданным списком отделов."""
        for item in self.departments_tree.get_children():
            self.departments_tree.delete(item)

        for department in departments:
            department_id = department[0]
            self.departments_tree.insert("", tk.END, values=department[:4] + ("Редактировать", "Удалить"), tags=(str(department_id),))


    def update_department_list(self): # UPDATED: Теперь вызывает update_treeview_with_departments
        """Обновляет список отделов в Treeview."""
        departments = department_db.get_all_departments()
        self.update_treeview_with_departments(departments) # Используем новый вспомогательный метод


    def on_tree_select(self, event):
        """Обработчик выбора строки в Treeview."""
        if self.departments_tree.selection():
            self.edit_department_button['state'] = tk.NORMAL
            self.delete_department_button['state'] = tk.NORMAL
        else:
            self.edit_department_button['state'] = tk.DISABLED
            self.delete_department_button['state'] = tk.DISABLED

    def open_add_department_form(self):
        """Открывает форму добавления нового отдела."""
        add_department_window = tk.Toplevel(self.parent)
        add_department_window.title("Добавить новый отдел")
        department_form = DepartmentDetailsForm(add_department_window, department_list=self, form_window=add_department_window) # Передаем add_department_window
        department_form.pack(padx=10, pady=10)

    def open_edit_form_from_button(self):
        """Открывает форму редактирования для отдела, выбранного в Treeview (вызывается кнопкой)."""
        selected_item = self.departments_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            department_id_tag = self.departments_tree.item(item_id, 'tags')[0]
            self.open_edit_form(department_id_tag)
        else:
            messagebox.showinfo("Информация", "Выберите отдел для редактирования в списке.")

    def open_edit_form(self, department_id_tag):
        """Открывает форму редактирования для выбранного отдела."""
        department_data = None
        for dept in self.departments:
            if str(dept[0]) == department_id_tag:
                department_data = dept
                break
        if department_data:
            edit_window = tk.Toplevel(self.parent)
            edit_window.title(f"Редактирование отдела: {department_data[1]}")
            detail_form = DepartmentDetailsForm(edit_window, department_list=self, department_data=department_data, form_window=edit_window) # Передаем edit_window
            detail_form.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти данные отдела для редактирования.")

    def delete_department(self):
        """Удаляет выбранный отдел после подтверждения пользователя."""
        selected_item = self.departments_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите отдел для удаления в списке.")
            return

        item_id = selected_item[0]
        department_id_tag = self.departments_tree.item(item_id, 'tags')[0]
        department_name = self.departments_tree.item(item_id, 'values')[1]

        confirm_delete = messagebox.askyesno("Подтверждение удаления",
                                            f"Вы уверены, что хотите удалить отдел '{department_name}'?",
                                            icon='warning')
        if confirm_delete:
            if department_db.delete_department(department_id_tag):
                messagebox.showinfo("Успех", f"Отдел '{department_name}' успешно удален.")
                self.update_department_list() # Обновляем список отделов через update_department_list
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить отдел '{department_name}'. Проверьте консоль.")

    def recreate_department_list_tab(self):
        """Пересоздает вкладку "Список отделов"."""
        notebook = self.parent.master
        department_list_tab_index = notebook.index(self)
        department_list_tab_text = notebook.tab(department_list_tab_index, "text")

        self.destroy()
        new_department_list = DepartmentList(notebook)
        notebook.insert(department_list_tab_index, new_department_list, text=department_list_tab_text)