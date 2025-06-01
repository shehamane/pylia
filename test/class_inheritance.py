class Animal:
    def __init__(self, name, age: int):
        self.name: str = name
        self.age: int = age
        
    def voice(self):
        pass
    
class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.age = age
        self.color = color
        
    def voice(self):
        print('meow')

animal = Animal('Bobik', 3)
murka = Cat('Murka', 3, 'black')
murzik = Cat('Murzik', 2, 'ginger')

print(murka.age)
print(murka.color)
print(murzik.age)
print(murzik.name)
