import datetime

from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway
from acord.voice.core import VoiceConnection
from acord.utils import _d_to_channel
from acord.errors import *
from acord.models import *


async def handle_websocket(self, ws):

    async for message in ws:
        if self.dispatch_on_recv:
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

        if EVENT != "VOICE_SERVER_UPDATE":
            SEQUENCE = data["s"]
            gateway.SEQUENCE = SEQUENCE

        UNAVAILABLE = dict()

        if OPERATION == gateway.INVALIDSESSION:
            raise GatewayConnectionRefused(
                "Invalid session data, currently not handled in this version"
                "\nCommon causes can include:"
                "\n* Invalid intents"
            )

        elif OPERATION == gateway.RESUME:
            self.dispatch("resume")

        elif OPERATION == gateway.HEARTBEATACK:
            self.dispatch("heartbeat")

        elif EVENT == "READY":
            self.dispatch("ready")

            self.session_id = DATA["session_id"]
            self.gateway_version = DATA["v"]
            self.user = User(conn=self.http, **DATA["user"])

            UNAVAILABLE = {i["id"]: i["unavailable"] for i in DATA["guilds"]}

            self.INTERNAL_STORAGE["users"].update({self.user.id: self.user})

            continue

        # NOTE: Interactions

        elif EVENT == "INTERACTION_CREATE":
            data = Interaction(conn=self.http, **DATA)

            self.dispatch("interaction_create", data)

        elif EVENT == "INTERACTION_UPDATE":
            data = Interaction(conn=self.http, **DATA)

            self.dispatch("interaction_update", data)

        elif EVENT == "INTERACTION_DELETE":
            try:
                id, guild_id, application_id = DATA.values()
            except ValueError:
                id, guild_id, application_id = DATA.values(), None

            self.dispatch("interaction_delete", id, guild_id, application_id)

        # NOTE: Messages

        elif EVENT == "MESSAGE_CREATE":
            message = Message(conn=self.http, **DATA)

            try:
                if hasattr(message.channel, "last_message_id"):
                    message.channel.last_message_id = message.id
            except ValueError:
                pass

            self.INTERNAL_STORAGE["messages"].update(
                {f"{message.channel_id}:{message.id}": message}
            )

            self.dispatch("message", message)

        elif EVENT == "CHANNEL_PINS_UPDATE":
            channel = self.get_channel(int(DATA["channel_id"]))
            ts = datetime.datetime.fromisoformat(DATA["last_pin_timestamp"])

            self.dispatch("message_pin", channel, ts)

        # NOTE: Guilds

        elif EVENT == "GUILD_CREATE":
            guild = Guild(conn=self.http, **DATA)

            if DATA["id"] in UNAVAILABLE:
                UNAVAILABLE.pop(DATA["id"])
                self.dispatch("guild_recv", guild)
            else:
                self.dispatch("guild_create", guild)

            self.INTERNAL_STORAGE["guilds"].update({int(DATA["id"]): guild})

        elif EVENT == "GUILD_DELETE":
            if DATA.get("unavailable", None) is not None:
                guild = Guild(conn=self.http, **DATA)
                UNAVAILABLE.pop(DATA["id"])
                self.dispatch("guild_outage", guild)

                self.INTERNAL_STORAGE["guilds"].update({int(DATA["id"]): guild})
            else:
                guild = self.INTERNAL_STORAGE["guilds"].pop(DATA["id"])
                self.dispatch("guild_remove", guild)

        elif EVENT == "GUILD_UPDATE":
            guild = Guild(conn=self.http, **DATA)

            self.INTERNAL_STORAGE["guilds"].update({guild.id: guild})
            self.dispatch("guild_update", guild)

        elif EVENT == "GUILD_BAN_ADD":
            guild = self.get_guild(int(DATA["guild_id"]))
            user = User(conn=self.http, **DATA["user"])

            guild.members.pop(user.id)
            self.INTERNAL_STORAGE["users"].update({user.id: user})
            self.dispatch("guild_ban", guild, user)

        elif EVENT == "GUILD_BAN_REMOVE":
            guild = self.get_guild(int(DATA["guild_id"]))
            user = User(conn=self.http, **DATA["user"])

            self.INTERNAL_STORAGE["users"].update({user.id: user})
            self.dispatch("guild_ban_remove", guild, user)

        elif EVENT == "GUILD_EMOJIS_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            emojis = DATA["emojis"]
            bulk = list()

            for emoji in emojis:
                e = Emoji(conn=self.http, guild_id=guild.id, **emoji)
                guild.emojis.update({e.id: e})
                bulk.append(e)

                self.dispatch("emoji_update", e)

            self.dispatch("emojis_update", bulk)

        elif EVENT == "GUILD_STICKERS_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            stickers = DATA["stickers"]
            bulk = list()

            for sticker in stickers:
                s = Sticker(conn=self.http, guild_id=guild.id, **sticker)
                guild.stickers.update({s.id: s})
                bulk.append(s)

                self.dispatch("sticker_update", s)

            self.dispatch("stickers_update", bulk)

        # NOTE: channels

        elif EVENT == "CHANNEL_CREATE":
            channel, _ = _d_to_channel(DATA, self.http)

            self.INTERNAL_STORAGE["channels"].update({channel.id: channel})
            self.dispatch("channel_create", channel)

        elif EVENT == "CHANNEL_UPDATE":
            channel, _ = _d_to_channel(DATA, self.http)

            self.INTERNAL_STORAGE["channels"].update({channel.id: channel})
            self.dispatch("channel_update", channel)

        elif EVENT == "CHANNEL_DELETE":
            channel = self.INTERNAL_STORAGE["channels"].pop(int(DATA["id"]))
            self.dispatch("channel_delete", channel)

        # NOTE: threads

        elif EVENT == "THREAD_CREATE":
            thread = Thread(conn=self.http, **DATA)

            guild = self.get_guild(thread.guild_id)
            guild.threads.update({thread.id: thread})

            self.dispatch("thread_create", thread)

        elif EVENT == "THREAD_UPDATE":
            thread = Thread(conn=self.http, **DATA)

            guild = self.get_guild(thread.guild_id)
            guild.threads.update({thread.id: thread})

            self.dispatch("thread_update", thread)

        elif EVENT == "THREAD_DELETE":
            guild = self.get_guild(int(DATA["guild_id"]))
            thread = guild.threads.pop(int(DATA["guild_id"]))

            self.dispatch("thread_delete")

        elif EVENT == "THREAD_SYNC_LIST":
            guild = self.get_guild(int(DATA["guild_id"]))
            threads = list()

            for thread in DATA["threads"]:
                tr = Thread(conn=self.http, **thread)
                threads.append(tr)

                guild.threads.update({tr.id: tr})

            self.dispatch("thread_sync", threads)

        elif EVENT == "THREAD_MEMBER_UPDATE":
            guild = self.get_guild(int(DATA.pop("guild_id")))
            member = ThreadMember(**DATA)

            guild.threads[member.id].members.update({member.user_id: member})

            self.dispatch("thread_member_update", member)

        elif EVENT == "THREAD_MEMBERS_UPDATE":
            guild = self.get_guild(int(DATA.pop("guild_id")))
            thread = guild.threads[int(DATA.pop("id"))]

            thread.member_count = DATA["member_count"]

            for member in DATA["added_members"]:
                trm = ThreadMember(**member)
                thread.members.update({trm.id: trm})

            for member in DATA["removed_member_ids"]:
                thread.members.pop(int(member), None)
                # Not all members may be in the thread

            self.dispatch("thread_members_update", thread)

        elif EVENT == "VOICE_STATE_UPDATE":
            self.awaiting_voice_connections.update({
                DATA["guild_id"]: (DATA["session_id"], DATA["channel_id"])
                })

            m = Member(
                conn=self.http, 
                guild_id=DATA["guild_id"],
                voice_state=DATA,
                **DATA["member"]
            )

            if m.user.id == self.user.id:
                # call manual disconnect if OP 13 has not already been recieved
                conn = self.voice_connections.pop(DATA["guild_id"], None)
                if conn is not None:
                    await conn.disconnect()

            self.INTERNAL_STORAGE["guilds"][m.guild_id].members.update({m.user.id: m})
            channel_id = DATA["channel_id"]

            self.dispatch("voice_state_update", channel_id, m)

        # NOTE: VOICE EVENTS
        elif EVENT == "VOICE_SERVER_UPDATE":
            session_id, channel_id = self.awaiting_voice_connections.pop(DATA["guild_id"], None)

            if not session_id:
                continue
            data["d"]["session_id"] = session_id
            data["d"]["user_id"] = self.user.id

            vc = VoiceConnection(data, self.loop, self, channel_id)
            self.voice_connections.update({DATA["guild_id"]: vc})

            # Handled by default handler in Client.on_voice_server_update
            self.dispatch("voice_server_update", vc)
