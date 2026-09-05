class AppException(Exception):
    """Настройка обработки ошибок."""

    def __init__(
        self,
        status_code: int,
        detail: str,
    ) -> None:
        """Меняем формат возвращаемой ошибки."""
        self.status_code = status_code
        self.message = detail
