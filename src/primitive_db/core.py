from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def _table_exists(metadata, table_name):
    """Проверяет, что таблица существует. Если нет, выводит ошибку."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def _format_columns(columns):
    """Превращает схему {"ID": "int", "name": "str"} в строку "ID:int, name:str"."""
    return ", ".join(f"{name}:{type_}" for name, type_ in columns.items())


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

    columns_str = _format_columns(table_columns)
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
    if not _table_exists(metadata, table_name):
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


def _is_valid_record(columns, record):
    """Проверяет, что все столбцы записи есть в схеме и типы значений совпадают.

    Args:
        columns: схема таблицы вида {"столбец": "тип"}.
        record: словарь вида {"столбец": значение}.

    Returns:
        True, если всё верно. Иначе выводит ошибку и возвращает False.
    """
    for column, value in record.items():
        if column not in columns:
            print(f'Ошибка: Столбец "{column}" не существует.')
            return False

        # type(), а не isinstance(): isinstance(True, int) тоже даёт True
        if type(value) is not VALID_TYPES[columns[column]]:
            print(f"Некорректное значение: {value!r}. Попробуйте снова.")
            return False

    return True


def validate_clause(metadata, table_name, clause, allow_id=True):
    """Проверяет условие where или set по схеме таблицы.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        clause: словарь вида {"столбец": значение} или None.
        allow_id: можно ли использовать столбец ID (для set - нельзя).

    Returns:
        True, если таблица существует и условие подходит к её схеме.
        Иначе выводит ошибку и возвращает False.
    """
    if not _table_exists(metadata, table_name):
        return False

    if clause is None:
        return True

    if not allow_id and ID_COLUMN in clause:
        print(f"Ошибка: Столбец {ID_COLUMN} нельзя изменить.")
        return False

    return _is_valid_record(metadata[table_name], clause)


def insert(metadata, table_name, values, table_data):
    """Добавляет новую запись в таблицу. ID генерируется автоматически.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        values: список значений для всех столбцов, кроме ID.
        table_data: текущие записи таблицы (список словарей).

    Returns:
        Обновлённый список записей или None, если данные некорректны
        (сообщение об ошибке при этом уже выведено).
    """
    if not _table_exists(metadata, table_name):
        return None

    columns = metadata[table_name]
    data_columns = [column for column in columns if column != ID_COLUMN]

    if len(values) != len(data_columns):
        print(
            f"Ошибка: Ожидалось значений: {len(data_columns)}, получено: {len(values)}."
        )
        return None

    record = dict(zip(data_columns, values))
    if not _is_valid_record(columns, record):
        return None

    new_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    table_data.append({ID_COLUMN: new_id, **record})

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def _matches(record, where_clause):
    """Проверяет, подходит ли запись под все условия where_clause."""
    return all(record.get(column) == value for column, value in where_clause.items())


def select(table_data, where_clause=None):
    """Возвращает записи таблицы, подходящие под условие.

    Args:
        table_data: записи таблицы (список словарей).
        where_clause: условие вида {"age": 28} или None.

    Returns:
        Все записи, если условие не задано, иначе только подходящие.
    """
    if where_clause is None:
        return table_data
    return [record for record in table_data if _matches(record, where_clause)]


def update(table_data, set_clause, where_clause):
    """Обновляет поля в записях, подходящих под условие.

    Args:
        table_data: записи таблицы (список словарей).
        set_clause: новые значения вида {"age": 29}.
        where_clause: условие вида {"name": "Sergei"}.

    Returns:
        Изменённый список записей.
    """
    for record in select(table_data, where_clause):
        record.update(set_clause)
    return table_data


def delete(table_data, where_clause):
    """Удаляет записи, подходящие под условие.

    Args:
        table_data: записи таблицы (список словарей).
        where_clause: условие вида {"ID": 1}.

    Returns:
        Новый список записей без удалённых.
    """
    return [record for record in table_data if not _matches(record, where_clause)]


def info(metadata, table_name, table_data):
    """Выводит описание таблицы: столбцы и количество записей.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        table_data: записи таблицы (список словарей).
    """
    if not _table_exists(metadata, table_name):
        return

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {_format_columns(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")
