from tg_companion.tgclient import client
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.tl.types import ChannelParticipantsKicked
from telethon.tl.types import ChannelParticipantsBanned


BAN_HELP = """
    **Ban a user from your chat.**
        __Usage:__
            Reply to or mention a user to ban him.
"""
UNBAN_HELP = """
    **Unban a user from your chat.**
        __Usage:__
            Reply to or mention a banned user to unban him.
"""

MUTE_HELP = """
    **Mute a user from your chat.**
        __Usage:__
            Reply to or mention a user to mute him.
"""

UNMUTE_HELP = """
    **Unmute a user from your chat.**
        __Usage:__
            Reply to or mention a mutes user to unmute him.
"""

@client.CommandHandler(outgoing=True, command="ban", help=BAN_HELP)
@client.log_exception
async def ban_user(event):
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await event.edit("You don't have permission to ban users here")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await event.reply("`You don't seem to be referring to a user.`")
                return
        else:
            await event.edit(BAN_HELP)
            return

        if user.id == me.id:
            await event.edit("`You can't ban yourself`")
            return
        query = user.username if user.username else user.first_name
        banned = await client.get_participants(chat, filter=ChannelParticipantsKicked(query))
        if banned:
            await event.edit("This user is already banned")
            return
        await client(EditBannedRequest(chat.id, user, ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
        )))
        await event.edit(f"`Succesfully banned {user.first_name}`")
    else:
        await event.edit("You need admin permissions to ban users here")

@client.CommandHandler(outgoing=True, command="unban", help=UNBAN_HELP)
@client.log_exception
async def ban_user(event):
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await event.edit("You don't have permission to ban users here")
                return

        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await event.reply("`You don't seem to be referring to a user.`")
                return
        else:
            await event.edit(UNBAN_HELP)
            return

        if user.id == me.id:
            await event.edit("`You can't ban yourself`")
            return

        query = user.username if user.username else user.first_name
        banned = await client.get_participants(chat, filter=ChannelParticipantsKicked(query))
        if not banned:
            await event.edit("This user is not banned yet")
            return

        await client(EditBannedRequest(chat, user, ChatBannedRights(
                    until_date=None,
                    view_messages=None,
                    send_messages=None,
                    send_media=None,
                    send_stickers=None,
                    send_gifs=None,
                    send_games=None,
                    send_inline=None,
                    embed_links=None
        )))
        await event.edit(f"`Succesfully unbanned {user.first_name}`")
    else:
        await event.edit("You need admin permissions to ban users here")


@client.CommandHandler(outgoing=True, command="mute", help=MUTE_HELP)
@client.log_exception
async def mute_user(event):
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await event.edit("You don't have permission to mute users here")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await event.reply("`You don't seem to be referring to a user.`")
                return
        else:
            await event.edit(MUTE_HELP)
            return

        if user.id == me.id:
            await event.edit("`You can't mute yourself`")
            return
        query = user.username if user.username else user.first_name
        muted = await client.get_participants(chat, filter=ChannelParticipantsBanned(query))
        if muted:
            await event.edit("This user is already muted")
            return

        await client(EditBannedRequest(chat.id, user, ChatBannedRights(
                    until_date=None,
                    view_messages=None,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
        )))
        await event.edit(f"`Succesfully muted {user.first_name}`")
    else:
        await event.edit("You need admin permissions to mute users here")

@client.CommandHandler(outgoing=True, command="unmute", help=UNMUTE_HELP)
@client.log_exception
async def unmute_user(event):
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await event.edit("You don't have permission to unmute users here")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await event.reply("`You don't seem to be referring to a user.`")
                return
        else:
            await event.edit(UNMUTE_HELP)
            return

        if user.id == me.id:
            await event.edit("`You can't unmute yourself`")
            return
        query = user.username if user.username else user.first_name
        muted = await client.get_participants(chat, filter=ChannelParticipantsBanned(query))
        if not muted:
            await event.edit("This user is not muted")
            return

        await client(EditBannedRequest(chat.id, user, ChatBannedRights(
                    until_date=None,
                    view_messages=None,
                    send_messages=None,
                    send_media=None,
                    send_stickers=None,
                    send_gifs=None,
                    send_games=None,
                    send_inline=None,
                    embed_links=None
        )))
        await event.edit(f"`Succesfully unmuted {user.first_name}`")
    else:
        await event.edit("You need admin permissions to unmute users here")
