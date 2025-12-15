from itertools import product, permutations

class ExpressionEvaluator:
    """
    Класс для парсинга и вычисления логического выражения.
    """
    def __init__(self, expression=None):
        self.__expression = expression
        if expression:
            self.__replace_symbols()

    def set_expression(self, new_expression):
        self.__expression = new_expression
        self.__replace_symbols()

    def __replace_symbols(self):
        # Замена символов на Python-синтаксис
        if not self.__expression: return
        
        expr = self.__expression
        
        # Словарь замен (символы ЕГЭ -> Python)
        symbols = (
            ("≡", " == "), 
            ("↔", " == "),
            ("¬", " not "), 
            ("∧", " and "), 
            ("∨", " or "), 
            ("→", " <= "),
            # Временная замена для безопасности
            ("w", "var_w"), ("x", "var_x"), ("y", "var_y"), ("z", "var_z") 
        )
        
        for s_from, s_to in symbols:
            expr = expr.replace(s_from, s_to)
            
        # Возвращаем имена переменных обратно
        expr = expr.replace("var_w", "w").replace("var_x", "x").replace("var_y", "y").replace("var_z", "z")
        self.__expression = expr

    def evaluate(self, context):
        """Вычисляет выражение с переданным словарем переменных {'x': 1, ...}"""
        try:
            return 1 if eval(self.__expression, {}, context) else 0
        except Exception:
            return 0

    def get_values(self):
        """Генерирует полную таблицу истинности (x, y, z, w, F) для Task 1"""
        res = []
        # Порядок циклов важен для стандартного вывода: x, y, z, w
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    for w in range(2):
                        val = self.evaluate({'x': x, 'y': y, 'z': z, 'w': w})
                        res.append((x, y, z, w, val))
        return res


class TruthTable:
    """Класс для хранения и фильтрации таблицы истинности (для левой панели)"""
    def __init__(self, expression_model):
        self.expression_model = expression_model
        self.raw_data = self.expression_model.get_values() 
        self.rows = self._generate_rows()

    def _generate_rows(self):
        rows = []
        for val in self.raw_data:
            row_str = f"{val[0]} {val[1]} {val[2]} {val[3]} | {val[4]}"
            rows.append(row_str)
        return rows

    def filter_rows(self, val):
        filtered = []
        for row in self.rows:
            if row.endswith(f"| {val}"):
                filtered.append(row)
        return filtered

    def get_base_filter(self):
        count_0 = len(self.filter_rows(0))
        count_1 = len(self.filter_rows(1))
        return 0 if count_0 < count_1 else 1


class EgeSolver:
    """
    Класс для решения задания №2.
    Реализует алгоритм перебора пропусков (product) и перестановок (permutations).
    """
    def __init__(self, truth_table_instance):
        # Нам нужен доступ к вычислителю выражения
        self.evaluator = truth_table_instance.expression_model

    def solve(self, partial_input):
        """
        partial_input: список списков строк [['1', '?', '0', '0', '1'], ...]
        Возвращает: (список перестановок, список заполненных строк для первой перестановки)
        """
        
        # 1. Анализ входных данных: находим координаты "дырок" (?)
        fragment_structure = [] # Здесь будут числа или None
        holes_indices = []      # Координаты (row, col) для None
        
        for r_idx, row in enumerate(partial_input):
            clean_row = []
            for c_idx, val in enumerate(row):
                if val in ('0', '1'):
                    clean_row.append(int(val))
                else:
                    clean_row.append(None) # Это пропуск
                    holes_indices.append((r_idx, c_idx))
            fragment_structure.append(clean_row)
        
        # Количество переменных (x, y, z, w) = 4 столбца
        # F - это 5-й столбец (индекс 4)
        var_names = ['x', 'y', 'z', 'w']
        
        valid_permutations = set()
        example_filled_rows = []

        # 2. Перебор всех вариантов заполнения "дырок" (как в product([0,1], repeat=5))
        n_holes = len(holes_indices)
        
        for p_vals in product([0, 1], repeat=n_holes):
            # Создаем временную таблицу t, заполняя пропуски текущими значениями p_vals
            # Делаем глубокую копию структуры, чтобы не портить оригинал для следующей итерации
            current_table = [r[:] for r in fragment_structure]
            
            # Заполняем пропуски
            for i, val in enumerate(p_vals):
                r, c = holes_indices[i]
                current_table[r][c] = val
            
            # 3. Проверка уникальности строк (как if len(t)==len(set(t)))
            # Превращаем строки в кортежи, чтобы добавить в set. Сравниваем строки целиком (включая F)
            table_as_tuples = tuple(tuple(r) for r in current_table)
            if len(set(table_as_tuples)) != len(table_as_tuples):
                continue # Строки повторяются, вариант не подходит
            
            # 4. Перебор перестановок переменных (for p in permutations('wxyz'))
            for perm in permutations(var_names):
                # perm - это текущий порядок столбцов, например ('z', 'x', 'y', 'w')
                # Это значит: 0-й столбец фрагмента -> z, 1-й -> x, и т.д.
                
                is_valid_perm = True
                
                # Проверяем каждую строку заполненной таблицы t
                for row in current_table:
                    # row: [val_col0, val_col1, val_col2, val_col3, val_F]
                    
                    # Формируем словарь аргументов для функции: {'x': ..., 'y': ...}
                    args = {}
                    for i in range(4): # Первые 4 элемента - переменные
                        var_name = perm[i]
                        val = row[i]
                        args[var_name] = val
                    
                    target_f = row[4] # Последний элемент - значение функции F
                    
                    # Вычисляем u(**dict) == r[-1]
                    if self.evaluator.evaluate(args) != target_f:
                        is_valid_perm = False
                        break
                
                if is_valid_perm:
                    perm_str = "".join(perm)
                    if perm_str not in valid_permutations:
                        valid_permutations.add(perm_str)
                        # Сохраняем пример заполненной таблицы (только первый найденный)
                        if not example_filled_rows:
                            example_filled_rows = [[str(x) for x in r] for r in current_table]

        return sorted(list(valid_permutations)), example_filled_rows