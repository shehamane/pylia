class A:
    def __init__(self):
        self.x = 1

    def bad_style(self):
        self.y = 2


v = A()
print(v.x)
v.bad_style()
print(v.y)
v.z = 3
print(v.z)