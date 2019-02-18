import asyncio
import logging
import os
import re
import sys
from argparse import ArgumentParser

import aiohttp

from tg_companion.plugins import load_plugins

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

parser = ArgumentParser()

parser.add_argument(
    "--install",
    help="Install any given plugin. Usage: --install <pluginname> or <user/repo/plugin_name>.")

parser.add_argument(
    "--remove",
    help="Remove any given plugin. Usage: --remove <pluginname>.")

parser.add_argument(
    "--plugins",
    help="Disply the installed plugins", action="store_true")

args = parser.parse_args()


async def download_plugins(user="nitanmarcel", repo="TgCompanionPlugins", plugin=None):
    if plugin is None:
        LOGGER.error("No plugin specified")
        return

    LOGGER.info(f"Downloading Plugin: {plugin}")

    github = f"https://api.github.com/repos/{user}/{repo}/contents/{plugin}/{plugin}"
    requirements = None

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{github}.py") as request:

            if request.status == 404:
                LOGGER.error(f"Can't find the py file of {plugin} plugin")
                return
            result = await request.json()

        async with session.get(result.get("download_url")) as pyfile:

            text = await pyfile.text(encoding="utf8")
            LOGGER.info("Writing python module")
            with open(f"tg_companion/plugins/{plugin}.py", "w+") as file:

                file.write(text)

        async with session.get(f"{github}.plugin") as request:

            if request.status == 404:
                LOGGER.error(
                    f"Can't find the plugin file of {plugin} plugin")
                return

            result = await request.json()
        async with session.get(result.get("download_url")) as plugfile:

            text = await plugfile.text(encoding="utf8")

            LOGGER.info("Writing plugin file")

            with open(f"tg_companion/plugins/{plugin}.plugin", "w+") as file:
                file.write(text)

        get_req = re.search("Requirements = (.+)", text)
        if get_req:
            requirements = get_req.group(1)

            if "," in requirements:
                requirements = requirements.replace(",", "")

            LOGGER.info("Installing Requirements:")

            process = await asyncio.create_subprocess_shell(f"pip3 install {requirements}", stdin=asyncio.subprocess.PIPE)

            stdout, stderr = await process.communicate()

            LOGGER.info(f"Installed {plugin}")
            LOGGER.info(f"Plugin {plugin} Installed")


def remove_plugin(plugin_name):
    if os.path.isfile(f"tg_companion/plugins/{plugin_name}.plugin"):
        for plugin in os.listdir("tg_companion/plugins/"):
            if re.search(plugin_name, plugin):
                os.remove(os.path.join("tg_companion/plugins/", plugin))
        LOGGER.info(f"Plugin {plugin_name} removed")
    else:
        LOGGER.info("Can't find the specified plugin.")


def list_plugins():
    PLUGINS = sorted(load_plugins())
    OUTPUT = f"Installed Plugins:\n"
    for plugin in PLUGINS:
        OUTPUT += f"\n{plugin}"
    print(OUTPUT)


def load_plugins_info():

    path = "tg_companion/plugins/"
    plugin_dct = {}
    if os.path.isdir(path):
        for plugin in os.listdir("tg_companion/plugins/"):
            if plugin.endswith(".plugin"):
                with open(path + plugin) as config_file:
                    for line in config_file.read().splitlines():
                        if "Module" in line:
                            module_name = line.split("Module = ")[1]
                        item = line.split("=")[0]
                        val = line.split("=")[1]

                        if module_name not in plugin_dct.keys():
                            plugin_dct[module_name] = {item: val}
                        if val not in plugin_dct:
                            plugin_dct[module_name].update({item: val})

    return plugin_dct


if __name__ == "__main__":
    if args.install:
        loop = asyncio.get_event_loop()

        to_match = re.match(
            r"([^\/]+)\/([^\/]+)(\/([^\/]+)(\/(.*))?)?",
            args.install)
        if to_match:
            loop.run_until_complete(
                download_plugins(
                    user=to_match.group(1),
                    repo=to_match.group(2),
                    plugin=to_match.group(4)))
        else:
            loop.run_until_complete(
                download_plugins(
                    plugin=args.install))
    elif args.remove:
        remove_plugin(args.remove)
    elif args.plugins:
        list_plugins()
    else:
        parser.print_help(sys.stderr)
