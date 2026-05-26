class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BadRequestException(AppException):
    def __init__(self, message="Bad request"):
        super().__init__(message, 400)


class UnauthorizedException(AppException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)


class ForbiddenException(AppException):
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403)


class NotFoundException(AppException):
    def __init__(self, message="Not found"):
        super().__init__(message, 404)


class ConflictException(AppException):
    def __init__(self, message="Conflict"):
        super().__init__(message, 409)