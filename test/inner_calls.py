class A:
    def foo1(self):
        return 3
    
    def foo2(self, x):
        return 2 ** x
    
    def foo3(self, x):
        return x + 1
    
def sayhi(name):
    print(f'Hello, {name}!')
    
def getname():
    return "Abzagir"

sayhi(getname())

a = A()
print(a.foo3(a.foo2(a.foo1())))