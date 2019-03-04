import math
from io import BytesIO

import emoji
from PIL import Image
from telethon.errors.rpcerrorlist import StickersetInvalidError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (DocumentAttributeFilename,
                               InputMediaUploadedDocument,
                               InputStickerSetShortName,
                               MessageMediaPhoto,
                               InputStickerSetID)
from telethon.tl.types import DocumentAttributeSticker

from tg_companion.tgclient import client

KANG_HELP = """
    **Save any image/sticker to a sticker pack**
        __Usage:__
            __Reply to any image or photo document/sticker.__
        __Args:__
            `<emoji>` (**optional**) __The emoji you want to attach to your sticker__
"""

PACKINFO_HELP = """
    **Get sticker pack info**
        __Usage:__
            __Reply to any sticker to get his pack info.__
"""

GET_HELP = """
    **Send a sticker as a PMG document**
        __Usage:__
            __Reply to any sticker to get it as a PMG document.__
"""

@client.CommandHandler(outgoing=True, command="kang", help=KANG_HELP)
async def kang_sticker(event):
    if not event.is_reply:
        await client.update_message(event, KANG_HELP)
        return
    rep_msg = await event.get_reply_message()
    sticker_emoji = "🤔"
    if len(event.text.split()) > 1:
        sticker_emoji = event.text.split()[1]
    if not is_message_image(rep_msg):
        await client.update_message(event, "`Invalid message type`")
        return
    if sticker_emoji not in list(emoji.EMOJI_UNICODE.values()):
        await client.update_message(event, "`Please use a valid emoji`")
        return
    me = await client.get_me()
    user_name = me.username if me.username else me.firstname
    packname = f"{user_name}'s sticker pack"
    packshortname = f"tg_companion_{me.id}"  # format: tg_companion_userid
    await client.update_message(event, "`Processing your sticker. Please Wait!`")
    async with client.conversation('Stickers') as bot_conv:
        file = await client.download_file(rep_msg.media)
        with BytesIO(file) as mem_file, BytesIO() as sticker:
            resize_image(mem_file, sticker)
            sticker.seek(0)
            uploaded_sticker = await client.upload_file(sticker, file_name="sticker.png")
            if not await stickerset_exists(bot_conv, packshortname):
                await bot_conv.send_message("/cancel")
                await bot_conv.get_response()
                await bot_conv.send_message("/newpack")
                response = await bot_conv.get_response()
                if response.text != "Yay! A new stickers pack. How are we going to call it? Please choose a name for your pack.":
                    await client.update_message(event, response.text)
                    return
                await bot_conv.send_message(packname)
                response = await bot_conv.get_response()
                if not response.text.startswith("Alright!"):
                    await client.update_message(event, response.text)
                    return

                await bot_conv.send_file(InputMediaUploadedDocument(file=uploaded_sticker, mime_type='image/png', attributes=[DocumentAttributeFilename("sticker.png")]), force_document=True)
                await bot_conv.get_response()
                await bot_conv.send_message(sticker_emoji)
                response = await bot_conv.get_response()
                await bot_conv.send_message("/publish")
                await bot_conv.get_response()
                await bot_conv.send_message(packshortname)
                response = await bot_conv.get_response()
                if response.text == "Sorry, this short name is already taken.":
                    await client.update_message(event, "There has been an error processing your sticker!")
                    return
            else:
                await bot_conv.send_message("/cancel")
                await bot_conv.get_response()
                await bot_conv.send_message("/addsticker")
                await bot_conv.get_response()
                await bot_conv.send_message(packshortname)
                await bot_conv.send_file(InputMediaUploadedDocument(file=uploaded_sticker, mime_type='image/png', attributes=[DocumentAttributeFilename("sticker.png")]), force_document=True)
                await bot_conv.get_response()
                await bot_conv.send_message(sticker_emoji)
                await bot_conv.get_response()
                await bot_conv.send_message("/done")
    await client.update_message(event, f"sticker added! Your pack can be found [here](https://t.me/addstickers/{packshortname})")


@client.CommandHandler(outgoing=True, command="packinfo", help=PACKINFO_HELP)
async def get_pack_info(event):
    if not event.is_reply:
        await client.update_message(event, PACKINFO_HELP)
        return
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await client.update_message(event, "`Reply to a sticker to get the pack details`")
        return
    stickerset_attr = rep_msg.document.attributes[1]
    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        await client.update_message(event, "`Not a valid sticker`")
        return
    get_stickerset = await client(GetStickerSetRequest(InputStickerSetID(id=stickerset_attr.stickerset.id, access_hash=stickerset_attr.stickerset.access_hash)))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    OUTPUT = f"**Sticker Title:** `{get_stickerset.set.title}\n`" \
             f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n" \
             f"**Official:** `{get_stickerset.set.official}`\n" \
             f"**Archived:** `{get_stickerset.set.archived}`\n" \
             f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n" \
             f"**Emojis In Pack:** {' '.join(pack_emojis)}"
    await client.update_message(event, OUTPUT)


@client.CommandHandler(outgoing=True, command="stickerget", help=GET_HELP)
async def sticker_to_png(event):
    if not event.is_reply:
        await client.update_message(event, GET_HELP)
        return
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await client.update_message(event, "`Reply to a sticker to get the pack details`")
        return
    stickerset_attr = rep_msg.document.attributes[1]
    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        await client.update_message(event, "`Not a valid sticker`")
        return
    chat = await event.get_chat()
    await client.send_file(chat.id, rep_msg.document)
# Helpers


def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False


async def stickerset_exists(conv, setname):
    try:
        await client(GetStickerSetRequest(InputStickerSetShortName(setname)))
        await conv.send_message("/addsticker")
        response = await conv.get_response()
        if response.text == "Invalid pack selected.":
            await conv.send_message("/cancel")
            return False
        await conv.send_message("/cancel")
        return True
    except StickersetInvalidError:
        return False


def resize_image(image, save_locaton):
    """ Copyright Rhyse Simpson:
        https://github.com/skittles9823/SkittBot/blob/master/tg_bot/modules/stickers.py
    """

    im = Image.open(image)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(maxsize)
    im.save(save_locaton, "PNG")
