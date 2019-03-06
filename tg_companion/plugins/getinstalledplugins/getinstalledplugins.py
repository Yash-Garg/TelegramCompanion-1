from tg_companion.pluginmanager import load_plugin_info, list_plugins
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
        info = load_plugin_info(plugin_name)
        if info:
            await client.update_message(event,
                                         f"**Plugin Info for:** `{plugin_name}`\n\n"
                                         f"**Name:** `{info.get('main')}`\n"
                                         f"**Author:** `{info.get('author')}`\n"
                                         f"**Description:** `{info.get('description')}`")
        else:
            await client.update_message(event, f"Plugin `{plugin_name}` is not installed")


@client.CommandHandler(outgoing=True, command="plugins", help=PLUGINS_HELP)
async def get_installed_plugins(event):
    await client.update_message(event, f"**Installed Plugins:**\n{list_plugins()}")
