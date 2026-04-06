from typing import Optional, Any


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(
        self,
        message: str,
        code: str = "app_error",
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


# Infrastructure exceptions
class DatabaseException(AppException):
    """Ошибки базы данных"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="database_error",
            details=details
        )


class ConnectionError(DatabaseException):
    """Ошибка подключения к БД"""
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message=message, code="db_connection_error")


class QueryError(DatabaseException):
    """Ошибка выполнения запроса"""
    def __init__(self, message: str, table: Optional[str] = None):
        details = {"table": table} if table else {}
        super().__init__(message=message, code="db_query_error", details=details)


class IntegrityError(DatabaseException):
    """Ошибка целостности данных (дубликаты, foreign key)"""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message=message, code="db_integrity_error", details=details)


# Domain exceptions
class DomainException(AppException):
    """Базовое исключение доменного слоя"""
    def __init__(
        self,
        message: str,
        code: str = "domain_error",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message=message, code=code, details=details)


class NotFoundException(DomainException):
    """Ресурс не найден"""
    def __init__(
        self,
        resource: str,
        field: str,
        value: Any
    ):
        super().__init__(
            message=f"{resource} не найден",
            code="not_found",
            details={"resource": resource, "field": field, "value": value}
        )


class ValidationError(DomainException):
    """Ошибка валидации бизнес-логики"""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message=message, code="validation_error", details=details)


class ConflictError(DomainException):
    """Конфликт данных (дубликат)"""
    def __init__(
        self,
        resource: str,
        field: str,
        value: Any
    ):
        super().__init__(
            message=f"{resource} с таким {field} уже существует",
            code="conflict",
            details={"resource": resource, "field": field, "value": value}
        )


class UnprocessableError(DomainException):
    """Ошибка обработки данных (422)"""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message=message, code="unprocessable", details=details)


class ForbiddenError(DomainException):
    """Доступ запрещен (403) - недостаточно прав"""

    def __init__(
            self,
            message: str = "Доступ запрещен",
            required_role: Optional[str] = None,
            user_role: Optional[str] = None,
            details: Optional[dict] = None
    ):
        error_details = details or {}
        if required_role:
            error_details["required_role"] = required_role
        if user_role:
            error_details["user_role"] = user_role

        super().__init__(
            message=message,
            code="forbidden",
            details=error_details
        )
