class Interval:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    def __contains__(self, item):
        return self.start <= item <= self.end