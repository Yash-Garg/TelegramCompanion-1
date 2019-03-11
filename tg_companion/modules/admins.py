from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import (ChannelParticipantsBanned,
                               ChannelParticipantsKicked, ChatBannedRights)

from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="ban")
async def ban_user(event):
    """
    **Ban a user from your chat.**
        __Usage:__
            Reply to or mention a user to ban him.
    """
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await client.update_message(event, "I don't have permission to ban users here.")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
                return
        else:
            await client.update_message(event, ban_user.__doc__)
            return

        if user.id == me.id:
            await client.update_message(event, "`I can't ban myself`!")
            return
        user_banned = False
        query = user.username if user.username else user.first_name
        banned = await client.get_participants(chat, filter=ChannelParticipantsKicked(query))
        if banned:
            for kicked in banned:
                if user.id == kicked.id:
                    user_banned = True

        if user_banned is True:
            await client.update_message(event, "This user is already banned!")
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
        await client.update_message(event, f"`I succesfully banned {user.first_name}`!")
    else:
        await client.update_message(event, "I need admin permissions to ban users here!")


@client.CommandHandler(outgoing=True, command="unban")
async def unban_user(event):
    """
    **Unban a user from your chat.**
        __Usage:__
            Reply to or mention a banned user to unban him.
    """
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await client.update_message(event, "I don't have permission to ban users here!")
                return

        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
                return
        else:
            await client.update_message(event, unban_user.__doc__)
            return

        if user.id == me.id:
            await client.update_message(event, "`I can't ban myself!`")
            return

        user_banned = False
        query = user.username if user.username else user.first_name
        banned = await client.get_participants(chat, filter=ChannelParticipantsKicked(query))
        if banned:
            for kicked in banned:
                if user.id == kicked.id:
                    user_banned = True

        if user_banned is False:
            await client.update_message(event, "This user is not banned yet.")
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
        await client.update_message(event, f"`Succesfully unbanned {user.first_name}`!")
    else:
        await client.update_message(event, "I need admin permissions to ban users here!")


@client.CommandHandler(outgoing=True, command="mute")
async def mute_user(event):
    """
    **Mute a user from your chat.**
        __Usage:__
            Reply to or mention a user to mute him.
    """
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await client.update_message(event, "I don't have permission to mute users here!")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
                return
        else:
            await client.update_message(event, mute_user.__doc__)
            return

        if user.id == me.id:
            await client.update_message(event, "`I can't mute myself`")
            return
        user_muted = False
        query = user.username if user.username else user.first_name
        muted = await client.get_participants(chat, filter=ChannelParticipantsBanned(query))
        if muted:
            for restricted in muted:
                if user.id == restricted.id:
                    user_muted = True

        if user_muted is True:
            await client.update_message(event, "This user is already muted!")
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
        await client.update_message(event, f"`Succesfully muted {user.first_name}`!")
    else:
        await client.update_message(event, "I need admin permissions to mute users here!")


@client.CommandHandler(outgoing=True, command="unmute")
async def unmute_user(event):
    """
    **Unmute a user from your chat.**
        __Usage:__
            Reply to or mention a mutes user to unmute him.
    """
    chat = await event.get_chat()
    me = await client.get_me()
    split_text = event.text.split(None, 1)

    if chat.creator or chat.admin_rights:
        if chat.admin_rights:
            if not chat.admin_rights.ban_users:
                await client.update_message(event, "I don't have permission to unmute users here!")
        if event.reply_to_msg_id:
            rep_msg = await event.get_reply_message()
            user = await rep_msg.get_sender()

        elif len(split_text) > 1:
            try:
                user = await client.get_entity(split_text[1])
            except Exception:
                await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
                return
        else:
            await client.update_message(event, unmute_user.__doc__)
            return

        if user.id == me.id:
            await client.update_message(event, "`I can't unmute myself!`")
            return
        query = user.username if user.username else user.first_name
        muted = await client.get_participants(chat, filter=ChannelParticipantsBanned(query))
        user_muted = False
        if muted:
            for kicked in user_muted:
                if user.id == kicked.id:
                    user_muted = True

        if user_muted is True:
            await client.update_message(event, "This user is not muted!")
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
        await client.update_message(event, f"`Succesfully unmuted {user.first_name}`!")
    else:
        await client.update_message(event, "I need admin permissions to unmute users here!")
