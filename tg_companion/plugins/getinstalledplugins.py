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


@client.CommandHandler(outgoing=True, command="plugin", help=PLUGIN_HELP)
async def get_plugin_info(event):
    split_text = event.text.split(None, 1)
    if len(split_text) > 1:
        plugin_name = split_text[1]
        OUTPUT = f"Plugin Info For: {plugin_name}\n\n"

        plugins = load_plugins_info()
        if plugin_name in plugins:

            dct = plugins[plugin_name]

            for k, v in dct.items():
                OUTPUT += f"\n{k} : `{v}`"

            await event.reply(OUTPUT)
        else:
            await client.update_message(event, f"Plugin `{plugin_name}` is not installed")


@client.CommandHandler(outgoing=True, command="plugins", help=PLUGINS_HELP)
async def get_installed_plugins(event):
    PLUGINS = sorted(load_plugins())
    OUTPUT = f"Installed Plugins:\n\n"
    for plugin in PLUGINS:
        OUTPUT += f"`\n{plugin}`"
    await event.reply(OUTPUT)
