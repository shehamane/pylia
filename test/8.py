class Animal:
    def __init__(self, name):
        self.name: str = name
        self.age = None
    
    def __init__(self, name, age: int):
        self.name: str = name
        self.age = age
        
    def voice(self):
        pass
    
class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color
        
    def __init__(self, name, color):
        super(Animal).__init__(name)
        self.color = color
        
    def voice(self):
        print('meow')
        
class Kitty(Cat):
    def __init__(self, name, age):
        super(Animal).__init__(name, age)
        self.color = None

animal = Animal('Bobik', 3)
cat = Cat('Murka', 'black')
kitty = Kitty('Murzik', 1)

print(animal)
print(cat)
print(kitty)