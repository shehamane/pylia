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

animal = Animal('Bobik', 3)
cat = Cat('Murka', 4, 'black')

print(animal)
print(cat)
