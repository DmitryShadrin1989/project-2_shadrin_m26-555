import shlex

import prompt

from primitive_db.constants import DB_META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

COMMANDS = {"create_table", "drop_table", "list_tables", "help", "exit"}


def print_help():
    """Выводит справку по доступным командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Запускает основной цикл программы: читает команды и выполняет их.

    На каждой итерации метаданные заново читаются из файла, а после
    create_table и drop_table сохраняются обратно.
    """
    print_help()

    while True:
        metadata = load_metadata(DB_META_FILE)

        try:
            user_input = prompt.string(">>>Введите команду: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        match args:
            case []:
                continue
            case ["create_table", table_name, *columns]:
                metadata = create_table(metadata, table_name, columns)
                save_metadata(DB_META_FILE, metadata)
            case ["drop_table", table_name]:
                metadata = drop_table(metadata, table_name)
                save_metadata(DB_META_FILE, metadata)
            case ["list_tables"]:
                list_tables(metadata)
            case ["help"]:
                print_help()
            case ["exit"]:
                break
            case [command, *_] if command in COMMANDS:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            case [command, *_]:
                print(f"Функции {command} нет. Попробуйте снова.")
