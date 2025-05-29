import os
import argparse
from compiler import Compiler

def compile_and_save(test_filename):
    input_path = os.path.join('test', test_filename)

    if not os.path.isfile(input_path):
        print(f"Ошибка: Тестовый файл не найден: {input_path}")
        return

    print(f"Компиляция файла: {test_filename}...")
    with open(input_path, 'r') as test_f:
        program = test_f.read()

    compiler = Compiler(program)
    result = compiler.compile()

    test_name = os.path.splitext(test_filename)[0]
    output_path = os.path.join('out', f'{test_name}.jl')

    os.makedirs('out', exist_ok=True)

    with open(output_path, 'w') as result_f:
        result_f.write(result)
    print(f"Результат сохранен в: {output_path}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Компилятор для тестовых файлов. Запускает все тесты или один указанный."
    )
    parser.add_argument(
        '--test',
        type=str,
        help='Имя конкретного файла из папки test для компиляции (например, my_test.txt)'
    )
    args = parser.parse_args()

    if args.test:
        compile_and_save(args.test)
    else:
        print("Запуск компиляции для всех тестов в папке 'test'...")
        test_files = os.listdir('test')
        if not test_files:
            print("Папка 'test' пуста или не найдена.")
        else:
            for test_file in test_files:
                compile_and_save(test_file)
