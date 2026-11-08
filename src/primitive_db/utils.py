import json
from pathlib import Path

from primitive_db.constants import DATA_DIR


def _load_json(filepath, default):
    """Читает JSON-файл. Если файла нет, возвращает default."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _save_json(filepath, data):
    """Записывает данные в JSON-файл, полностью перезаписывая его."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def _table_path(table_name):
    """Возвращает путь к файлу данных таблицы, например data/users.json."""
    return Path(DATA_DIR) / f"{table_name}.json"


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла.

    Args:
        filepath: путь к файлу метаданных, например "db_meta.json".

    Returns:
        Словарь метаданных. Если файла ещё нет, возвращает пустой словарь.
    """
    return _load_json(filepath, {})


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл, полностью перезаписывая его.

    Args:
        filepath: путь к файлу метаданных, например "db_meta.json".
        data: словарь метаданных для сохранения.
    """
    _save_json(filepath, data)


def load_table_data(table_name):
    """Загружает строки таблицы из файла data/<имя_таблицы>.json.

    Args:
        table_name: имя таблицы.

    Returns:
        Список записей-словарей. Если файла ещё нет, возвращает пустой список.
    """
    return _load_json(_table_path(table_name), [])


def save_table_data(table_name, data):
    """Сохраняет строки таблицы в файл data/<имя_таблицы>.json.

    Папка data создаётся, если её ещё нет.

    Args:
        table_name: имя таблицы.
        data: список записей-словарей.
    """
    Path(DATA_DIR).mkdir(exist_ok=True)
    _save_json(_table_path(table_name), data)


def delete_table_data(table_name):
    """Удаляет файл данных таблицы. Если файла нет, ничего не делает.

    Args:
        table_name: имя таблицы.
    """
    _table_path(table_name).unlink(missing_ok=True)