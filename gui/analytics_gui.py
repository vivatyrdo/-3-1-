import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib
matplotlib.use('TkAgg')  # Указываем бэкенд TkAgg для matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from database import employee_db
from database import salary_db  # Импорт salary_db


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


class AnalyticsTab(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.analytics_label = tk.Label(self, text="Аналитика и Дашборд", font=("Arial", 14))
        self.analytics_label.pack(pady=10)

        # --- Добавляем кнопку "Обновить" ---
        self.refresh_button_frame = ttk.Frame(self)  # Фрейм для кнопки "Обновить"
        self.refresh_button_frame.pack(pady=5)

        self.refresh_button = ttk.Button(self.refresh_button_frame, text="Обновить аналитику",
                                          command=self.update_analytics)  # Кнопка "Обновить"
        self.refresh_button.pack(side=tk.TOP, anchor=tk.NW)  # Размещаем кнопку слева вверху фрейма
        ToolTip(self.refresh_button, "Обновить данные и перерисовать графики")  # Подсказка для кнопки
        # --- Конец блока добавления кнопки "Обновить" ---

        self.plot_frame = ttk.Frame(self)  # Фрейм для размещения графиков
        self.plot_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- Фреймы для отдельных графиков ---
        self.department_chart_frame = ttk.Frame(self.plot_frame) # Фрейм для круговой диаграммы
        self.department_chart_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5) # Размещаем слева

        self.salary_histogram_frame = ttk.Frame(self.plot_frame) # Фрейм для гистограммы
        self.salary_histogram_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5) # Размещаем справа
        # --- Конец фреймов для отдельных графиков ---


        self.create_department_distribution_chart()  # Создаем круговую диаграмму
        self.create_salary_histogram()  # --- Вызываем функцию для создания гистограммы зарплат

    def update_analytics(self):
        """Обновляет данные аналитики и перерисовывает графики."""
        # Очищаем фрейм с графиками перед обновлением
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # --- Вызываем функции для создания графиков ---
        self.create_department_distribution_chart()  # Вызываем функцию для создания круговой диаграммы
        self.create_salary_histogram()  # --- Вызываем функцию для создания гистограммы зарплат

    def create_department_distribution_chart(self):
        """Создает круговую диаграмму распределения сотрудников по отделам."""
        distribution_data = employee_db.get_employee_distribution_by_department()  # --- Получаем данные из базы

        if not distribution_data:  # Если данные не получены (например, нет отделов или ошибка)
            label = tk.Label(self.department_chart_frame, # <--- Используем department_chart_frame
                             text="Нет данных для отображения диаграммы распределения сотрудников по отделам.",
                             font=("Arial", 12))
            label.pack(padx=10, pady=10)
            return

        labels = [item[0] for item in distribution_data]  # Названия отделов для меток диаграммы
        sizes = [item[1] for item in distribution_data]  # Количество сотрудников для размеров секторов диаграммы

        fig = Figure(figsize=(5, 4), dpi=100)  # <--- Уменьшаем размер figsize для горизонтального размещения
        ax = fig.add_subplot(111)  # Добавляем область рисования

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)  # Создаем круговую диаграмму
        ax.axis('equal')  # Делаем диаграмму круглой
        ax.set_title('Распределение сотрудников по отделам', fontsize=10) # <--- Уменьшаем fontsize заголовка

        canvas = FigureCanvasTkAgg(fig, master=self.department_chart_frame)  # <--- Используем department_chart_frame
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def create_salary_histogram(self):
        """Создает гистограмму распределения зарплат сотрудников."""
        bins, hist = salary_db.get_salary_distribution()  # --- Получаем данные для гистограммы зарплат

        if hist is None:  # Если данные не получены (например, нет зарплат или ошибка)
            label = tk.Label(self.salary_histogram_frame, # <--- Используем salary_histogram_frame
                             text="Нет данных о зарплатах для отображения гистограммы.", font=("Arial", 12))
            label.pack(padx=10, pady=10)
            return

        fig = Figure(figsize=(5, 4), dpi=100) # <--- Уменьшаем размер figsize для горизонтального размещения
        ax = fig.add_subplot(111)

        # --- Строим гистограмму с помощью matplotlib ---
        ax.hist(bins[:-1], bins, weights=hist)  # bins[:-1] - центры "корзин" для x-оси, weights=hist - высоты столбцов
        ax.set_xlabel('Размер зарплаты, руб.', fontsize=8)  # <--- Уменьшаем fontsize подписей осей
        ax.set_ylabel('Количество сотрудников', fontsize=8)  # <--- Уменьшаем fontsize подписей осей
        ax.set_title('Распределение зарплат сотрудников', fontsize=10)  # <--- Уменьшаем fontsize заголовка
        ax.tick_params(axis='x', labelsize=8) # <--- Уменьшаем размер меток на оси X
        ax.tick_params(axis='y', labelsize=8) # <--- Уменьшаем размер меток на оси Y
        ax.grid(True)  # Добавляем сетку для наглядности

        canvas = FigureCanvasTkAgg(fig, master=self.salary_histogram_frame) # <--- Используем salary_histogram_frame
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)