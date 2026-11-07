import json


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла.

    Args:
        filepath: путь к файлу метаданных, например "db_meta.json".

    Returns:
        Словарь метаданных. Если файла ещё нет, возвращает пустой словарь.
    """
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл, полностью перезаписывая его.

    Args:
        filepath: путь к файлу метаданных, например "db_meta.json".
        data: словарь метаданных для сохранения.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
