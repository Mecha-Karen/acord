from typing import Dict
from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway

from acord.errors import *
from ..models import User, Message, Guild


async def handle_websocket(self, ws):

    async for message in ws:
        self.dispatch("socket_recieve", message)

        data = message.data
        if type(data) is bytes:
            data = decompressResponse(data)

        if not data:
            continue

        if not data.startswith("{"):
            data = ETF(data)
        else:
            data = JSON(data)

        EVENT = data["t"]
        OPERATION = data["op"]
        DATA = data["d"]
        SEQUENCE = data["s"]

        gateway.SEQUENCE = SEQUENCE
        UNAVAILABLE = list()

        if OPERATION == gateway.INVALIDSESSION:
            raise GatewayConnectionRefused(
                "Invalid session data, currently not handled in this version"
                "\nCommon causes can include:"
                "\n* Invalid intents"
            )

        if OPERATION == gateway.HEARTBEATACK:
            self.dispatch("heartbeat")

        if EVENT == "READY":
            self.dispatch("ready")

            self.session_id = DATA["session_id"]
            self.gateway_version = DATA["v"]
            self.user = User(conn=self.http, **DATA["user"])
            UNAVAILABLE = [i["id"] for i in DATA["guilds"]]

            self.INTERNAL_STORAGE["users"].update({self.user.id: self.user})

            continue

        if EVENT == "MESSAGE_CREATE":
            message = Message(conn=self.http, **DATA)
            self.INTERNAL_STORAGE["messages"].update(
                {f"{message.channel_id}:{message.id}": message}
            )

            self.dispatch("message", message)

        if EVENT == "GUILD_CREATE":
            guild = Guild(conn=self.http, **DATA)

            if DATA["id"] in UNAVAILABLE:
                UNAVAILABLE.remove(DATA["id"])
                self.dispatch("guild_recv", guild)
            else:
                self.dispatch("guild_create", guild)

            self.INTERNAL_STORAGE["guilds"].update({int(DATA["id"]): guild})

        if EVENT == "GUILD_DELETE":
            if DATA.get("unavailable", None) is not None:
                guild = Guild(conn=self.http, **DATA)
                UNAVAILABLE.remove(DATA["id"])
                self.dispatch("guild_outage", guild)

                self.INTERNAL_STORAGE["guilds"].update({int(DATA["id"]): guild})
            else:
                guild = self.INTERNAL_STORAGE["guilds"].pop(DATA["id"])
                self.dispatch("guild_remove", guild)
