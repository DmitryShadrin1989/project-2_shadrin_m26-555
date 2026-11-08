import time

from primitive_db.constants import CONFIRM_ANSWER


def _copy_metadata(wrapper, func):
    """Копирует имя и описание исходной функции на обёртку.

    Делает то же, что functools.wraps: без этого у обёрнутой функции
    было бы имя wrapper и не было бы докстринга.
    """
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Перехватывает ошибки базы данных и выводит понятное сообщение.

    KeyError - не найдена таблица или столбец, ValueError - некорректное
    значение, RuntimeError - нарушено правило базы данных (например,
    таблица уже существует). Если функция завершилась с ошибкой,
    обёртка возвращает None.
    """

    def wrapper(*args, **kwargs):
        """Вызывает func и превращает её ошибки в сообщения."""
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

    return _copy_metadata(wrapper, func)


def confirm_action(action_name):
    """Фабрика декораторов: запрашивает подтверждение перед выполнением.

    Args:
        action_name: название действия для вопроса, например "удаление таблицы".

    Если пользователь ответил не CONFIRM_ANSWER ("y"), функция не вызывается
    и обёртка возвращает None.
    """

    def decorator(func):
        """Оборачивает func в запрос подтверждения."""

        def wrapper(*args, **kwargs):
            """Спрашивает подтверждение и вызывает func только при согласии."""
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            try:
                answer = input(question)
            except (KeyboardInterrupt, EOFError):
                print()
                answer = ""

            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return _copy_metadata(wrapper, func)

    return decorator


def log_time(func):
    """Замеряет время выполнения функции и выводит его в консоль."""

    def wrapper(*args, **kwargs):
        """Вызывает func и печатает, сколько секунд она выполнялась."""
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result

    return _copy_metadata(wrapper, func)


def create_cacher():
    """Создаёт функцию кэширования со своим словарём кэша в замыкании.

    Returns:
        Функция cache_result(key, value_func). Если результат для key уже
        есть в кэше, она возвращает его. Иначе вызывает value_func(),
        сохраняет результат в кэш и возвращает его.
    """
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет его через value_func."""
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
