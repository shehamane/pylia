from abc import abstractmethod

class Employee:
    def __init__(self, name: str):
        self.__name = name
        
    @abstractmethod
    def rank(self) -> str:
        print('Not Implemented')
    
    def greeting(self) -> str:
        print('Hello, my names is' + self.__name + ', я ' + self.rank())
        
    def static_print(s: str):
        print(s)
        

class Welder(Employee):
    def __init__(self, name: str, degree: int):
        super().__init__(name)
        self.__degree = degree
        
    def rank(self) -> str:
        return 'сварщик ' + self.__degree + ' разряда'
    

class Manager(Employee):
    def __init__(self, name:str, department: str):
        super().__init__(name)
        self.__dep = department
        
    def rank(self) -> str:
        return 'начальник отдела ' + self.__dep