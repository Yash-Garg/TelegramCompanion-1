import io
import os
import platform
import re
import sys
import time
import datetime
from html import escape

import aiohttp
import telethon
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User, InputPeerNotifySettings

from tg_companion.modules.global_bans import GBANNED_USERS
from tg_companion.modules.rextester.api import UnknownLanguage, rexec
from tg_companion.tgclient import client

from .._version import __version__


@client.CommandHandler(outgoing=True, command="ping")
async def ping(event):
    """
    **Test if the bot is alive and the response time.**
    """

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.google.com"):
            end_time = time.time()
            ping_time = float(end_time - start_time) * 1000
            await client.update_message(event, f"Ping time was: {ping_time}ms.")


@client.CommandHandler(outgoing=True, command="version")
async def version(event):
    """
    **Get your companion version information.**
    """
    bot_version = __version__.public()
    python_version = platform.python_version()
    telethon_version = telethon.__version__

    await client.update_message(event, f"__Companion__ (**{bot_version}**),"
                                f" __Python__ (**{python_version}**),"
                                f" __Telethon__"
                                f" (**{telethon_version}**)")


@client.CommandHandler(outgoing=True, command="info")
async def user_info(event):
    """
    **Get a user's info.**
    """
    message = event.message
    user = await event.get_sender()
    chat = await event.get_chat()

    if event.reply_to_msg_id:
        message = await event.get_reply_message()
        user = await message.get_sender()

    if len(event.text.split()) > 1:
        user = int(event.text.split()[1]) if event.text.split()[
            1].isdigit() else event.text.split()[1]
        user = event.text.split()[1]
        user = int(user) if user.isdigit() else user
        try:
            user = await client.get_entity(user)
        except Exception:
            await client.update_message(event, f"`I don't seem to find this user by {event.text.split()[1]}`.")
            return

        if not isinstance(user, User):
            await event.reply(f"`@{user.username}` is not a User")
            return
        if user.deleted:
            await event.edit("This user has deleted his account. I can't get his info.")
            return

    full_user = await client(GetFullUserRequest(user.id))
    firstName = full_user.user.first_name
    lastName = full_user.user.last_name
    username = full_user.user.username
    user_id = full_user.user.id
    common_chats = full_user.common_chats_count

    REPLY = "<b>User Info:</b>\n"

    if firstName:
        REPLY += f"\nFirst Name: {escape(firstName)}"

    if lastName:
        REPLY += f"\nLast Name: {escape(lastName)}"
    if username:
        REPLY += f"\nUsername: @{escape(username)}"

    REPLY += f"\nUser id: <code>{user_id}</code>"
    REPLY += f"\nPermanent user link: <a href=\"tg://user?id={user_id}\">link</a>"

    if user.id in GBANNED_USERS:
        REPLY += "\n\nThis user is globally banned on this companion!"
        if GBANNED_USERS.get(user.id):
            REPLY += f"\nReason: {escape(GBANNED_USERS.get(user_id))}"
    if full_user.about:
        REPLY += f"\n\n<b>About User:</b>\n{escape(full_user.about)}"
    if not full_user.user.is_self:
        REPLY += f"\n\nI have <code>{common_chats}</code> chats in common with this user."

    await client.send_message(
        chat.id, REPLY, reply_to=message.id, link_preview=False, file=full_user.profile_photo, parse_mode="html"
    )


@client.CommandHandler(outgoing=True, command="rex")
async def rextestercli(event):
    """
    **Execute your code using rextester's API**
        __Usage:__
            Use the command + language followed by your code that will be executed.
        __Example:__
            rex py3 print('Hello World')
    """
    stdin = ""
    message = event.text.split("rex ", 1)
    chat = await event.get_chat()

    if len(message) < 2:
        await client.update_message(event, rextestercli.__doc__)
        return

    regex = re.search(
        r"([\w.#+]+)\s+([\s\S]+?)(?:\s+\/stdin\s+([\s\S]+))?$",
        message[1],
        re.IGNORECASE,
    )
    language = regex.group(1)
    code = regex.group(2)
    stdin = regex.group(3)

    try:
        res = await rexec(language, code, stdin)
    except UnknownLanguage as exc:
        await client.update_message(event, str(exc))
        return

    output = f"**Language:**\n\n```{language}```"
    output += f"\n\n**Source:** \n\n```{code}```"

    if res.results:
        output += f"\n\n**Result:** \n\n```{res.results}```"

    if res.warnings:
        output += f"\n\n**Warnings:** \n\n```{res.warnings}```\n"

    if res.errors:
        output += f"\n\n**Errors:** \n\n```{res.errors}```"

    if len(output) > 4096:
        with io.BytesIO(str.encode(output)) as out_file:
            out_file.name = "output.txt"
            await client.send_file(chat.id, file=out_file)
            await client.update_message(event, code)
        return

    await client.update_message(event, output)


