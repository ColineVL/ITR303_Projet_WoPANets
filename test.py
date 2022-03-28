class Planet:
    def __init__(self, name, number):
        self.name = name
        self.number = number


x = [Planet("truc", 1), Planet("machin", 1), Planet("bidule", 3)]

get_indexes = lambda name, number, xs: [
    i for (y, i) in zip(xs, range(len(xs))) if (name == y.name) and (number == y.number)
]
print(get_indexes("truc", 1, x))
