from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создаёт таблицу и добавляет её описание в метаданные.

    Столбец ID:int добавляется первым автоматически. Если пользователь сам
    указал ID:int, дубль не создаётся. Метаданные меняются только после того,
    как все столбцы прошли проверку.

    Args:
        metadata: словарь метаданных вида {"имя_таблицы": {"столбец": "тип"}}.
        table_name: имя новой таблицы.
        columns: список столбцов в формате "имя:тип", например ["name:str"].
            Допустимые типы: int, str, bool.

    Returns:
        Обновлённый словарь метаданных. При ошибке выводит сообщение
        и возвращает метаданные без изменений.
    """
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
    """Удаляет таблицу из метаданных.

    Args:
        metadata: словарь метаданных вида {"имя_таблицы": {"столбец": "тип"}}.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновлённый словарь метаданных. Если таблицы нет, выводит ошибку
        и возвращает метаданные без изменений.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц, по одной в строке.

    Args:
        metadata: словарь метаданных вида {"имя_таблицы": {"столбец": "тип"}}.
    """
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")
