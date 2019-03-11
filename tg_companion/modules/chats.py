import io
import os
import re

from telethon import errors
from telethon.tl.functions.channels import UpdateUsernameRequest
from telethon.tl.functions.messages import (EditChatAboutRequest,
                                            EditChatPhotoRequest,
                                            EditChatTitleRequest)
from telethon.tl.functions.channels import EditPhotoRequest, EditTitleRequest

from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, InputChannel

from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="cpic")
async def update_profile_pic(event):
    """
    **Change your channel/group profile picture.**
        __Usage:__
            Reply to any image or photo document.
    """
    if event.is_private:
        await client.update_message(event, "Invalid chat type")
        return
    if event.reply:
        message = await event.get_reply_message()
        chat = await event.get_chat()
        if not await client.is_user_admin(chat):
            await client.update_message(event, "`Chat admin privileges are required change chat photo`")
            return
        photo = None
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                await client.update_message(event, "`DOWNLOADING`")
                photo = await client.download_media(message.photo)

            elif isinstance(message.media, MessageMediaDocument):
                mime_type = message.media.document.mime_type.split("/")
                media_type = mime_type[0]
                media_ext = mime_type[1]

                if media_type == "image":
                    await client.update_message(event, "`DOWNLOADING`")
                    photo = await client.download_file(message.media.document)
                    photo = io.BytesIO(photo)
                    photo.name = "image." + media_ext

            else:
                await client.update_message(event, "`The type of this media entity is invalid.`")

        if photo:
            await client.update_message(event, "`UPLOADING`")
            file = await client.upload_file(photo)
            try:
                if chat.megagroup:
                    await client(EditPhotoRequest((chat.id), file))
                else:
                    await client(EditChatPhotoRequest((chat.id), file))
                await client.update_message(event, "`Chat picture changed`")

            except Exception as exc:
                if isinstance(exc, errors.PhotoInvalidError):
                    await client.update_message(event, "`The selected photo is invalid`")
                else:
                    raise

            if isinstance(photo, str):
                os.remove(photo)


@client.CommandHandler(outgoing=True, command="cabout")
async def update_profile_bio(event):
    """
    **Change your channel/group bio.**
        __Args:__
            `<bio>` - The about text you want to use for your profile.
    """
    if event.is_private:
        await client.update_message(event, "Invalid chat type")
        return

    split_text = event.text.split(None, 1)
    print(split_text)
    return
    if len(split_text) == 1:
        await client.update_message(event, update_profile_bio.__doc__)
        return

    about = split_text[1]
    chat = await event.get_chat()

    if not await client.is_user_admin(chat):
        await client.update_message(event, "`Chat admin privileges are required to change this chat about`")
        return

    if len(about) > 255:
        await client.update_message(event, "`Chat about is too long.`")

    else:
        try:
            await client(EditChatAboutRequest(chat.id, about))
            await client.update_message(event, "`Succesfully changed chat about`")

        except Exception as exc:
            if isinstance(exc, errors.ChatAboutNotModifiedError):
                await client.update_message(event, "`About text has not changed.`")

            if isinstance(exc, errors.ChatNotModifiedError):
                await client.update_message(event, "`The chat wasn't modified`")


@client.CommandHandler(outgoing=True, command="cuname (.+)")
async def change_profile_username(event):
    """
    **Change your channel/group username.**
        __Args:__
            `<name>` -The username you want to use for your chat.
    """

    if event.is_private:
        await client.update_message(event, "Invalid chat type")
        return
    username = event.pattern_match.group(1)
    chat = await event.get_chat()

    if not await client.is_user_admin(chat):
        await client.update_message(event, "`Chat admin privileges are required to change this chat username`")
        return

    if "@" in username:
        username = username[1:]

    allowed_char = re.match(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", username)

    if not allowed_char:
        await client.update_message(event, "`Invalid Username`")

    elif len(username) > 30:
        await client.update_message(event, "`Chat username is too long.`")

    elif len(username) < 5:
        await client.update_message(event, "`Chat username is too short`")

    else:
        try:
            await client(UpdateUsernameRequest(chat.id, username))
            await client.update_message(event, "`Succesfully changed chat username`")

        except Exception as exc:
            if isinstance(exc, errors.AdminsTooMuchError):
                await client.update_message(event,
                                            "`You're admin of too many public channels, make some channels private to change the username of this chat.`"
                                            )

            if isinstance(exc, errors.UsernameOccupiedError):
                await client.update_message(event, f"`{username} is already taken`")

            if isinstance(exc, errors.ChatNotModifiedError):
                await client.update_message(event, "`The chat wasn't modified`")


@client.CommandHandler(outgoing=True, command="cname (.+)")
async def change_profile_name(event):
    """
    **Change your channel/group name.**
        __Args:__
            `<name>` -The name you want to use for your chat.
    """
    if event.is_private:
        await client.update_message(event, "Invalid chat type.")
        return
    split_text = event.text.split(None, 1)

    if len(split_text) == 0:
        await client.update_message(event, change_profile_name.__doc__)
        return

    title = split_text[1]
    chat = await event.get_chat()
    if not await client.is_user_admin(chat):
        await client.update_message(event, "`Chat admin privileges are required to change the chat title`!")
        return
    try:
        if chat.megagroup:
            await client(EditTitleRequest(chat.id, title))
        else:
            await client(EditChatTitleRequest(chat.id, title))
        await client.update_message(event, "`Succesfully changed chat's title`!")

    except Exception as exc:
        if isinstance(exc, errors.ChatNotModifiedError):
            await client.update_message(event, "`The chat or chat wasn't modified`!")
