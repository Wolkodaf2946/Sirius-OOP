import tkinter as tk
from tkinter import ttk
from backend import TruthTable, ExpressionModel

NUM_PARTIAL_ROWS = 3
NUM_VARS = 4
NUM_COLS_TASK2 = 5


class LogicMaster:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x500")
        self.root.title("Logic Master - Таблица истинности")

        self.truthtable = None
        self.create_ui()

    def create_ui(self):
        # --основная структура--
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill='both', expand=True)

        # --поле ввода выражения--
        ttk.Label(main_frame, text="Логическое выражение:").pack(anchor='w')

        expr_frame = ttk.Frame(main_frame)
        expr_frame.pack(fill='x', pady=10)

        self.entry_expr = tk.Entry(expr_frame, font=('Arial', 12))
        self.entry_expr.pack(side='left', fill='x', expand=True, padx=(0, 10))

        ttk.Button(expr_frame, text="Построить таблицу", command=self.show_base_filter).pack(side='right')
        self.entry_expr.bind('<Return>', lambda e: self.show_base_filter())

        # --разделитель--
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        # --таблица истинности--
        table_frame = ttk.LabelFrame(main_frame, text="Таблица истинности", padding="10")
        table_frame.pack(fill='both', expand=True)

        # --кнопки управления таблицей--
        btn_frame = ttk.Frame(table_frame)
        btn_frame.pack(fill='x', pady=10)

        ttk.Button(btn_frame, text="Показать все строки", command=self.show_all).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Показать F=1", command=lambda: self.show_filtered(1)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Показать F=0", command=lambda: self.show_filtered(0)).pack(side='left', padx=5)

        # --информация о таблице--
        self.info_label = ttk.Label(btn_frame, text="")
        self.info_label.pack(side='right', padx=10)

        # --текстовая область таблицы--
        text_frame = ttk.Frame(table_frame)
        text_frame.pack(fill='both', expand=True)

        self.text_table = tk.Text(text_frame, width=50, height=20, font=('Consolas', 10))
        scrollbar_table = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_table.yview)
        self.text_table.configure(yscrollcommand=scrollbar_table.set)

        self.text_table.pack(side='left', fill='both', expand=True)
        scrollbar_table.pack(side='right', fill='y')

        # --статус бар--
        self.status_var = tk.StringVar()
        self.status_var.set("Введите логическое выражение и нажмите 'Построить таблицу'")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', padding="5")
        status_bar.pack(fill='x', pady=(10, 0))

    def _build_table(self):
        expr = self.entry_expr.get().strip()
        if not expr:
            raise ValueError("Выражение не может быть пустым.")

        self.status_var.set("Построение таблицы...")
        self.root.update()

        evaluator = ExpressionModel(expr)
        self.truthtable = TruthTable(evaluator)

        # Обновляем информацию о таблице
        total_rows = len(self.truthtable.rows)
        ones = len(self.truthtable.filter_rows(1))
        zeros = len(self.truthtable.filter_rows(0))
        self.info_label.config(text=f"Всего: {total_rows} | F=1: {ones} | F=0: {zeros}")

    def show_all(self):
        self._execute_task1_action(lambda: self.truthtable.rows, clear_before=True)
        self.status_var.set("Показаны все строки таблицы")

    def show_filtered(self, val):
        self._execute_task1_action(lambda: self.truthtable.filter_rows(val), clear_before=True)
        self.status_var.set(f"Показаны строки с F={val}")

    def show_base_filter(self, event=None):
        def filter_func():
            base_val = self.truthtable.get_base_filter()
            rows = self.truthtable.filter_rows(base_val)
            self.text_table.config(state=tk.NORMAL)
            self.text_table.insert(tk.END, f"\n--- Показаны F={base_val} (меньшее количество) ---\n")
            self.text_table.config(state=tk.DISABLED)
            return rows

        self._execute_task1_action(filter_func, append_message=False, clear_before=True)
        self.status_var.set("Показаны строки с меньшим количеством значений")

    def _execute_task1_action(self, filter_function, append_message=False, clear_before=False):
        try:
            self._build_table()
            rows = filter_function()
            self._display_rows(rows, self.text_table, append_message, clear_before)
            self.status_var.set("Таблица построена успешно")
        except Exception as e:
            self._display_error(self.text_table, str(e))
            self.status_var.set(f"Ошибка: {str(e)}")

    def _display_rows(self, rows, text_widget, append=False, clear_before=False):
        text_widget.config(state=tk.NORMAL)
        if clear_before or not append:
            text_widget.delete("1.0", tk.END)

            # Заголовок таблицы
            header = "w x y z | F\n"
            separator = "─" * 15 + "\n"
            text_widget.insert(tk.END, header)
            text_widget.insert(tk.END, separator)

        for r in rows:
            text_widget.insert(tk.END, f"{r}\n")

        text_widget.config(state=tk.DISABLED)

    def _display_error(self, text_widget, error_message):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"ОШИБКА:\n{error_message}")
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicMaster(root)
    root.mainloop()