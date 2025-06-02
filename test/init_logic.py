class WithArray:
    def __init__(self, x, y):
        if x <= 0:
            self.x = -x
        else:
            self.x = x
        self.array = []
        for i in range(y):
            self.array.append(None)
        while y > 0:
            y -= 1
            self.array[y] = y * y


wa = WithArray(-7, 15)
print(wa.x)
print(wa.array[7])
