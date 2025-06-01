class Animal:
    def __init__(self, name, age: int):
        self.name: str = name
        self.age = age
        self.__food_history = []
        
    def __add_food(self, food):
        self.__food_history.append(food)
        
    def eat(self, food: str):
        self.__add_food(food)
        
    def get_food_history(self):
        return self.__food_history

animal = Animal('Bobik', 3)
animal.eat('apple')
animal.eat('milk')
print(animal.get_food_history())
