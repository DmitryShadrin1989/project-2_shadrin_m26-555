import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import DB_META_FILE, ID_COLUMN
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
    validate_clause,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import parse_delete, parse_insert, parse_select, parse_update
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

COMMANDS = {
    "create_table",
    "drop_table",
    "list_tables",
    "insert",
    "select",
    "update",
    "delete",
    "info",
    "help",
    "exit",
}


def print_help():
    """Выводит справку по доступным командам."""
    print("\n***Операции с таблицами***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print('Строковые значения указываются в кавычках, например "Sergei".')

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _print_records(columns, records):
    """Выводит записи в виде таблицы PrettyTable."""
    if not records:
        print("Записи не найдены.")
        return

    table = PrettyTable(list(columns))
    for record in records:
        table.add_row([record.get(column) for column in columns])
    print(table)


def _matching_ids(table_data, where_clause):
    """Возвращает ID записей, подходящих под условие."""
    return [record[ID_COLUMN] for record in select(table_data, where_clause)]


@handle_db_errors
def _handle_insert(metadata, user_input):
    """Выполняет команду insert into ... values (...)."""
    table_name, values = parse_insert(user_input)
    table_data = insert(metadata, table_name, values, load_table_data(table_name))
    if table_data is not None:
        save_table_data(table_name, table_data)


@handle_db_errors
def _handle_select(metadata, user_input):
    """Выполняет команду select from ... [where ...]."""
    table_name, where_clause = parse_select(user_input)
    if not validate_clause(metadata, table_name, where_clause):
        return

    records = select(load_table_data(table_name), where_clause)
    _print_records(metadata[table_name], records)


@handle_db_errors
def _handle_update(metadata, user_input):
    """Выполняет команду update ... set ... where ..."""
    table_name, set_clause, where_clause = parse_update(user_input)
    if not (
        validate_clause(metadata, table_name, where_clause)
        and validate_clause(metadata, table_name, set_clause, allow_id=False)
    ):
        return

    table_data = load_table_data(table_name)
    ids = _matching_ids(table_data, where_clause)
    if not ids:
        print("Записи не найдены.")
        return

    table_data = update(table_data, set_clause, where_clause)
    save_table_data(table_name, table_data)
    for record_id in ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


@handle_db_errors
def _handle_delete(metadata, user_input):
    """Выполняет команду delete from ... where ..."""
    table_name, where_clause = parse_delete(user_input)
    if not validate_clause(metadata, table_name, where_clause):
        return

    table_data = load_table_data(table_name)
    ids = _matching_ids(table_data, where_clause)
    if not ids:
        print("Записи не найдены.")
        return

    table_data = delete(table_data, where_clause)
    if table_data is None:
        return  # пользователь отменил удаление

    save_table_data(table_name, table_data)
    for record_id in ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def run():
    """Запускает основной цикл программы: читает команды и выполняет их.

    На каждой итерации метаданные заново читаются из файла. Изменения
    таблиц и данных сразу сохраняются в файлы.
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
                if create_table(metadata, table_name, columns) is not None:
                    save_metadata(DB_META_FILE, metadata)
            case ["drop_table", table_name]:
                # сначала проверяем, что таблица есть, чтобы не спрашивать зря
                if (
                    validate_clause(metadata, table_name, None)
                    and drop_table(metadata, table_name) is not None
                ):
                    save_metadata(DB_META_FILE, metadata)
                    delete_table_data(table_name)
            case ["list_tables"]:
                list_tables(metadata)
            case ["insert", *_]:
                _handle_insert(metadata, user_input)
            case ["select", *_]:
                _handle_select(metadata, user_input)
            case ["update", *_]:
                _handle_update(metadata, user_input)
            case ["delete", *_]:
                _handle_delete(metadata, user_input)
            case ["info", table_name]:
                info(metadata, table_name, load_table_data(table_name))
            case ["help"]:
                print_help()
            case ["exit"]:
                break
            case [command, *_] if command in COMMANDS:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            case [command, *_]:
                print(f"Функции {command} нет. Попробуйте снова.")
