import os
from compiler import Compiler

if __name__ == '__main__':
    for test in os.listdir('test'):
        with open(f'test/{test}', 'r') as test_f:
            program = test_f.read()
        compiler = Compiler(program)
        result = compiler.compile()

        test_name = test.split('.')[0]
        with open(f'out/{test_name}.jl', 'w') as result_f:
            result_f.write(result)

