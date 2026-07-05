class BaseCustomException(Exception):
    """Base class for all expected user errors."""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)
