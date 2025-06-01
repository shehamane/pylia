#!/bin/bash

if [ -z "$1" ]; then
    echo "Использование: $0 <папка>"
    echo "Запускает все .py файлы в указанной папке"
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "Ошибка: папка '$1' не существует"
    exit 1
fi

cd "$1" || exit 1

for script in *.py; do
    if [ -f "$script" ]; then
        echo "──────────────────────────────────"
        echo "Запуск скрипта: $script"
        python3 "$script"
        echo "Статус завершения: $?"
        echo
    else
        echo "В папке нет .py файлов"
        exit 0
    fi
done