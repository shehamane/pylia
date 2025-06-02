class B:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class C(B):
    def __init__(self, a, b, c):
        self.z = c
        super().__init__(a, b)
        

b = B(1, 2)
print(b.x)
print(b.y)

c = C(1, 2, 3)
print(c.x)
print(c.y)
print(c.z)
