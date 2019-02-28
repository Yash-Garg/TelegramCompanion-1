from tg_companion.tgclient import client
from telethon import events
import re


FLAGS = {
    "i": re.I,
    "l": re.L,
    "m": re.M,
    "s": re.S,
    "a": re.A,
    "x": re.X
}


SED_HELP = """
    **Sed-like commands**
    __Usage:__
        Reply to a message to get send back a modified version.
        The sed format is: `sed/<to_replace>/<replace_with>/<optional_flag>`
    __Flags:__
        `i` : Ignore case
        `l` : Locale
        `m` : Multiline
        `s` : Dotall
        `a` : Ascii
        `x` : Verbose
        __You can find all about these flags here:__ https://docs.python.org/3.7/library/re.html#module-contents

"""


@client.on(events.NewMessage(outgoing=True, pattern="sed/"))
@client.log_exception
async def regex_no_symb(event):

    regex_cmd = r"\/((?:\\\/|[^\/])+)\/((?:\\\/|[^\/])*)(?:\/(.*))?"

    regex_group = re.search(regex_cmd, event.text)
    group_len = 0
    if not regex_group:
        await client.update_message(event, SED_HELP)
        return

    for group in regex_group.groups():
        if group is not None:
            group_len += 1

    if group_len < 2 or not event.reply_to_msg_id:
        await client.update_message(event, SED_HELP)
        return

    rep_msg = await event.get_reply_message(

    )
    to_replace = regex_group.group(1)
    replacement = regex_group.group(2).replace('\\/', '/')
    flags = 0
    count = 1

    if group_len > 2:
        for flag in regex_group.group(3):
            if flag == "g":
                count = 0
            elif flag.lower() in "ilmsax":
                flags |= FLAGS[flag.lower()]
            else:
                await client.update_message(event, f"**unknown flag:** `{regex_group.group(3)}`")
                return

    final_text = re.sub(
        to_replace,
        replacement,
        rep_msg.text,
        count=count,
        flags=flags)
    await client.update_message(event, f"**Did you mean:**\n\n{final_text}")


@client.CommandHandler(outgoing=True, command="sed/", help=SED_HELP)
@client.log_exception
async def regex_cmd(event):
    await regex_no_symb(event)
