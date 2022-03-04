import asyncio
import datetime
import time
import logging
from aiohttp import WSMsgType

from acord.core.decoders import decodeResponse
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


def get_command(client, name: str, type):
    udac = client.application_commands.get(name)

    if udac is not None:
        if isinstance(udac, list):
            # Use this to find command
            for i in udac:
                if i.type == type:
                    udac = i
                    break

    return udac


async def exec_handler(handler, interaction, option):
    _, dev_handle, on_error = handler.__autocomplete__
    
    try:
        return await handler(interaction, option), dev_handle
    except Exception as exc:
        try:
            await on_error(
                interaction,
                (type(exc), exc, exc.__traceback__)
            )
        except Exception:
            logger.error("Failed to trigger on_error for autocomplete", exc_info=1)
    
    return None, None

class Empty:
    def dict(client):
        return {}


def close_code_handler(code: int) -> None:
    if code == gateway.UNKNOWN:
        logger.info("An unknown error has occurred, resuming")
    elif code == gateway.UNKNOWN_OP:
        logger.info("An unknown gateway OP was sent, resuming")
    elif code == gateway.DECODE_ERROR:
        logger.info("An incorrect payload was sent, resuming")
    elif code == gateway.FORBIDDEN:
        logger.info("A payload was sent before identifying, resuming")
    elif code == gateway.AUTH_FAILED:
        raise GatewayError("Incorrect token sent whilst identifying")
    elif code == gateway.AUTH_COMPLETED:
        logger.info("Another identity packet was sent, resuming")
    elif code == gateway.FAILED_SEQUENCE:
        logger.info("An incorrect sequence was sent during resume, resetting sequence")
        return "sequence"
    elif code == gateway.RATELIMIT:
        logger.info("Too many payloads were sent, slow down, resuming")
    elif code == gateway.SESSION_TIMED_OUT:
        logger.info("Session timed out! Recreating new session.")
    elif code == gateway.INVALID_SHARD:
        raise GatewayError("An invalid shard was sent")
    elif code == gateway.SHARD_REQUIRED:
        raise GatewayError("Your client has too many guilds, enable sharding to continue!")
    elif code == gateway.INVALID_GATEWAY_VER:
        raise GatewayError("Looks like the gateway version is incorrect, don't mess with acord.core.abc!")
    elif code == gateway.INVALID_INTENTS:
        raise GatewayError("Invalid intent sent, check what you sent")
    elif code == gateway.DISALLOWED_INTENT:
        raise GatewayError("You have requested an intent you dont have access to")


async def handle_websocket(shard):
    _ = "err"
    # define err here just in case an error occurred 

    try:
        _ = await _handle_websocket(shard)
    except Exception:
        raise
    finally:
        if _ != "err":
            logger.info(f"Connection closed for shard {shard.shard_id}")
        # We want to let the user know the connection closed if no error occurred during the handling


