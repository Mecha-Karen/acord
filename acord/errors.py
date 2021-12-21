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


class BadRequest(BaseResponseException):
    """Raised when requested recourse return 400,
    This is only raised for unhandled errors"""


class Forbidden(BaseResponseException):
    """Raised when requested recourse returns 403,
    indicating that you don't have sufficient permissions"""


class DiscordError(BaseResponseException):
    """Raised when requested recourse returns 500,
    Indicating an error has occured on discords side"""


class NotFound(BaseResponseException):
    """Raised when requested recourse returns 404,
    indicating that you dont have sufficient permissions"""


class CannotOverideTokenWarning(Warning):
    """Warned when cannot use provided token due to binded token present"""
