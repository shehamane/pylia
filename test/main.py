class Employee:
    def __init__(self, name: str):
        self.__name = name
        
    def rank(self):
        print('Not Implemented')
    
    def greeting(self):
        print(str('Hello, my names is', self.__name, ', I am ', self.rank()))
        

class Welder(Employee):
    def __init__(self, name: str, degree: int):
        super().__init__(name)
        self.__degree = degree
        
    def rank(self) -> str:
        return str('welder of ', self.__degree, ' degree')
    

class Manager(Employee):
    def __init__(self, name:str, department: str):
        super().__init__(name)
        self.__dep = department
        
    def rank(self) -> str:
        return str('boss of ', self.__dep)
    
employee = Employee('Bob')

welder = Welder('Charles', 3)
welder.greeting()

manager = Manager('Alice', 'economics')
manager.greeting()