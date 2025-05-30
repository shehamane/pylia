class Animal:
    def __init__(self, name, age: int):
        self.name: str = name
        self.age = age
        
    def voice(self):
        pass

animal = Animal('Bobik', 3)
