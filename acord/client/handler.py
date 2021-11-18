from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway

from acord.errors import *
from ..models import User, Message


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

        EVENT = data['t']
        OPERATION = data['op']
        DATA = data['d']
        SEQUENCE = data['s']

        gateway.SEQUENCE = SEQUENCE

        if OPERATION == gateway.INVALIDSESSION:
            raise GatewayConnectionRefused(
                'Invalid session data, currently not handled in this version'
                '\nCommon causes can include:'
                '\n* Invalid intents'
            )

        if OPERATION == gateway.HEARTBEATACK:
            await self.dispatch('heartbeat')

        if EVENT == 'READY':
            await self.dispatch('ready')

            self.session_id = DATA['session_id']
            self.gateway_version = DATA['v']
            self.user = User(conn=self.http, **DATA['user'])

            continue

        if EVENT == 'MESSAGE_CREATE':
            message = Message(conn=self.http, **DATA)

            await self.dispatch('message', message)