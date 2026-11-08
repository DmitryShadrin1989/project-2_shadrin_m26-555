QUOTES = "\"'"


def parse_value(token):
    """Превращает текстовое значение в значение Python.

    Строки должны быть в кавычках: "Sergei" -> 'Sergei'.
    true / false -> True / False, целое число -> int.

    Raises:
        ValueError: если значение не подходит ни под один формат.
    """
    token = token.strip()
    if not token:
        raise ValueError("пустое значение")

    if len(token) >= 2 and token[0] in QUOTES and token[-1] == token[0]:
        return token[1:-1]

    if token.lower() == "true":
        return True
    if token.lower() == "false":
        return False

    try:
        return int(token)
    except ValueError:
        raise ValueError(token) from None


def split_by_comma(text):
    """Делит строку по запятым, не трогая запятые внутри кавычек.

    '"Smith, John", 30' -> ['"Smith, John"', ' 30']

    Raises:
        ValueError: если кавычка не закрыта.
    """
    parts = []
    current = ""
    quote = None  # открытая сейчас кавычка или None

    for char in text:
        if quote:
            if char == quote:
                quote = None
        elif char in QUOTES:
            quote = char
        elif char == ",":
            parts.append(current)
            current = ""
            continue
        current += char

    if quote:
        raise ValueError(text.strip())

    parts.append(current)
    return parts


def parse_values(text):
    """Разбирает список значений в скобках.

    '("Sergei", 28, true)' -> ['Sergei', 28, True]
    """
    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)

    inner = text[1:-1]
    if not inner.strip():
        return []
    return [parse_value(part) for part in split_by_comma(inner)]


def _parse_pair(text):
    """Разбирает пару 'столбец = значение' -> ('столбец', значение)."""
    column, sep, value = text.partition("=")
    column = column.strip()
    if not sep or not column:
        raise ValueError(text.strip())
    return column, parse_value(value)


def parse_where(text):
    """Разбирает условие where: 'age = 28' -> {'age': 28}."""
    column, value = _parse_pair(text)
    return {column: value}


def parse_set(text):
    """Разбирает часть set: 'age = 29, name = "Ivan"' -> {'age': 29, 'name': 'Ivan'}.

    Raises:
        ValueError: если столбец указан дважды.
    """
    result = {}
    for part in split_by_comma(text):
        column, value = _parse_pair(part)
        if column in result:
            raise ValueError(part.strip())
        result[column] = value
    return result


def _is_table_name(name):
    """Проверяет, что имя таблицы состоит только из букв, цифр и "_"."""
    return all(char.isalnum() or char == "_" for char in name)


def parse_insert(text):
    """insert into <таблица> values (...) -> (таблица, [значения])."""
    text = text.strip()
    parts = text.split(maxsplit=3)  # insert, into, таблица, values (...)
    if (
        len(parts) != 4
        or parts[:2] != ["insert", "into"]
        or not _is_table_name(parts[2])
        or not parts[3].startswith("values")
    ):
        raise ValueError(text)

    values_part = parts[3].removeprefix("values")
    if not values_part.strip():
        raise ValueError(text)
    return parts[2], parse_values(values_part)


def parse_select(text):
    """select from <таблица> [where ...] -> (таблица, условие или None)."""
    text = text.strip()
    parts = text.split(maxsplit=4)  # select, from, таблица, [where, условие]
    if parts[:2] != ["select", "from"] or len(parts) < 3:
        raise ValueError(text)
    if not _is_table_name(parts[2]):
        raise ValueError(text)

    if len(parts) == 3:
        return parts[2], None
    if len(parts) == 5 and parts[3] == "where":
        return parts[2], parse_where(parts[4])
    raise ValueError(text)


def parse_update(text):
    """update <таблица> set ... where ... -> (таблица, set, where)."""
    text = text.strip()
    parts = text.split(maxsplit=3)  # update, таблица, set, остаток
    if (
        len(parts) != 4
        or parts[0] != "update"
        or parts[2] != "set"
        or not _is_table_name(parts[1])
    ):
        raise ValueError(text)

    set_part, sep, where_part = parts[3].partition(" where ")
    if not sep or not set_part.strip() or not where_part.strip():
        raise ValueError(text)
    return parts[1], parse_set(set_part), parse_where(where_part)


def parse_delete(text):
    """delete from <таблица> where ... -> (таблица, условие)."""
    text = text.strip()
    parts = text.split(maxsplit=4)  # delete, from, таблица, where, условие
    if (
        len(parts) != 5
        or parts[:2] != ["delete", "from"]
        or parts[3] != "where"
        or not _is_table_name(parts[2])
    ):
        raise ValueError(text)
    return parts[2], parse_where(parts[4])
