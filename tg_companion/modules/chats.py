import io
import os
import re

from telethon import errors, events
from telethon.tl.functions.channels import UpdateUsernameRequest
from telethon.tl.functions.messages import (EditChatAboutRequest,
                                            EditChatPhotoRequest,
                                            EditChatTitleRequest)
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from tg_companion.tgclient import client


CPIC_HELP = """
    **Change your channel/group profile picture.**
        __Usage:__
            __Reply to any image or photo document.__
"""

CABOUT_HELP = """
    **Change your channel/group bio.**
        __Args:__
            `<bio>`
"""

CUNAME_HELP = """
    **Change your channel/group username.**
        __Args:__
            `<username>`
"""

CNAME_HELP = """
    **Change your channel/group name.**
        __Args:__
            `<name>` - __Use \\n to separate first name from second name__
"""


@client.CommandHandler(outgoing=True, command="cpic", help=CPIC_HELP)
@client.log_exception
async def update_profile_pic(event):
    if event.reply:
        message = await event.get_reply_message()
        chat = await event.get_chat()
        photo = None
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                await event.edit("`DOWNLOADING`")
                photo = await client.download_media(message.photo)

            elif isinstance(message.media, MessageMediaDocument):
                mime_type = message.media.document.mime_type.split("/")
                media_type = mime_type[0]
                media_ext = mime_type[1]

                if media_type == "image":
                    await event.edit("`DOWNLOADING`")
                    photo = await client.download_file(message.media.document)
                    photo = io.BytesIO(photo)
                    photo.name = "image." + media_ext

            else:
                await event.edit("`The type of this media entity is invalid.`")

        if photo:
            await event.edit("`UPLOADING`")
            file = await client.upload_file(photo)
            try:
                await client(EditChatPhotoRequest(chat.id, file))
                await event.edit("`Channel picture changed`")

            except Exception as exc:
                if isinstance(exc, errors.ChatAdminRequiredError):
                    await event.edit("`Chat admin privileges are required to do that`")

                if isinstance(exc, errors.PhotoInvalidError):
                    await event.edit("`The selected photo is invalid`")

            if isinstance(photo, str):
                os.remove(photo)


@client.CommandHandler(outgoing=True, command="cabout", help=CABOUT_HELP)
async def update_profile_bio(event):

    split_text = event.text.split(None, 1)
    print(split_text)
    return
    if len(split_text) == 1:
        await event.edit(CABOUT_HELP)
        return

    about = split_text[1]
    chat = await event.get_chat()


    if len(about) > 255:
        await event.edit("`Channel about is too long.`")

    else:
        try:
            await client(EditChatAboutRequest(chat.id, about))
            await event.edit("`Succesfully changed chat about`")

        except Exception as exc:
            if isinstance(exc, errors.ChatAboutNotModifiedError):
                await event.edit("`About text has not changed.`")

            if isinstance(exc, errors.ChatAdminRequiredError):
                await event.edit("`Chat admin privileges are required to do that`")

            if isinstance(exc, errors.ChatNotModifiedError):
                await event.edit("`The chat wasn't modified`")


@client.CommandHandler(outgoing=True, command="cuname (.+)", help=CUNAME_HELP)
@client.log_exception
async def change_profile_username(event):
    username = event.pattern_match.group(1)
    chat = await event.get_chat()

    if "@" in username:
        username = username[1:]

    allowed_char = re.match(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", username)

    if not allowed_char:
        await event.edit("`Invalid Username`")

    elif len(username) > 30:
        await event.edit("`Channel username is too long.`")

    elif len(username) < 5:
        await event.edit("`Channel username is too short`")

    else:
        try:
            await client(UpdateUsernameRequest(chat.id, username))
            await event.edit("`Succesfully changed channel username`")

        except Exception as exc:
            if isinstance(exc, errors.AdminsTooMuchError):
                await event.edit(
                    "`You're admin of too many public channels, make some channels private to change the username of this channel.`"
                )

            if isinstance(exc, errors.ChatAdminRequiredError):
                await event.edit("Chat admin privileges are required to do that")

            if isinstance(exc, errors.UsernameOccupiedError):
                await event.edit(f"`{username} is already taken`")

            if isinstance(exc, errors.ChatNotModifiedError):
                await event.edit("`The chat or channel wasn't modified`")


@client.CommandHandler(outgoing=True, command="cname (.+)", help=CNAME_HELP)
@client.log_exception
async def change_profile_name(event):
    split_text = event.text.split(None, 1)

    if len(split_text) == 0:
        await event.edit(CNAME_HELP)
        return

    title = split_text[1]
    chat = await event.get_chat()
    try:
        await client(EditChatTitleRequest(chat.id, title))
        await event.edit("`Succesfully changed channel/chat title`")

    except Exception as exc:
        if isinstance(exc, errors.ChatAdminRequiredError):
            await event.edit("`Chat admin privileges are required to do that`")

        if isinstance(exc, errors.ChatNotModifiedError):
            await event.edit("`The chat or channel wasn't modified`")
