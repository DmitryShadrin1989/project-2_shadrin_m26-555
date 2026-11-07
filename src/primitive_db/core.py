VALID_TYPES = {"int", "str", "bool"}
ID_COLUMN = "ID"
ID_TYPE = "int"


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not columns:
        print("Ошибка: Не указаны столбцы таблицы.")
        return metadata

    table_columns = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, _, column_type = column.partition(":")

        if name == ID_COLUMN and column_type == ID_TYPE:
            continue  # ID is already added

        if not name or column_type not in VALID_TYPES or name in table_columns:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        table_columns[name] = column_type

    metadata[table_name] = table_columns

    columns_str = ", ".join(f"{name}:{type_}" for name, type_ in table_columns.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")
