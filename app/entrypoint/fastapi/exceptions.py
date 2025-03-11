from typing import Type
from app.domain import exceptions as domain_exceptions
from fastapi import status, FastAPI
from fastapi.responses import ORJSONResponse


# type alias
DomainExceptionType = Type[domain_exceptions.DomainException]

# map domain exception to http status code
EXCEPTION_STATUS_MAPPING: dict[DomainExceptionType, int] = {
    domain_exceptions.UserNotFound: status.HTTP_404_NOT_FOUND,
    domain_exceptions.PostNotFound: status.HTTP_404_NOT_FOUND,
    domain_exceptions.InvalidFieldValue: status.HTTP_400_BAD_REQUEST,
    domain_exceptions.Forbiden: status.HTTP_403_FORBIDDEN,
}


# exec when exception is captured
# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers
def setup_exceptions_handler(app: FastAPI) -> None:
    @app.exception_handler(domain_exceptions.DomainException)
    # https://fastapi.tiangolo.com/advanced/custom-response/#ujsonresponse
    def domain_exception_handler(_, exc: domain_exceptions.DomainException) -> ORJSONResponse:
        return ORJSONResponse(
            content={
                "error": exc.message,
                "type": exc.TYPE
            },
            status_code=EXCEPTION_STATUS_MAPPING.get(
                type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        )

    @app.exception_handler(Exception)
    def non_domain_exception_handler(_, exc: Exception) -> ORJSONResponse:
        # TODO
        # logger.error(exception)

        return ORJSONResponse(
            content={
                "error": str(exc),
                "type": "internal_server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