async def _handle_websocket(shard):
    UNAVAILABLE = dict()

    ws = shard.ws
    client = shard.client

    while True:
        message = await ws.receive()

        if message.type in CLOSE_CODES:
            # Connection lost!
            logger.info(f"Websocket connection has been closed, resuming if possible : code={message.data}")
            
            _ = close_code_handler(message.data)

            if _ == "sequence":
                shard.sequence = None

            # Re-prep ws for next iter
            ws = await shard.resume(restart=True)

            logger.debug("Resuming completed")

            continue

        if client.dispatch_on_recv:
            client.dispatch("socket_receive", message)


        data = decodeResponse(message.data)

        EVENT = data["t"]
        OPERATION = data["op"]
        DATA = data["d"]

        SEQUENCE = data["s"]

        if SEQUENCE is not None:
            shard.sequence = SEQUENCE

        if OPERATION == gateway.INVALIDSESSION:

            if shard.resuming:
                await shard.send_identity(
                    client.token, client.intents,
                    client.presence
                )

                shard.resuming = False
            
            else:
                logger.error("Gateway refused connection due to an invalid session")

                # Skip error handling here and handle during close
                continue

        elif OPERATION == gateway.RESUME:
            client.dispatch("resume")

        elif OPERATION == gateway.HEARTBEAT:
            shard._keep_alive.send_heartbeat()
            logger.debug("Server requested heartbeat has been sent")

        elif OPERATION == gateway.HEARTBEATACK:
            shard._keep_alive.ack()
            client.dispatch("heartbeat", shard._keep_alive.latency)

        elif EVENT == "READY":
            client.dispatch("ready")

            shard.session_id = DATA["session_id"]
            shard.gateway_version = DATA["v"]
            client.user = User(conn=client.http, **DATA["user"])

            UNAVAILABLE = {i["id"]: i["unavailable"] for i in DATA["guilds"]}
            client.cache.add_user(client.user)

            shard.ready_event.set()

        # NOTE: Interactions

        elif EVENT == "INTERACTION_CREATE":
            data = Interaction(conn=client.http, **DATA)

            if data.type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                udac = get_command(client, data.data.name, data.data.type)

                if not udac:
                    continue

                # Command is a slash command so were good with __pre_calls__
                handlers = udac.__pre_calls__.get("__autocompleters__")

                if not handlers:
                    udac.auto_complete_handlers()
                    # Should be defined now
                    handlers = udac.__pre_calls__["__autocompleters__"]

                d = []

                for option in data.data.options:
                    if not option.focused:
                        continue
                    handler = handlers.get("*", handlers.get(option.name))

                    if not handler:
                        continue
                    result, dev_handled = await exec_handler(handler, data, option)

                    if dev_handled or not result:
                        continue

                    if isinstance(result, list):
                        d.extend(result)
                    else:
                        d.append(result)

                await data.respond_to_autocomplete(d)


            elif data.type == InteractionType.APPLICATION_COMMAND:
                udac = get_command(client, data.data.name, data.data.type)

                if not udac:
                    continue

                args, kwds = (), {}
                if data.data.type == ApplicationCommandType.CHAT_INPUT:
                    kwds = get_slash_options(data)
                elif data.data.type == ApplicationCommandType.MESSAGE:
                    message = client.get_message(data.channel_id, data.data.target_id)
                    if not message:
                        message = data.data.target_id
                    args = (message,)
                else:
                    user = client.get_user(data.data.target_id)
                    if not user:
                        user = data.data.target_id
                    args = (user,)

                fut = client.loop.create_future()
                client.loop.create_task(
                    udac.dispatcher(data, fut, *args, **kwds),
                    name=f"app_cmd dispatcher : {udac.name}",
                )

                possible_exc = await asyncio.wait_for(fut, None)
                if isinstance(possible_exc, Exception):
                    client.on_error(f"app_cmd dispatcher : {udac.name}")

            client.dispatch("interaction_create", data)

        elif EVENT == "INTERACTION_UPDATE":
            data = Interaction(conn=client.http, **DATA)

            client.dispatch("interaction_update", data)

        elif EVENT == "INTERACTION_DELETE":
            try:
                id, guild_id, application_id = DATA.values()
            except ValueError:
                id, guild_id, application_id = DATA.values(), None

            client.dispatch("interaction_delete", id, guild_id, application_id)

        # NOTE: Messages

        elif EVENT == "MESSAGE_CREATE":
            message = Message(conn=client.http, **DATA)

            try:
                if hasattr(message.channel, "last_message_id"):
                    message.channel.last_message_id = message.id
            except ValueError:
                pass

            client.cache.add_message(message)

            client.dispatch("message_create", message)

        elif EVENT == "MESSAGE_UPDATE":
            pre_existing: Message = client.get_message(int(DATA["channel_id"]), int(DATA["id"]))
            if not pre_existing:
                client.dispatch("partial_message_update", DATA)
                continue

            message = pre_existing.copy(update=DATA)
            client.cache.add_message(message)

            client.dispatch("message_update", message)

        elif EVENT == "MESSAGE_DELETE":
            message = client.cache.remove_message(int(DATA["channel_id"]), int(DATA["id"]), None)
            if message:
                client.dispatch("message_delete", message)
            else:
                client.dispatch("partial_message_delete",
                    Snowflake(DATA["channel_id"]),
                    Snowflake(DATA["id"]),
                    Snowflake(DATA["guild_id"]) if DATA["guild_id"] is not None else None
                )

        elif EVENT == "MESSAGE_DELETE_BULK":
            messages = [
                (
                    client.cache.remove_message(int(DATA["channel_id"]), int(DATA["id"]), None)
                    or Snowflake(id)
                )
                for id in DATA["ids"]
            ]

            client.dispatch("bulk_message_delete", 
                messages, 
                Snowflake(DATA["channel_id"]),
                Snowflake(DATA["guild_id"]) if DATA["guild_id"] is not None else None
            )

        elif EVENT == "MESSAGE_REACTION_ADD":
            reaction = MessageReaction(**DATA)

            message = client.get_message(reaction.channel_id, reaction.message_id)
            if message is not None:
                if reaction.emoji not in message.reactions:
                    message.reactions[reaction.emoji] = [reaction]
                else:
                    message.reactions[reaction.emoji].append(reaction)

        elif EVENT == "CHANNEL_PINS_UPDATE":
            channel = client.get_channel(int(DATA["channel_id"]))
            ts = datetime.datetime.fromisoformat(DATA["last_pin_timestamp"])

            client.dispatch("message_pin", channel, ts)

        # NOTE: invites
        elif EVENT == "INVITE_CREATE":
            invite = Invite(conn=client.http, **DATA)
            client.dispatch("invite_create", invite)

        elif EVENT == "INVITE_DELETE":
            channel_id = DATA["channel_id"]
            guild_id = DATA.get("guild_id", 0)
            code = DATA["code"]

            channel = client.get_channel(channel_id) or Snowflake(channel_id)
            guild = client.get_guild(guild_id) or (
                Snowflake(guild_id) if guild_id is not None else None
            )

            client.dispatch("invite_delete", channel, guild, code)

        # NOTE: Guilds

        elif EVENT == "GUILD_CREATE":
            guild = Guild(conn=client.http, **DATA)

            if DATA["id"] in UNAVAILABLE:
                UNAVAILABLE.pop(DATA["id"])
                client.dispatch("guild_recv", guild)
            else:
                client.dispatch("guild_create", guild)

            client.cache.add_guild(guild)

        elif EVENT == "GUILD_DELETE":
            if DATA.get("unavailable", None) is not None:
                guild = Guild(conn=client.http, **DATA)
                UNAVAILABLE.pop(DATA["id"])
                client.dispatch("guild_outage", guild)

                client.cache.add_guild(guild)
            else:
                guild = client.cache.remove_guild(int(DATA["id"]), None)
                client.dispatch("guild_remove", guild)

        elif EVENT == "GUILD_UPDATE":
            guild = Guild(conn=client.http, **DATA)

            client.cache.add_guild(guild)
            client.dispatch("guild_update", guild)

        elif EVENT == "GUILD_BAN_ADD":
            guild = client.get_guild(int(DATA["guild_id"]))
            user = User(conn=client.http, **DATA["user"])

            guild.members.pop(user.id, None)
            
            client.cache.add_user(user)
            client.dispatch("guild_ban", guild, user)

        elif EVENT == "GUILD_BAN_REMOVE":
            guild = client.get_guild(int(DATA["guild_id"]))
            user = User(conn=client.http, **DATA["user"])

            client.cache.add_user(user)
            client.dispatch("guild_ban_remove", guild, user)

        elif EVENT == "GUILD_EMOJIS_UPDATE":
            guild = client.get_guild(int(DATA["guild_id"]))
            emojis = DATA["emojis"]
            bulk = list()

            for emoji in emojis:
                e = Emoji(conn=client.http, guild_id=guild.id, **emoji)
                guild.emojis.update({e.id: e})
                bulk.append(e)

                client.dispatch("guild_emoji_update", e)

            client.dispatch("guild_emojis_update", bulk)

        elif EVENT == "GUILD_STICKERS_UPDATE":
            guild = client.get_guild(int(DATA["guild_id"]))
            stickers = DATA["stickers"]
            bulk = list()

            for sticker in stickers:
                s = Sticker(conn=client.http, guild_id=guild.id, **sticker)
                guild.stickers.update({s.id: s})
                bulk.append(s)

                client.dispatch("guild_sticker_update", s)

            client.dispatch("guild_stickers_update", bulk)

        elif EVENT == "GUILD_INTEGRATIONS_UPDATE":
            guild = client.get_guild(int(DATA["guild_id"]))
            if guild is None:
                guild = Snowflake(DATA["guild_id"])
            client.dispatch("guild_integrations_update", guild)

        elif EVENT == "GUILD_MEMBER_ADD":
            member = Member(conn=client.http, **DATA)
            guild = client.get_guild(member.guild_id)

            if guild is not None:
                guild.members.update({member.user.id: member})
            else:
                guild = Snowflake(DATA["guild_id"])

            client.dispatch("member_join", member, guild)

        elif EVENT == "GUILD_MEMBER_REMOVE":
            guild = client.get_guild(int(DATA["guild_id"]))
            user = User(conn=client.http, **DATA["user"])
            
            if guild is not None:
                user = guild.members.pop(user.id, user)
            else:
                guild = Snowflake(DATA["guild_id"])

            client.dispatch("member_remove", user, guild)

        elif EVENT == "GUILD_MEMBER_UPDATE":
            guild = client.get_guild(int(DATA["guild_id"]))

            if guild is None:
                client.dispatch("u_member_update", DATA)
                continue

            b_member = guild.get_member(int(DATA["user"]["id"]))
            if not b_member:
                b_member = await guild.fetch_member(int(DATA["user"]["id"]))
            a_member = b_member.copy(update=DATA)
            
            client.dispatch("member_update", b_member, a_member, guild)

        elif EVENT == "GUILD_ROLE_CREATE":
            guild = client.get_guild(int(DATA["guild_id"]))
            role = Role(conn=client.http, **(DATA["role"]))

            guild.roles.update({role.id: role})

            client.dispatch("role_create", role, guild)

        elif EVENT == "GUILD_ROLE_UPDATE":
            guild = client.get_guild(int(DATA["guild_id"]))
            a_role = Role(conn=client.http, **(DATA["role"]))
            b_role = guild.roles.get(a_role.id)

            guild.roles.update({role.id: role})

            client.dispatch("role_update", a_role, b_role, guild)

        elif EVENT == "GUILD_ROLE_DELETE":
            guild = client.get_guild(int(DATA["guild_id"]))
            role = guild.roles.get(Snowflake(DATA["role_id"]))

            client.dispatch("role_delete", role, guild)

        # NOTE: Guild scheduled events

        elif EVENT == "GUILD_SCHEDULED_EVENT_CREATE":
            event = GuildScheduledEvent(conn=client.http, **DATA)
            guild = client.get_guild(event.guild_id)
            guild.guild_scheduled_events.update({event.id: event})

            client.dispatch("guild_scheduled_event_create", event, guild)

        elif EVENT == "GUILD_SCHEDULED_EVENT_UPDATE":
            event = GuildScheduledEvent(conn=client.http, **DATA)
            guild = client.get_guild(event.guild_id)
            guild.guild_scheduled_events.update({event.id: event})

            client.dispatch("guild_scheduled_event_update", event, guild)

        elif EVENT == "GUILD_SCHEDULED_EVENT_DELETE":
            event = GuildScheduledEvent(conn=client.http, **DATA)
            guild = client.get_guild(event.guild_id)

            event = guild.scheduled_events.pop(event.id, event)

            client.dispatch("guild_scheduled_event_delete", event, guild)

        # NOTE: Integrations

        elif EVENT == "ON_INTEGRATION_CREATE":
            d = Integration(conn=client.http, **DATA)

            client.dispatch("guild_integration_create", d.guild_id, d)

        elif EVENT == "ON_INTEGRATION_UPDATE":
            d = Integration(conn=client.http, **DATA)

            client.dispatch("guild_integration_update", d.guild_id, d)

        elif EVENT == "ON_INTEGRATION_DELETE":
            integration_id = Snowflake(DATA["id"])
            guild_id = Snowflake(DATA["guild_id"])
            
            if (application_id := DATA.pop("application_id", None)):
                application_id = Snowflake(application_id)

            client.dispatch(
                "guild_integration_delete",
                integration_id,
                guild_id,
                application_id
            )

        # NOTE: Invites

        elif EVENT == "ON_INVITE_CREATE":
            inv = Invite(conn=client.http, **DATA)

            client.dispatch("invite_create", inv)

        elif EVENT == "ON_INVITE_DELETE":
            channel_id = Snowflake(DATA["channel_id"])
            code = DATA["code"]
            
            if guild_id := DATA.pop("guild_id", None):
                guild_id = Snowflake(guild_id)

            client.dispatch(
                "invite_delete",
                code,
                channel_id,
                guild_id
            )
    
        # NOTE: channels

        elif EVENT == "CHANNEL_CREATE":
            channel, _ = _d_to_channel(DATA, client.http)

            client.cache.add_channel(channel)
            client.dispatch("channel_create", channel)

        elif EVENT == "CHANNEL_UPDATE":
            channel, _ = _d_to_channel(DATA, client.http)

            client.cache.add_channel(channel)
            client.dispatch("channel_update", channel)

        elif EVENT == "CHANNEL_DELETE":
            channel = client.cache.remove_channel(channel.id, None)
            client.dispatch("channel_delete", channel)

        # NOTE: threads

        elif EVENT == "THREAD_CREATE":
            thread = Thread(conn=client.http, **DATA)
            client.cache.add_channel(thread)

            guild = client.get_guild(thread.guild_id)
            guild.threads.update({thread.id: thread})

            client.dispatch("thread_create", thread)

        elif EVENT == "THREAD_UPDATE":
            thread = Thread(conn=client.http, **DATA)
            client.cache.add_channel(thread)

            guild = client.get_guild(thread.guild_id)
            guild.threads.update({thread.id: thread})

            client.dispatch("thread_update", thread)

        elif EVENT == "THREAD_DELETE":
            guild = client.get_guild(int(DATA["guild_id"]))
            thread = guild.threads.pop(int(DATA["id"]), None)
            client.cache.remove_channel(int(DATA["id"]), None)

            client.dispatch("thread_delete")

        elif EVENT == "THREAD_SYNC_LIST":
            guild = client.get_guild(int(DATA["guild_id"]))
            threads = list()

            for thread in DATA["threads"]:
                tr = Thread(conn=client.http, **thread)
                threads.append(tr)

                guild.threads.update({tr.id: tr})
                client.cache.add_channel(tr)

            client.dispatch("thread_sync", threads)

        elif EVENT == "THREAD_MEMBER_UPDATE":
            guild = client.get_guild(int(DATA.pop("guild_id")))
            member = ThreadMember(**DATA)

            guild.threads[member.id].members.update({member.user_id: member})

            client.dispatch("thread_member_update", member)

        elif EVENT == "THREAD_MEMBERS_UPDATE":
            guild = client.get_guild(int(DATA.pop("guild_id")))
            thread = guild.threads[int(DATA.pop("id"))]

            thread.member_count = DATA["member_count"]

            for member in DATA["added_members"]:
                trm = ThreadMember(**member)
                thread.members.update({trm.id: trm})

            for member in DATA["removed_member_ids"]:
                thread.members.pop(int(member), None)
                # Not all members may be in the thread

            client.dispatch("thread_members_update", thread)

        elif EVENT == "VOICE_STATE_UPDATE":
            client.awaiting_voice_connections.update(
                {DATA["guild_id"]: (DATA["session_id"], DATA["channel_id"])}
            )

            m = Member(
                conn=client.http,
                guild_id=DATA["guild_id"],
                voice_state=DATA,
                **DATA["member"],
            )

            if m.user.id == client.user.id:
                # call manual disconnect if OP 13 has not already been recieved
                conn = client.voice_connections.pop(DATA["guild_id"], None)
                if conn is not None:
                    await conn.disconnect()

            guild = client.cache.get_guild(m.guild_id)

            if not guild:
                continue

            guild.members.update({m.user.id: m})
            channel_id = DATA["channel_id"]

            client.dispatch("voice_state_update", channel_id, m)

        # NOTE: VOICE EVENTS

        elif EVENT == "VOICE_SERVER_UPDATE":
            session_id, channel_id = client.awaiting_voice_connections.pop(
                DATA["guild_id"], None
            )

            if not session_id:
                continue
            data["d"]["session_id"] = session_id
            data["d"]["user_id"] = client.user.id

            vc = VoiceConnection(data, client.loop, client, channel_id)
            client.voice_connections.update({DATA["guild_id"]: vc})

            # Handled by default handler in Client.on_voice_server_update
            client.dispatch("voice_server_update", vc)
