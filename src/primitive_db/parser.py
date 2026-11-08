import re

INSERT_PATTERN = re.compile(r"insert\s+into\s+(\w+)\s+values\s*(.+)")
SELECT_PATTERN = re.compile(r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?")
UPDATE_PATTERN = re.compile(r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)")
DELETE_PATTERN = re.compile(r"delete\s+from\s+(\w+)\s+where\s+(.+)")

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


def _match(pattern, text):
    """Проверяет команду по шаблону и возвращает найденные части."""
    match = pattern.fullmatch(text.strip())
    if match is None:
        raise ValueError(text.strip())
    return match.groups()


def parse_insert(text):
    """insert into <таблица> values (...) -> (таблица, [значения])."""
    table_name, values = _match(INSERT_PATTERN, text)
    return table_name, parse_values(values)


def parse_select(text):
    """select from <таблица> [where ...] -> (таблица, условие или None)."""
    table_name, where = _match(SELECT_PATTERN, text)
    if where is None:
        return table_name, None
    return table_name, parse_where(where)


def parse_update(text):
    """update <таблица> set ... where ... -> (таблица, set, where)."""
    table_name, set_part, where = _match(UPDATE_PATTERN, text)
    return table_name, parse_set(set_part), parse_where(where)


def parse_delete(text):
    """delete from <таблица> where ... -> (таблица, условие)."""
    table_name, where = _match(DELETE_PATTERN, text)
    return table_name, parse_where(where)
