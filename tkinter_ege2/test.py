import tkinter as tk
from tkinter import ttk, messagebox


NUM_PARTIAL_ROWS = 3
NUM_VARS = 4
NUM_COLS_TASK2 = 5


class LogicMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("Logic Master")
        self.root.geometry("800x600")

        self.truthtable = None
        self.create_ui()

    def create_ui(self):
        """Создание простого интерфейса"""
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Ввод выражения
        ttk.Label(main_frame, text="Логическое выражение:").pack(anchor='w')

        expr_frame = ttk.Frame(main_frame)
        expr_frame.pack(fill='x', pady=5)

        self.entry_expr = tk.Entry(expr_frame, font=('Arial', 12))
        self.entry_expr.pack(side='left', fill='x', expand=True, padx=(0, 10))

        ttk.Button(expr_frame, text="Анализ", command=self.show_base_filter).pack(side='right')
        self.entry_expr.bind('<Return>', lambda e: self.show_base_filter())

        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # Две колонки
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # Левая часть - таблица истинности
        left_frame = ttk.LabelFrame(content_frame, text="Таблица истинности", padding="5")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Кнопки управления таблицей
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="Все", command=self.show_all).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="F=1", command=lambda: self.show_filtered(1)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="F=0", command=lambda: self.show_filtered(0)).pack(side='left', padx=2)

        # Текстовая область таблицы
        self.text_table = tk.Text(left_frame, width=35, height=20, font=('Consolas', 10))
        scrollbar_table = ttk.Scrollbar(left_frame, orient='vertical', command=self.text_table.yview)
        self.text_table.configure(yscrollcommand=scrollbar_table.set)

        self.text_table.pack(side='left', fill='both', expand=True)
        scrollbar_table.pack(side='right', fill='y')

        # Правая часть - решатель ЕГЭ
        right_frame = ttk.LabelFrame(content_frame, text="Решатель ЕГЭ №2", padding="5")
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Ввод частичной таблицы
        ttk.Label(right_frame, text="Частичная таблица:").pack(anchor='w')

        table_frame = ttk.Frame(right_frame)
        table_frame.pack(pady=5)

        # Заголовки переменных
        self.var_labels = []
        for j in range(NUM_VARS):
            lbl = tk.Label(table_frame, text="?", font=('Arial', 10, 'bold'), width=3)
            lbl.grid(row=0, column=j, padx=1, pady=1)
            self.var_labels.append(lbl)

        tk.Label(table_frame, text="F", font=('Arial', 10, 'bold'), width=3).grid(
            row=0, column=NUM_VARS, padx=1, pady=1)

        # Поля ввода
        self.entry_fields = []
        for i in range(NUM_PARTIAL_ROWS):
            row_entries = []
            for j in range(NUM_COLS_TASK2):
                entry = tk.Entry(table_frame, width=3, font=('Arial', 10), justify='center')
                entry.grid(row=i + 1, column=j, padx=1, pady=1)
                row_entries.append(entry)
            self.entry_fields.append(row_entries)

        # Кнопка решения
        ttk.Button(right_frame, text="Найти порядок переменных",
                   command=self.solve_ege_problem).pack(pady=10)

        # Область ответа
        ttk.Label(right_frame, text="Результат:").pack(anchor='w')

        self.text_answer = tk.Text(right_frame, height=3, font=('Arial', 11), state=tk.DISABLED)
        self.text_answer.pack(fill='x', pady=5)

        ttk.Button(right_frame, text="Копировать ответ",
                   command=self.copy_answer_task2).pack(anchor='e')

    # Методы функциональности (остаются без изменений)
    def _build_table(self):
        expr = self.entry_expr.get()
        if not expr:
            raise ValueError("Выражение не может быть пустым.")
        evaluator = ExpressionEvaluator(expr)
        self.truthtable = TruthTable(evaluator)

    def show_all(self):
        self._execute_task1_action(lambda: self.truthtable.rows, clear_before=True)

    def show_filtered(self, val):
        self._execute_task1_action(lambda: self.truthtable.filter_rows(val), clear_before=True)

    def show_base_filter(self, event=None):
        def filter_func():
            base_val = self.truthtable.get_base_filter()
            rows = self.truthtable.filter_rows(base_val)
            self.text_table.config(state=tk.NORMAL)
            self.text_table.insert(tk.END, f"\n--- Показаны F={base_val} (меньшее количество) ---\n")
            self.text_table.config(state=tk.DISABLED)
            return rows

        self._execute_task1_action(filter_func, append_message=False, clear_before=True)

    def _execute_task1_action(self, filter_function, append_message=False, clear_before=False):
        try:
            self._build_table()
            rows = filter_function()
            self._display_rows(rows, self.text_table, append_message, clear_before)
        except Exception as e:
            self._display_error(self.text_table, str(e))

    def _display_rows(self, rows, text_widget, append=False, clear_before=False):
        text_widget.config(state=tk.NORMAL)
        if clear_before or not append:
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, "w x y z | F\n")
            text_widget.insert(tk.END, "─" * 15 + "\n")

        for r in rows:
            text_widget.insert(tk.END, f"{r}\n")

        text_widget.config(state=tk.DISABLED)

    def _display_error(self, text_widget, error_message):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"ОШИБКА:\n{error_message}")
        text_widget.config(state=tk.DISABLED)
        self._update_answer_task2("ОШИБКА")

    def _get_partial_input(self):
        input_rows = []
        for row_entries in self.entry_fields:
            row_data = [entry.get().strip() for entry in row_entries]
            input_rows.append(row_data)
        return input_rows

    def _fill_partial_input(self, filled_rows: list, permutation: str):
        for i, var_name in enumerate(permutation):
            self.var_labels[i].config(text=var_name)

        for i, row in enumerate(filled_rows):
            if i < NUM_PARTIAL_ROWS:
                for j in range(NUM_VARS):
                    val = row[j]
                    self.entry_fields[i][j].delete(0, tk.END)
                    self.entry_fields[i][j].insert(0, val)

    def solve_ege_problem(self):
        self._update_answer_task2("Вычисление...")
        try:
            self._build_table()

            solver = EgeSolver(self.truthtable)
            input_data = self._get_partial_input()

            permutations_list, filled_rows = solver.solve(input_data)

            if len(permutations_list) == 1:
                answer = f"ОТВЕТ: {permutations_list[0]}"
                if filled_rows:
                    self._fill_partial_input(filled_rows, permutations_list[0])
            elif len(permutations_list) == 0:
                answer = "Решение не найдено."
            else:
                answer = f"Несколько вариантов: {', '.join(permutations_list)}"

            if len(permutations_list) != 1:
                for i in range(NUM_VARS):
                    self.var_labels[i].config(text="?")

            self._update_answer_task2(answer)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self._update_answer_task2("ОШИБКА")

    def copy_answer_task2(self):
        try:
            answer_text = self.text_answer.get("1.0", tk.END).strip()
            if "ОТВЕТ:" in answer_text:
                final_answer = answer_text.split('ОТВЕТ:')[-1].strip()
            else:
                final_answer = answer_text

            self.root.clipboard_clear()
            self.root.clipboard_append(final_answer)
            messagebox.showinfo("Успех", "Ответ скопирован в буфер обмена")
        except Exception:
            pass

    def _update_answer_task2(self, text):
        self.text_answer.config(state=tk.NORMAL)
        self.text_answer.delete("1.0", tk.END)
        self.text_answer.insert(tk.END, text)
        self.text_answer.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicMaster(root)
    root.mainloop()