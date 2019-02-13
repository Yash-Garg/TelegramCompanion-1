import asyncio
import importlib

from tg_companion import LOGGER, CMD_HANDLER, proxy
from tg_companion.modules import MODULES
from tg_companion.plugins import PLUGINS
from tg_companion.tgclient import client

for module_name in MODULES:
    imported_module = importlib.import_module(
        "tg_companion.modules." + module_name)

for plugin_name in PLUGINS:
    imported_plugin = importlib.import_module(
        "tg_companion.plugins." + plugin_name)

if proxy:
    LOGGER.info(f"Connecting to Telegram over proxy: {proxy[1]}:{proxy[2]}")
    LOGGER.info(f"Use {CMD_HANDLER}ping in any chat to see if your userbot has connected.")
else:
    LOGGER.info(f"Your userbot is running. Type {CMD_HANDLER}ping in any chat to test it")


loop = asyncio.get_event_loop()


if __name__ == "__main__":

    client.run_until_disconnected()
