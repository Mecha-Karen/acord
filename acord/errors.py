""" Exceptions raised by the module """


class BaseResponseException(Exception):
    ...


class HTTPException(BaseResponseException):
    def __init__(self, code, message):
        super().__init__(f"Status {code}: {message}")


class GatewayConnectionRefused(BaseResponseException):
    """Raised when connecting to gateway fails"""


class APIObjectDepreciated(BaseResponseException):
    """Raised when a certain item in the api has been depreciated"""


class Forbidden(BaseResponseException):
    """Raised when requested recourse returns 403,
    indicating that you don't have sufficient permissions"""


class NotFound(BaseResponseException):
    """Raised when requested recourse returns 404,
    indicating that you dont have sufficient permissions"""


class CannotOverideTokenWarning(Warning):
    """Warned when cannot use provided token due to binded token present"""
