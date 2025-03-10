from typing import ParamSpec

P = ParamSpec("P")


class DomainException(Exception):

    TYPE = "internal_server_error"
    MESSAGE = "Internal Server Error"

    def __init__(self, message: str | None = None, *args: P.args, **kwargs: P.kwargs):
        self._message = message
        self._kwargs = kwargs
        super().__init__(message)

    @property
    def message(self) -> str:
        return self._message or self.MESSAGE.format(**self._kwargs)

    def __str__(self):
        return self.message


class InvalidFieldValue(DomainException):
    TYPE = "invalid_field_value"
    MESSAGE = "Invalid value {field_value} for field {field_name}"


class UserNotFound(DomainException):
    TYPE = "user_not_found"
    MESSAGE = "User {user_id} not found"


class PostNotFound(DomainException):
    TYPE = "post_not_found"
    MESSAGE = "Post {post_id} not found"


class Forbiden(DomainException):
    TYPE = "forbidden"
    MESSAGE = "Access Forbidden"
