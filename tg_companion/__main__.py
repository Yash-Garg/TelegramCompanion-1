import asyncio
import importlib


from tg_companion import CMD_HANDLER, LOGGER, proxy
from tg_companion.modules import MODULES
from tg_companion.plugins import PLUGINS
from tg_companion.tgclient import CMD_HELP, client

for module_name in MODULES:
    imported_module = importlib.import_module(
        "tg_companion.modules." + module_name)

for plugin_name in PLUGINS:
    imported_plugin = importlib.import_module(
        "tg_companion.plugins." + plugin_name)

if proxy:
    LOGGER.info(f"Connecting to Telegram over proxy: {proxy[1]}:{proxy[2]}")
    LOGGER.info(
        f"Use {CMD_HANDLER}ping in any chat to see if your userbot has connected.")
else:
    LOGGER.info(
        f"Your userbot is running. Type {CMD_HANDLER}version in any chat to test it")

SELF_HELP = """
    **Displays this message.**
        __Args:__
            `<command>` - **(optional)** __Optional command name to get display help for.__
"""


@client.CommandHandler(outgoing=True, command="help", help=SELF_HELP)
async def send_help(event):

    text = event.text.split()
    parts = 0
    limit_exceded = False
    saved_keys = []

    if len(text) == 2:
        if text[1] in CMD_HELP:
            await event.edit(f"Here is the help for the `{text[1]}` command:\n{CMD_HELP.get(text[1])}")
            return
        else:
            await event.edit(f"No help available for `{text[1]}`")
            return

    OUTPUT = ""
    if not event.is_private:
        await event.edit("Use this in PM for help!")
        return

    if CMD_HELP:
        for k, v in sorted(CMD_HELP.items()):
            OUTPUT += f"\n\n{CMD_HANDLER}{k}: {v}"
            saved_keys.append(k)
            if len(OUTPUT) >= 3096:
                parts += 1
                await event.reply(f"**Here are all the commands you can use. Part {parts}** \n {OUTPUT}")
                OUTPUT = ""
                limit_exceded = True
            if limit_exceded is True:
                if k not in saved_keys:
                    OUTPUT += f"\n\n{CMD_HANDLER}{k}: {v}"

    await event.reply(f"**Here are all the commands you can use. Part {parts + 1}** \n {OUTPUT}")


loop = asyncio.get_event_loop()


if __name__ == "__main__":

    client.run_until_disconnected()
