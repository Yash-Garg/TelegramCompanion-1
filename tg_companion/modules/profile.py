import io
import os
import re

from telethon import events
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon.tl.functions.account import (UpdateProfileRequest,
                                           UpdateUsernameRequest)
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="ppic")
@client.log_exception
async def update_profile_pic(event):
    if event.reply_to_msg_id:
        message = await event.get_reply_message()
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
                await client(UploadProfilePhotoRequest(file))
                await event.edit("`Profile picture changed`")

            except Exception as exc:
                if isinstance(exc, PhotoCropSizeSmallError):
                    await event.edit("`The image is too small`")
                if isinstance(exc, ImageProcessFailedError):
                    await event.edit("`Failure while processing the image`")

            if isinstance(photo, str):
                os.remove(photo)


@client.CommandHandler(outgoing=True, command="^pbio (.+)")
@client.log_exception
async def update_profile_bio(event):
    bio = event.pattern_match.group(1)
    if len(bio) > 70:
        await event.edit("`Your bio is too long.`")
    else:
        await client(UpdateProfileRequest(about=bio))
        await event.edit("`Succesfully changed your bio`")


@client.CommandHandler(outgoing=True, command="puname (.+)")
@client.log_exception
async def change_profile_username(event):
    username = event.pattern_match.group(1)

    if "@" in username:
        username = username[1:]

    allowed_char = re.match(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", username)

    if not allowed_char:
        await event.edit("`Invalid Username`")

    elif len(username) > 30:
        await event.edit("`Your username is too long.`")

    elif len(username) < 5:
        await event.edit("`Your username is too short`")

    else:
        try:
            await client(UpdateUsernameRequest(username))
            await event.edit("`Succesfully changed your username`")

        except UsernameOccupiedError:
            await event.edit(f"`{username} is already taken`")


@client.CommandHandler(outgoing=True, command="pname (.+)")
@client.log_exception
async def change_profile_name(event):
    name = event.pattern_match.group(1)
    firstName = name.split("\\n", 1)[0]
    lastName = " "

    if "\\n" in name:
        lastName = name.split("\\n", 1)[1]

    await client(UpdateProfileRequest(first_name=firstName, last_name=lastName))
    await event.edit("`Succesfully changed your name`")
