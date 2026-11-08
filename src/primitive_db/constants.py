# Хранение данных
DB_META_FILE = "db_meta.json"
DATA_DIR = "data"
JSON_INDENT = 4

# Схема таблиц
VALID_TYPES = {"int": int, "str": str, "bool": bool}
ID_COLUMN = "ID"
ID_TYPE = "int"

# Разбор команд: строковые значения берутся в такие кавычки
QUOTES = "\"'"

# Работа с консолью
PROMPT = ">>>Введите команду: "
CONFIRM_ANSWER = "y"
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
MODIFYING_COMMANDS = {"create_table", "drop_table", "insert", "update", "delete"}
