class B:
    def __init__(self, x, y):
        print('Init B')
        self.x = x + y
        self.y = x * y

class C(B):
    def foo(self):
        print(self.x)

b = B(7, 8)
print(b.x)
print(b.y)

c = C(7, 8)
c.foo()