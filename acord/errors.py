""" Exceptions raised by the module """

class BaseResponseException(Exception):
    def __new__(cls, *args, **kwargs):
        return super(BaseResponseException, cls).__new__(BaseResponseException)

class GatewayConnectionRefused(BaseResponseException):
    """ Raised when connecting to gateway fails """


class CannotOverideTokenWarning(Warning):
    """ Warned when cannot use provided token due to binded token present """
