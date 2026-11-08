from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.decorators import DatabaseError, handle_db_errors


def _ensure_table_exists(metadata, table_name):
    """Проверяет, что таблица существует.

    Raises:
        KeyError: если таблицы нет.
    """
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует')


def _format_columns(columns):
    """Превращает схему {"ID": "int", "name": "str"} в строку "ID:int, name:str"."""
    return ", ".join(f"{name}:{type_}" for name, type_ in columns.items())


@handle_db_errors
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
        Обновлённый словарь метаданных или None, если произошла ошибка
        (сообщение выводит декоратор handle_db_errors).
    """
    if table_name in metadata:
        raise DatabaseError(f'Таблица "{table_name}" уже существует')

    if not columns:
        raise DatabaseError("Не указаны столбцы таблицы")

    table_columns = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, _, column_type = column.partition(":")

        if name == ID_COLUMN and column_type == ID_TYPE:
            continue  # ID is already added

        if not name or column_type not in VALID_TYPES or name in table_columns:
            raise ValueError(column)

        table_columns[name] = column_type

    metadata[table_name] = table_columns

    columns_str = _format_columns(table_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata


@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных.

    Args:
        metadata: словарь метаданных вида {"имя_таблицы": {"столбец": "тип"}}.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновлённый словарь метаданных или None, если таблицы нет.
    """
    _ensure_table_exists(metadata, table_name)

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


def _validate_record(columns, record):
    """Проверяет, что все столбцы записи есть в схеме и типы значений совпадают.

    Args:
        columns: схема таблицы вида {"столбец": "тип"}.
        record: словарь вида {"столбец": значение}.

    Raises:
        KeyError: если столбца нет в схеме.
        ValueError: если тип значения не совпадает с типом столбца.
    """
    for column, value in record.items():
        if column not in columns:
            raise KeyError(f'Столбец "{column}" не существует')

        # type(), а не isinstance(): isinstance(True, int) тоже даёт True
        if type(value) is not VALID_TYPES[columns[column]]:
            raise ValueError(repr(value))


@handle_db_errors
def validate_clause(metadata, table_name, clause, allow_id=True):
    """Проверяет условие where или set по схеме таблицы.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        clause: словарь вида {"столбец": значение} или None.
        allow_id: можно ли использовать столбец ID (для set - нельзя).

    Returns:
        True, если таблица существует и условие подходит к её схеме.
        None, если есть ошибка (сообщение выводит handle_db_errors).
    """
    _ensure_table_exists(metadata, table_name)

    if clause is None:
        return True

    if not allow_id and ID_COLUMN in clause:
        raise DatabaseError(f"Столбец {ID_COLUMN} нельзя изменить")

    _validate_record(metadata[table_name], clause)
    return True


@handle_db_errors
def insert(metadata, table_name, values, table_data):
    """Добавляет новую запись в таблицу. ID генерируется автоматически.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        values: список значений для всех столбцов, кроме ID.
        table_data: текущие записи таблицы (список словарей).

    Returns:
        Обновлённый список записей или None, если данные некорректны
        (сообщение выводит декоратор handle_db_errors).
    """
    _ensure_table_exists(metadata, table_name)

    columns = metadata[table_name]
    data_columns = [column for column in columns if column != ID_COLUMN]

    if len(values) != len(data_columns):
        raise DatabaseError(
            f"Ожидалось значений: {len(data_columns)}, получено: {len(values)}"
        )

    record = dict(zip(data_columns, values))
    _validate_record(columns, record)

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


@handle_db_errors
def info(metadata, table_name, table_data):
    """Выводит описание таблицы: столбцы и количество записей.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        table_data: записи таблицы (список словарей).
    """
    _ensure_table_exists(metadata, table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {_format_columns(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")
