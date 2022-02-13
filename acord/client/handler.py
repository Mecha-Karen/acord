import asyncio
import datetime
import time
import logging
from aiohttp import WSMsgType

from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway
from acord.voice.core import VoiceConnection
from acord.utils import _d_to_channel
from acord.errors import *
from acord.models import *
from acord.bases import *

CLOSE_CODES = (WSMsgType.CLOSED, WSMsgType.CLOSING, WSMsgType.CLOSE)
logger = logging.getLogger(__name__)


def get_slash_options(interaction: Interaction) -> dict:
    data = dict()

    for option in interaction.data.options:
        data.update({option.name: option})
    return data


class Empty:
    def dict(self):
        return {}


async def handle_websocket(self, ws, on_ready_scripts=[]):
    ready_scripts = filter(lambda x: x is not None, on_ready_scripts)
    UNAVAILABLE = dict()

    self._resume = False

    while not self._resume:
        message = await ws.receive()

        if message.type in CLOSE_CODES:
            # Connection lost!
            logger.info(f"Websocket connection has been closed, resuming session shortly : code={message.data}")
            
            self._resume = True
            return

        if self.dispatch_on_recv:
            self.dispatch("socket_receive", message)

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

        if SEQUENCE is not None:
            self.sequence = SEQUENCE

        if OPERATION == gateway.INVALIDSESSION:
            raise GatewayConnectionRefused(
                "Invalid session data, currently not handled in this version"
                "\nCommon causes can include:"
                "\n* Invalid intents"
            )

        elif OPERATION == gateway.RESUME:
            self.dispatch("resume")

        elif OPERATION == gateway.HEARTBEATACK:
            p = time.perf_counter()
            ping = p - self.acked_at

            self.latency = ping
            self.dispatch("heartbeat", ping)

        elif EVENT == "READY":
            self.dispatch("ready")

            self.session_id = DATA["session_id"]
            self.gateway_version = DATA["v"]
            self.user = User(conn=self.http, **DATA["user"])

            for script in ready_scripts:
                self.loop.create_task(script)

            UNAVAILABLE = {i["id"]: i["unavailable"] for i in DATA["guilds"]}
            self.INTERNAL_STORAGE["users"].update({self.user.id: self.user})

            continue

        # NOTE: Interactions

        elif EVENT == "INTERACTION_CREATE":
            data = Interaction(conn=self.http, **DATA)

            if data.type == InteractionType.APPLICATION_COMMAND:
                udac = self.application_commands.get(data.data.name)

                if udac is not None:
                    if isinstance(udac, list):
                        # Use this to find command
                        for i in udac:
                            if i.type == data.data.type:
                                udac = i
                                break

                    args, kwds = (), {}
                    if data.data.type == ApplicationCommandType.CHAT_INPUT:
                        kwds = get_slash_options(data)
                    elif data.data.type == ApplicationCommandType.MESSAGE:
                        message = self.get_message(data.channel_id, data.data.target_id)
                        if not message:
                            message = data.data.target_id
                        args = (message,)
                    else:
                        user = self.get_user(data.data.target_id)
                        if not user:
                            user = data.data.target_id
                        args = (user,)

                    fut = self.loop.create_future()
                    self.loop.create_task(
                        udac.dispatcher(data, fut, *args, **kwds),
                        name=f"app_cmd dispatcher : {udac.name}",
                    )

                    possible_exc = await asyncio.wait_for(fut, None)
                    if isinstance(possible_exc, Exception):
                        self.on_error(f"app_cmd dispatcher : {udac.name}")

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

            self.dispatch("message_create", message)

        elif EVENT == "MESSAGE_UPDATE":
            pre_existing = self.get_message(DATA["channel_id"], DATA["id"]) or Empty()
            m_data = {**DATA, **pre_existing.dict()}
            m_data["conn"] = self.http

            message = Message(**m_data)

            try:
                if hasattr(message.channel, "last_message_id"):
                    message.channel.last_message_id = message.id
            except ValueError:
                pass

            self.INTERNAL_STORAGE["messages"].update(
                {f"{message.channel_id}:{message.id}": message}
            )

            self.dispatch("message_update", message)

        elif EVENT == "MESSAGE_DELETE":
            message = self.get_message(DATA["channel_id"], DATA["id"])
            if message:
                self.INTERNAL_STORAGE["messages"].pop(f"{DATA['channel_id']}:{DATA['id']}")
                self.dispatch("message_delete", message)
            else:
                self.dispatch("partial_message_delete",
                    Snowflake(DATA["channel_id"]),
                    Snowflake(DATA["id"]),
                    Snowflake(DATA["guild_id"]) if DATA["guild_id"] is not None else None
                )

        elif EVENT == "MESSAGE_DELETE_BULK":
            messages = [
                (
                    self.get_message(DATA["channel_id"], id) or Snowflake(id)
                )
                for id in DATA["ids"]
            ]

            self.dispatch("bulk_message_delete", 
                messages, 
                Snowflake(DATA["channel_id"]),
                Snowflake(DATA["guild_id"]) if DATA["guild_id"] is not None else None
            )

        elif EVENT == "MESSAGE_REACTION_ADD":
            reaction = MessageReaction(**DATA)

            message = self.get_message(reaction.channel_id, reaction.message_id)
            if message is not None:
                if reaction.emoji not in message.reactions:
                    message.reactions[reaction.emoji] = [reaction]
                else:
                    message.reactions[reaction.emoji].append(reaction)

        elif EVENT == "CHANNEL_PINS_UPDATE":
            channel = self.get_channel(int(DATA["channel_id"]))
            ts = datetime.datetime.fromisoformat(DATA["last_pin_timestamp"])

            self.dispatch("message_pin", channel, ts)

        # NOTE: invites
        elif EVENT == "INVITE_CREATE":
            invite = Invite(conn=self.http, **DATA)
            self.dispatch("invite_create", invite)

        elif EVENT == "INVITE_DELETE":
            channel_id = DATA["channel_id"]
            guild_id = DATA.get("guild_id", 0)
            code = DATA["code"]

            channel = self.get_channel(channel_id) or Snowflake(channel_id)
            guild = self.get_guild(guild_id) or (
                Snowflake(guild_id) if guild_id is not None else None
            )

            self.dispatch("invite_delete", channel, guild, code)

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

                self.dispatch("guild_emoji_update", e)

            self.dispatch("guild_emojis_update", bulk)

        elif EVENT == "GUILD_STICKERS_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            stickers = DATA["stickers"]
            bulk = list()

            for sticker in stickers:
                s = Sticker(conn=self.http, guild_id=guild.id, **sticker)
                guild.stickers.update({s.id: s})
                bulk.append(s)

                self.dispatch("guild_sticker_update", s)

            self.dispatch("guild_stickers_update", bulk)

        elif EVENT == "GUILD_INTEGRATIONS_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            if guild is None:
                guild = Snowflake(DATA["guild_id"])
            self.dispatch("guild_integrations_update", guild)

        elif EVENT == "GUILD_MEMBER_ADD":
            member = Member(conn=self.http, **DATA)
            guild = self.get_guild(member.guild_id)

            if guild is not None:
                guild.members.update({member.user.id: member})
            else:
                guild = Snowflake(DATA["guild_id"])

            self.dispatch("member_join", member, guild)

        elif EVENT == "GUILD_MEMBER_REMOVE":
            guild = self.get_guild(int(DATA["guild_id"]))
            user = User(conn=self.http, **DATA["user"])
            
            if guild is not None:
                user = guild.members.pop(user.id, user)
            else:
                guild = Snowflake(DATA["guild_id"])
            
            self.dispatch("member_remove", user, guild)

        elif EVENT == "GUILD_MEMBER_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            a_member = Member(conn=self.http, **DATA)

            if guild is not None:
                b_member = guild.get_member(a_member.user.id)
                guild.members.update({a_member.user.id: a_member})
            else:
                b_member = None
            
            self.dispatch("member_update", b_member, a_member, guild)

        elif EVENT == "GUILD_ROLE_CREATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            role = Role(conn=self.http, **(DATA["role"]))

            guild.roles.update({role.id: role})

            self.dispatch("role_create", role, guild)

        elif EVENT == "GUILD_ROLE_UPDATE":
            guild = self.get_guild(int(DATA["guild_id"]))
            a_role = Role(conn=self.http, **(DATA["role"]))
            b_role = guild.roles.get(a_role.id)

            guild.roles.update({role.id: role})

            self.dispatch("role_update", a_role, b_role, guild)

        elif EVENT == "GUILD_ROLE_DELETE":
            guild = self.get_guild(int(DATA["guild_id"]))
            role = guild.roles.get(Snowflake(DATA["role_id"]))

            self.dispatch("role_delete", role, guild)

        elif EVENT == "GUILD_SCHEDULED_EVENT_CREATE":
            event = GuildScheduledEvent(conn=self.http, **DATA)
            guild = self.get_guild(event.guild_id)
            guild.guild_scheduled_events.update({event.id: event})

            self.dispatch("guild_scheduled_event_create", event, guild)

        elif EVENT == "GUILD_SCHEDULED_EVENT_UPDATE":
            event = GuildScheduledEvent(conn=self.http, **DATA)
            guild = self.get_guild(event.guild_id)
            guild.guild_scheduled_events.update({event.id: event})

            self.dispatch("guild_scheduled_event_update", event, guild)

        elif EVENT == "GUILD_SCHEDULED_EVENT_DELETE":
            event = GuildScheduledEvent(conn=self.http, **DATA)
            guild = self.get_guild(event.guild_id)

            event = guild.scheduled_events.pop(event.id, event)

            self.dispatch("guild_scheduled_event_delete", event, guild)
    
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
            channel = self.INTERNAL_STORAGE["channels"].pop(int(DATA["id"]), None)
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
            self.awaiting_voice_connections.update(
                {DATA["guild_id"]: (DATA["session_id"], DATA["channel_id"])}
            )

            m = Member(
                conn=self.http,
                guild_id=DATA["guild_id"],
                voice_state=DATA,
                **DATA["member"],
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
            session_id, channel_id = self.awaiting_voice_connections.pop(
                DATA["guild_id"], None
            )

            if not session_id:
                continue
            data["d"]["session_id"] = session_id
            data["d"]["user_id"] = self.user.id

            vc = VoiceConnection(data, self.loop, self, channel_id)
            self.voice_connections.update({DATA["guild_id"]: vc})

            # Handled by default handler in Client.on_voice_server_update
            self.dispatch("voice_server_update", vc)
