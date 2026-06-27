class AppException(Exception):
    """Базовое исключение приложения."""


class NotFoundError(AppException):
    """Запрошенный объект не найден"""


class AlreadyExistsError(AppException):
    """Объект с такими уникальными полями уже существует"""


class InvalidCredentialsError(AppException):
    """Неверный email/пароль при логине"""


class PermissionDeniedError(AppException):
    """У пользователя нет прав на это действие"""


class InsufficientStockError(AppException):
    """Недостаточно товара на складе для оформления заказа"""


class InvalidOperationError(AppException):
    """Операция недопустима в текущем состоянии объекта"""
