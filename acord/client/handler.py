from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway
from acord import User

from acord.errors import *


async def handle_websocket(self, ws):
    async for message in ws:
        await self.dispatch('socket_recieve')

        data = message.data
        if type(data) is bytes:
            data = decompressResponse(data)
            
        if not data:
            continue

        if not data.startswith('{'):
            data = ETF(data)
        else:
            data = JSON(data)

        print(data)

        if data['op'] == gateway.INVALIDSESSION:
            raise GatewayConnectionRefused(
                'Invalid session data, currently not handled in this version'
                '\nCommon causes can include:'
                '\n* Invalid intents'
                '\n* '
            )

        if data['t'] == 'READY':
            await self.dispatch('ready')

            self.session_id = data['d']['session_id']
            self.gateway_version = data['d']['v']
            self.user = User(conn=self.http, **data['d']['user'])

            continue

        if data['op'] == gateway.HEARTBEATACK:
            await self.dispatch('heartbeat')

        