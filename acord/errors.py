""" Exceptions raised by the module """
from typing import Any


class BaseExc(Exception):
    def __init__(self, message, **attrs) -> None:
        self._attrs = attrs

        super().__init__(message)

    def __getattribute__(self, __name: str) -> Any:
        try:
            attrs = object.__getattribute__(self, "_attrs")
            return attrs[__name]
        except (KeyError, AttributeError):
            pass
  
        return object.__getattribute__(self, __name)


class HTTPException(BaseExc):
    def __init__(self, code, message):
        super().__init__(f"Status {code}: {message}")


class SlashOptionError(BaseExc):
    """ Raised when validating slash option fails """


class SlashCommandError(BaseExc):
    """ Raised when validated slash command fails """


class ApplicationCommandError(BaseExc):
    """ Raised when an error occurs with application commands """


class GatewayConnectionRefused(BaseExc):
    """Raised when connecting to gateway fails"""


class APIObjectDepreciated(BaseExc):
    """Raised when a certain item in the api has been depreciated"""


class BadRequest(BaseExc):
    """Raised when requested recourse return 400,
    This is only raised for unhandled errors"""


class Forbidden(BaseExc):
    """Raised when requested recourse returns 403,
    indicating that you don't have sufficient permissions"""


class DiscordError(BaseExc):
    """Raised when requested recourse returns 500,
    Indicating an error has occured on discords side"""


class NotFound(BaseExc):
    """Raised when requested recourse returns 404,
    indicating that you dont have sufficient permissions"""


class VoiceError(BaseExc):
    """Raised when a voice operation fails or goes wrong,
    mostly due to user side operations.
    """


class CannotOverideTokenWarning(Warning):
    """Warned when cannot use provided token due to binded token present"""
