"""
All version related info for connecting to the gateway.
"""
import yarl
import typing

API_VERSION = 9
BASE_API_URL = "https://discord.com/api"
GATEWAY_ENCODING = typing.Literal["JSON", "ETF"]


def buildURL(*paths, **parameters) -> str:
    URI = f'{BASE_API_URL}/v{API_VERSION}'
    for path in paths:
        URI += f'/{path}'

    if not parameters:
        return URI

    URI += '?'

    for key, value in parameters.items():
        URI += f'{key}={value}&'

    return yarl.URL(URI)
