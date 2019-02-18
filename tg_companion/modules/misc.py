import io
import os
import platform
import re
import sys
import time
from html import escape

import aiohttp
import telethon
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User

from tg_companion.modules.rextester.api import Rextester, UnknownLanguage
from tg_companion.tgclient import client

from .._version import __version__

PING_HELP = """
    **Test if the bot is alive and the response time.**
"""

VER_HELP = """
    **Get your companion version information.**
"""

INFO_HELP = """
    **Get a user's info.**
"""

REX_HELP = """
    **Execute your code using rextester's API**
        __Usage:__
            __Use the command symbol + language followed by your code that will be executed.__
        __Example:__
            `$py3 print("Hello World")`
"""

SEND_LOG_HELP = """
    **Send the log files from the logs folder. Requires DEBUG to be enabled in config.env or exported**
"""

EXEC_HELP = """
    **Execute your code using your python compiler**
        __Args:__
            `<code>` - Your python code that will be executed.
"""


@client.CommandHandler(outgoing=True, command="ping", help=PING_HELP)
@client.log_exception
async def ping(event):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.google.com"):
            end_time = time.time()
            ping_time = float(end_time - start_time) * 1000
            await event.edit(f"Ping time was: {ping_time}ms")


@client.CommandHandler(outgoing=True, command="version", help=VER_HELP)
@client.log_exception
async def version(event):
    bot_version = __version__.public()
    python_version = platform.python_version()
    telethon_version = telethon.__version__

    await event.edit(f"__Companion__ (**{bot_version}**),"
                     f" __Python__ (**{python_version}**),"
                     f" __Telethon__"
                     f" (**{telethon_version}**)")


@client.CommandHandler(outgoing=True, command="info", help=INFO_HELP)
@client.log_exception
async def user_info(event):
    message = event.message
    user = await event.get_sender()
    chat = await event.get_chat()

    if event.reply_to_msg_id:
        message = await event.get_reply_message()
        user = await message.get_sender()

    if len(event.text.split()) > 1:
        user = event.text.split()[1]
        try:
            user = await client.get_entity(user)
        except Exception as exc:
            await event.reply(str(exc))
            return

        if not isinstance(user, User):
            await event.reply(f"`@{user.username}` is not a User")
            return

    full_user = await client(GetFullUserRequest(user.id))
    firstName = full_user.user.first_name
    lastName = full_user.user.last_name
    username = full_user.user.username
    user_id = full_user.user.id
    common_chats = full_user.common_chats_count

    REPLY = "<b>User Info:</b>\n"

    REPLY += f"\nFirst Name: {escape(firstName)}"

    if lastName:
        REPLY += f"\nLast Name: {escape(lastName)}"
    if username:
        REPLY += f"\nUsername: @{escape(username)}"
    REPLY += f"\nPermanent user link: <a href=\"tg://user?id={user_id}\">link</a>"
    if full_user.about:
        REPLY += f"\n\n<b>About User:</b>\n{escape(full_user.about)}"
    if not full_user.user.is_self:
        REPLY += f"\n\nYou have <code>{common_chats}</code> chats in common with this user"

    await client.send_message(
        chat.id, REPLY, reply_to=message.id, link_preview=False, file=full_user.profile_photo, parse_mode="html"
    )


@client.CommandHandler(outgoing=True, command="$", help=REX_HELP)
@client.log_exception
async def rextestercli(event):
    stdin = ""
    message = event.text
    chat = await event.get_chat()

    if len(message.split()) > 1:
        regex = re.search(
            r"^\$([\w.#+]+)\s+([\s\S]+?)(?:\s+\/stdin\s+([\s\S]+))?$",
            message,
            re.IGNORECASE,
        )
        language = regex.group(1)
        code = regex.group(2)
        stdin = regex.group(3)

        try:
            rextester = Rextester(language, code, stdin)
            res = await rextester.exec()
        except UnknownLanguage as exc:
            await event.edit(str(exc))
            return

        output = ""
        output += f"**Language:**\n```{language}```"
        output += f"\n\n**Source:** \n```{code}```"

        if res.result:
            output += f"\n\n**Result:** \n```{res.result}```"

        if res.warnings:
            output += f"\n\n**Warnings:** \n```{res.warnings}```\n"

        if res.errors:
            output += f"\n\n**Errors:** \n'```{res.errors}```"

        if len(res.result) > 4096:
            with io.BytesIO(str.encode(res.result)) as out_file:
                out_file.name = "result.txt"
                await client.send_file(chat.id, file=out_file)
                await event.edit(code)
            return

        await event.edit(output)


@client.CommandHandler(outgoing=True, command="sendlog", help=SEND_LOG_HELP)
@client.log_exception
async def send_logs(event):

    if os.path.isdir("logs/"):
        await client.send_from_disk(event, "logs/")
    else:
        await event.edit("`There are no logs saved!`")


@client.CommandHandler(outgoing=True, command="exec", help=EXEC_HELP)
async def py_execute(event):
    chat = await event.get_chat()
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await event.edit(EXEC_HELP)
        return

    code = split_text[1]
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    try:
        exec(code)
    except Exception:
        import traceback
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        await event.edit(f"**Query**:\n`{code}`\n\n **Exception:**\n`{exc}`")
        return

    if stderr:
        await event.edit(f"**Query**:\n`{code}`\n\n **Error:**\n`{stderr}`")
        return

    if stdout:
        if len(stdout) > 4096:
            with io.BytesIO(str.encode(stdout)) as out_file:
                out_file.name = "result.txt"
                await client.send_file(chat.id, file=out_file, caption=f"'{code}'")
                return

        await event.edit(f"**Query**:\n`{code}`\n\n **Result:**\n`{stdout}`")
    else:
        await event.edit("Did you forget to output something?")
