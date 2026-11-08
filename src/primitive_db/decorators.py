import functools
import time


def handle_db_errors(func):
    """Перехватывает ошибки базы данных и выводит понятное сообщение.

    KeyError - не найдена таблица или столбец, ValueError - некорректное
    значение, RuntimeError - нарушено правило базы данных (например,
    таблица уже существует). Если функция завершилась с ошибкой,
    обёртка возвращает None.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}.")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
        except RuntimeError as error:
            print(f"Ошибка: {error}.")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name):
    """Фабрика декораторов: запрашивает подтверждение перед выполнением.

    Args:
        action_name: название действия для вопроса, например "удаление таблицы".

    Если пользователь ответил не "y", функция не вызывается и обёртка
    возвращает None.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            try:
                answer = input(question)
            except (KeyboardInterrupt, EOFError):
                print()
                answer = ""

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет время выполнения функции и выводит его в консоль."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result

    return wrapper
