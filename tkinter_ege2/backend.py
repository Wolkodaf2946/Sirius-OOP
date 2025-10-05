class ExpressionModel:
    def __init__(self, expression=None):
        self.__expression = expression
        if expression:
            self.__replace_symbols()

    def set_expression(self, new_expression):
        self.__expression = new_expression
        self.__replace_symbols()

    def __replace_symbols(self):
        symbols = (("∨", " or "), ("≡", " == "), ("→", " <= "), ("∧", " and "), ("¬", "not "))
        for symbol in symbols:
            self.__expression = self.__expression.replace(symbol[0], symbol[1])

    def get_values(self):
        res = []
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    for w in range(2):
                        res.append((x, y, z, w, self._replace_params(x, y, z, w)))
        return res

    def _replace_params(self, x, y, z, w):
        expr = self.__expression
        expr = expr.replace("w", str(w))
        expr = expr.replace("z", str(z))
        expr = expr.replace("y", str(y))
        expr = expr.replace("x", str(x))

        try:
            return 1 if eval(expr) else 0
        except:
            return 0


class TruthTable:
    def __init__(self, expression_model):
        self.expression_model = expression_model
        self.rows = self._generate_rows()

    def _generate_rows(self):
        values = self.expression_model.get_values()
        rows = []
        for val in values:
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
        return 0 if count_0 <= count_1 else 1
