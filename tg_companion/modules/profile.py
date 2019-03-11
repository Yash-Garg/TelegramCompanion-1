import io
import os
import re

from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon.tl.functions.account import (UpdateProfileRequest,
                                           UpdateUsernameRequest)
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="ppic")
async def update_profile_pic(event):
    """
    **Changes your profile picture.**
        __Usage:__
            __Reply to any image or photo document.__
    """
    if not event.reply_to_msg_id:
        await client.update_message(event, update_profile_pic.__doc__)
        return
    message = await event.get_reply_message()
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
            await client(UploadProfilePhotoRequest(file))
            await client.update_message(event, "`My profile picture was succesfully changed`")

        except Exception as exc:
            if isinstance(exc, PhotoCropSizeSmallError):
                await client.update_message(event, "`The image is too small`")
            if isinstance(exc, ImageProcessFailedError):
                await client.update_message(event, "`Failure while processing the image`")

        if isinstance(photo, str):
            os.remove(photo)


@client.CommandHandler(outgoing=True, command="pbio")
async def update_profile_bio(event):
    """
    **Changes your bio.**
        __Args:__
            `<bio>`
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, update_profile_bio.__doc__)
        return

    bio = split_text[1]

    if len(bio) > 70:
        await client.update_message(event, "`The specified bio is too long.`")
    else:
        await client(UpdateProfileRequest(about=bio))
        await client.update_message(event, "`Succesfully changed my profile bio`")


@client.CommandHandler(outgoing=True, command="puname")
async def change_profile_username(event):
    """
   **Change your username.**
       __Args:__
           `<username>`
   """

    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, change_profile_username.__doc__)
        return

    username = split_text[1]

    if "@" in username:
        username = username[1:]

    allowed_char = re.match(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", username)

    if not allowed_char:
        await client.update_message(event, "`Invalid Username`")

    elif len(username) > 30:
        await client.update_message(event, "`The specified username is too long.`")

    elif len(username) < 5:
        await client.update_message(event, "`The specified username is too short.`")

    else:
        try:
            await client(UpdateUsernameRequest(username))
            await client.update_message(event, "`Succesfully changed my profile username`")

        except UsernameOccupiedError:
            await client.update_message(event, f"`{username} is already taken`")


@client.CommandHandler(outgoing=True, command="pname")
async def change_profile_name(event):
    """
    **Change your name.**
        __Args:__
            `<name>` - __Use \\n to separate first name from second name__
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, change_profile_name.__doc__)
        return

    name = split_text[1]
    firstName = name.split("\\n", 1)[0]
    lastName = " "

    if "\\n" in name:
        lastName = name.split("\\n", 1)[1]

    await client(UpdateProfileRequest(first_name=firstName, last_name=lastName))
    await client.update_message(event, "`Succesfully changed my profile name`")
