class Animal:
    def __init__(self, name, age: int):
        self.name: str = name
        self.age = age
        
    def voice(self):
        pass
    
class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color
        
    def voice(self):
        print('meow')
        
class Kitty(Cat):
    def __init__(self, name, age):
        super().__init__(name, age, None)

animal = Animal('Bobik', 3)
cat = Cat('Murka', 5, 'black')
kitty = Kitty('Murzik', 1)

for c in [cat, kitty]:
    print('=====CAT=====')
    print(c.name)
    print(c.age)
    print(c.color)