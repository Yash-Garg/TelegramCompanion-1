from telethon import events

from tg_companion.pluginmanager import load_plugins_info
from tg_companion.plugins import load_plugins
from tg_companion.tgclient import client

PLUGIN_HELP = """
    **Get the plugin's info**
        __Args:__
            <pluginname> - The plugin you want to get the info
"""

PLUGINS_HELP = """
    **Get all the installed plugins.**
"""


@client.on(events.NewMessage(outgoing=True, pattern=r"\.plugin (.+)"))
async def get_plugin_info(event):
    plugin_name = event.pattern_match.group(1)
    OUTPUT = f"Plugin Info For: {plugin_name}\n\n"

    plugins = load_plugins_info()
    if plugin_name in plugins:

        dct = plugins[plugin_name]

        for k, v in dct.items():
            OUTPUT += f"\n{k} : `{v}`"

        await event.reply(OUTPUT)
    else:
        await event.edit(f"Plugin `{plugin_name}` is not installed")


@client.on(events.NewMessage(outgoing=True, pattern=r"\.plugins"))
async def get_installed_plugins(event):
    PLUGINS = sorted(load_plugins())
    OUTPUT = f"Installed Plugins:\n\n"
    for plugin in PLUGINS:
        OUTPUT += f"`\n{plugin}`"
    await event.reply(OUTPUT)
