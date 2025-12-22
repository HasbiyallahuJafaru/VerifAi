class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ValidationError(AppError):
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=400)
