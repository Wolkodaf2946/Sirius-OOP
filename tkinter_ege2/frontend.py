import tkinter as tk
from tkinter import ttk, messagebox

# Импорт логики из соседнего файла
from backend import ExpressionEvaluator, TruthTable, EgeSolver

# Константы интерфейса
NUM_PARTIAL_ROWS = 3
NUM_VARS = 4
NUM_COLS_TASK2 = 5

class LogicMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("Logic Master: ЕГЭ Информатика")
        self.root.geometry("850x650") # Чуть увеличил высоту

        self.truthtable = None
        self.create_ui()

    def create_ui(self):
        """Создание интерфейса"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # --- Ввод выражения ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(top_frame, text="Логическое выражение:").pack(anchor='w')
        ttk.Label(top_frame, text="(используйте w, x, y, z и знаки ≡, →, ∨, ∧, ¬)", font=("Arial", 8), foreground="gray").pack(anchor='w')

        expr_frame = ttk.Frame(top_frame)
        expr_frame.pack(fill='x', pady=5)

        self.entry_expr = tk.Entry(expr_frame, font=('Consolas', 12))
        self.entry_expr.pack(side='left', fill='x', expand=True, padx=(0, 10))

        ttk.Button(expr_frame, text="Построить таблицу", command=self.show_base_filter).pack(side='right')
        self.entry_expr.bind('<Return>', lambda e: self.show_base_filter())

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=5)

        # --- Основной контент (две колонки) ---
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # ЛЕВАЯ ЧАСТЬ - Таблица истинности
        left_frame = ttk.LabelFrame(content_frame, text="Таблица истинности", padding="5")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Все строки", command=self.show_all).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Только F=1", command=lambda: self.show_filtered(1)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Только F=0", command=lambda: self.show_filtered(0)).pack(side='left', padx=2)

        self.text_table = tk.Text(left_frame, width=30, height=20, font=('Consolas', 11))
        scrollbar_table = ttk.Scrollbar(left_frame, orient='vertical', command=self.text_table.yview)
        self.text_table.configure(yscrollcommand=scrollbar_table.set)
        self.text_table.pack(side='left', fill='both', expand=True)
        scrollbar_table.pack(side='right', fill='y')

        # ПРАВАЯ ЧАСТЬ - Решатель
        right_frame = ttk.LabelFrame(content_frame, text="Solver", padding="5")
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="Введите фрагмент таблицы:", font=('Arial', 9)).pack(pady=(5,2))
        ttk.Label(right_frame, text="(оставьте пустым или '?' для пропуска)", font=('Arial', 8), foreground="gray").pack(pady=(0,5))

        table_frame = ttk.Frame(right_frame)
        table_frame.pack(pady=5)

        # Заголовки переменных (динамические)
        self.var_labels = []
        for j in range(NUM_VARS):
            lbl = tk.Label(table_frame, text="?", font=('Arial', 10, 'bold'), width=3, bg="#ddd")
            lbl.grid(row=0, column=j, padx=2, pady=2)
            self.var_labels.append(lbl)

        tk.Label(table_frame, text="F", font=('Arial', 10, 'bold'), width=3, bg="#ddd").grid(row=0, column=NUM_VARS, padx=2, pady=2)

        # Поля ввода (сетка)
        self.entry_fields = []
        for i in range(NUM_PARTIAL_ROWS):
            row_entries = []
            for j in range(NUM_COLS_TASK2):
                entry = tk.Entry(table_frame, width=4, font=('Arial', 11), justify='center')
                entry.grid(row=i + 1, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.entry_fields.append(row_entries)

        # КНОПКИ УПРАВЛЕНИЯ РЕШАТЕЛЕМ
        solver_btns_frame = ttk.Frame(right_frame)
        solver_btns_frame.pack(pady=15)

        ttk.Button(solver_btns_frame, text="Найти переменные", command=self.solve_ege_problem).pack(side='left', padx=5)
        ttk.Button(solver_btns_frame, text="Очистить", command=self.clear_task2_table).pack(side='left', padx=5)

        ttk.Label(right_frame, text="Ответ:").pack(anchor='w')
        self.text_answer = tk.Text(right_frame, height=4, font=('Arial', 12, 'bold'), state=tk.DISABLED, bg="#f0f0f0")
        self.text_answer.pack(fill='x', pady=5)
        
        ttk.Button(right_frame, text="Копировать ответ", command=self.copy_answer_task2).pack(anchor='e')

    # --- Логика взаимодействия ---

    def _build_table(self):
        expr = self.entry_expr.get()
        if not expr:
            raise ValueError("Выражение пустое!")
        # Создаем объекты бэкенда
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
            self.text_table.insert(tk.END, f"\n--- ФИЛЬТР F={base_val} (меньше строк) ---\n")
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
            # Внимание: Бэкенд генерирует данные в порядке циклов x, y, z, w
            text_widget.insert(tk.END, "x y z w | F\n") 
            text_widget.insert(tk.END, "─" * 15 + "\n")

        for r in rows:
            text_widget.insert(tk.END, f"{r}\n")

        text_widget.config(state=tk.DISABLED)

    def _display_error(self, text_widget, error_message):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"ОШИБКА:\n{error_message}")
        text_widget.config(state=tk.DISABLED)

    def _get_partial_input(self):
        input_rows = []
        for row_entries in self.entry_fields:
            # Получаем значения, заменяем пустые на '?'
            row_data = [entry.get().strip() if entry.get().strip() != "" else "?" for entry in row_entries]
            # Проверяем, не пустая ли вся строка
            if all(x == '?' for x in row_data):
                continue
            input_rows.append(row_data)
        return input_rows

    def _fill_partial_input(self, filled_rows: list, permutation: str):
        # Обновляем заголовки
        for i, var_name in enumerate(permutation):
            self.var_labels[i].config(text=var_name, fg="blue")

        # Заполняем поля значениями (восстанавливаем пропущенные)
        if filled_rows:
            for i, row in enumerate(filled_rows):
                if i < len(self.entry_fields):
                    for j in range(NUM_VARS): # Заполняем только переменные
                        current_val = self.entry_fields[i][j].get().strip()
                        new_val = row[j]
                        if current_val == "" or current_val == "?":
                            self.entry_fields[i][j].delete(0, tk.END)
                            self.entry_fields[i][j].insert(0, new_val)
                            self.entry_fields[i][j].config(fg="green")

    def clear_task2_table(self):
        """Очистка таблицы решателя и сброс состояния"""
        # Сброс заголовков
        for lbl in self.var_labels:
            lbl.config(text="?", fg="black", bg="#ddd")
        
        # Очистка полей ввода
        for row in self.entry_fields:
            for entry in row:
                entry.delete(0, tk.END)
                entry.config(fg="black") # Сброс цвета текста (если был зеленым)
        
        # Очистка ответа
        self._update_answer_task2("")

    def solve_ege_problem(self):
        self._update_answer_task2("Вычисление...")
        # Сброс визуальных стилей перед решением
        for lbl in self.var_labels: lbl.config(text="?", fg="black")
        for row in self.entry_fields:
            for entry in row: entry.config(fg="black")

        try:
            self._build_table() # Сначала строим таблицу (Task 1 логика)
            
            solver = EgeSolver(self.truthtable) # Передаем таблицу в решатель (Task 2 логика)
            input_data = self._get_partial_input()
            
            if not input_data:
                self._update_answer_task2("Пустая таблица!")
                return

            permutations_list, filled_rows = solver.solve(input_data)

            if len(permutations_list) == 1:
                answer = f"{permutations_list[0]}"
                self._update_answer_task2(f"ОТВЕТ: {answer}")
                self._fill_partial_input(filled_rows, permutations_list[0])
            elif len(permutations_list) == 0:
                self._update_answer_task2("Решений нет.")
            else:
                self._update_answer_task2(f"Найдено {len(permutations_list)} вариантов:\n" + ", ".join(permutations_list))

        except Exception as e:
            self._update_answer_task2(f"ОШИБКА: {e}")

    def copy_answer_task2(self):
        try:
            answer_text = self.text_answer.get("1.0", tk.END).strip()
            if "ОТВЕТ:" in answer_text:
                final_answer = answer_text.split('ОТВЕТ:')[-1].strip()
            else:
                final_answer = answer_text
            
            self.root.clipboard_clear()
            self.root.clipboard_append(final_answer)
            messagebox.showinfo("Успех", "Ответ скопирован!")
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