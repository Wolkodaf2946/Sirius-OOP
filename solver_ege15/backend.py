from entity import Interval

class Solver:
    def __init__(self, expression, intervals, search_range=(0, 100), step=1.0):
        self.expression = expression
        self.intervals = {i.name: i for i in intervals} 
        self.search_range = search_range
        self.step = step

    def check_expression(self, x, a_val_bool):
        context = self.intervals.copy()

        if a_val_bool:
            context['A'] = [x] # (x in A) -> True
        else:
            context['A'] = [] # (x in A) -> False
        context['x'] = x

        try:
            return bool(eval(self.expression, {}, context))
        except Exception as e:
            raise ValueError(f"Ошибка в формуле: {e}")

    def solve(self, mode="min", target_value=True):
        points_in_a = []
        current = self.search_range[0]
        
        while current <= self.search_range[1]:
            res_without_a = self.check_expression(current, False)
            res_with_a = self.check_expression(current, True)
            
            if mode == "min":
                if res_without_a != target_value:#без А всё плохо? -> Значит, добавляем А.
                    points_in_a.append(current)
            
            elif mode == "max":
                if res_with_a == target_value: #c добавленным А всё хорошо? -> Значит, пускаем А.
                    points_in_a.append(current) 

            current += self.step
            current = round(current, 1) # предостерегаемся перед огромным кол-вом знаков после запятой

        if not points_in_a:
            return None
        
        return Interval("A (Result)", min(points_in_a), max(points_in_a))