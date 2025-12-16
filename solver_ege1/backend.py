from itertools import permutations

class Solver_ege1:
    def __init__(self, vertexes, adjacencies):
        self.raw_vertexes = vertexes
        self.adjacencies = adjacencies
        self.vertexes = {c: {*w} for c, *w in vertexes.split()}

    def solve(self):
        nodes = list(self.vertexes.keys())
        n = len(nodes)
        
        indices = "".join(str(i + 1) for i in range(n))
        
        for x in permutations(nodes):
            t = self.adjacencies
            for a, b in zip(indices, x):
                t = t.replace(a, b)
            
            try:
                converted_dict = {c: {*w} for c, *w in t.split()}
                if self.vertexes == converted_dict:
                    return dict(zip(indices, x))
            except:
                continue
        return None