async def aexec(code, event):
    exec(
        f'async def __aexec(event): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )
    return await locals()['__aexec'](event)


@client.CommandHandler(outgoing=True, command="exec")
async def py_execute(event):
    """
    **Execute your code using your python compiler**
        __Args:__
            `<code>` - Your python code that will be executed.
    """
    chat = await event.get_chat()
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, py_execute.__doc__)
        return

    code = split_text[1]
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    try:
        if "await" in code:
            await aexec(code, event)
        else:
            exec(code)
    except Exception:
        import traceback
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        await client.update_message(event, f"**Query**:\n`{code}`\n\n**Exception:**\n`{exc}`")
        return

    if stderr:
        await client.update_message(event, f"**Query**:\n`{code}`\n\n**Error:**\n`{stderr}`")
        return

    if stdout:
        if len(stdout) > 4096:
            with io.BytesIO(str.encode(stdout)) as out_file:
                out_file.name = "result.txt"
                await client.send_file(chat.id, file=out_file, caption=f"`{code}`")
                return

        await client.update_message(event, f"**Query**:\n`{code}`\n\n**Result:**\n`{stdout}`")
    else:
        await client.update_message(event, f"**Query**:\n`{code}`\n\n**Result:**\n`Success`")


@client.CommandHandler(outgoing=True, command="readall")
async def readall(event):
    """
    **Mark all messages as read.**
    """
    await client.update_message(event, "`Marking all the unread messages as read.. Please wait...`")
    async for dialog in client.iter_dialogs(limit=None):
        await client.send_read_acknowledge(dialog, clear_mentions=True)
    await client.update_message(event, "`Done. All the messages are marked as read`")


@client.CommandHandler(
    outgoing=True,
    command="disconnect")
async def disconnect_companion(event):
    """
    **Disconnects the companion from Telegram.**
    """
    await client.update_message(event, "Thanks for using Telegram Companion. Goodbye!")
    await client.disconnect()


@client.CommandHandler(outgoing=True, command="logout")
async def logout(event):
    """
    **Logs out the companion from Telegram and deletes the session.**
    """
    await client.update_message(event, "Thanks for using Telegram Companion. Goodbye!")
    await client.log_out()


@client.CommandHandler(outgoing=True, command="chatmute")
async def mute(event):
    """
    **Mutes a chat for a given time**
        __Args:__
            `<number>d <number>h <number>m <number>s` - The time in days, hours, minutes and seconds
                At least one of them is required but not more than 4.
        __Usage:__
            Use these arguments as an example: 1d 2h 3m 4s
            the chat will be now muted for one day, two hours, three mintues, and four seconds.
            Please remember that at least one of the values are required but not more than 4.
    """
    chat = await event.get_chat()
    split_text = event.text.split(None, 1)
    if len(split_text) == 1:
        await client.update_message(event, "...")
        return
    elif len(split_text[1].split()) > 4:
        await client.update_message(event, "`Invalid time format`!")
        return

    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    for val in split_text[1].split():
        if val.endswith("d"):
            days = val[:-1] if val[:-1].isdigit() else 0
        if val.endswith("h"):
            hours = val[:-1] if val[:-1].isdigit() else 0
        if val.endswith("m"):
            minutes = val[:-1] if val[:-1].isdigit() else 0
        if val.endswith("s"):
            seconds = val[:-1] if val[:-1].isdigit() else 0

    if any((int(days), int(hours), int(minutes), int(seconds))) == 0:
        await client.update_message(event, "`Invalid time format`!")
        return

    now = datetime.datetime.now()
    dt = now + datetime.timedelta(days=int(days),
                                  hours=int(hours),
                                  minutes=int(minutes),
                                  seconds=int(seconds))

    mute_for = await client(UpdateNotifySettingsRequest(peer=chat.id, settings=InputPeerNotifySettings(show_previews=False, mute_until=int(dt.timestamp()))))
    if mute_for:
        await client.update_message(event, f"`Chat muted until: {dt.strftime('%d/%m/%Y %I:%M:%S%p')}`")
    else:
        await client.update_message(event, "`Failed to mute this chat`!")
