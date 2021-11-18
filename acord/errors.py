""" Exceptions raised by the module """
class BaseResponseException(Exception):
    def __new__(cls, *args, **kwargs):
        return super(BaseResponseException, cls).__new__(BaseResponseException)

class HTTPException(BaseResponseException):
    def __init__(self, code, message):
        super().__init__(f'Status {code}: {message}')

class GatewayConnectionRefused(BaseResponseException):
    """ Raised when connecting to gateway fails """

class APIObjectDepreciated(BaseResponseException):
    """ Raised when a certain item in the api has been depreciated """

class CannotOverideTokenWarning(Warning):
    """ Warned when cannot use provided token due to binded token present """
