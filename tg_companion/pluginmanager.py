import asyncio
import importlib
import logging
import os
import re
import sys
from argparse import ArgumentParser
import configparser
import shutil

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
config = configparser.ConfigParser()

async def download_plugins(user="nitanmarcel", repo="TgCompanionPlugins", plugin=None):
    if plugin is None:
        LOGGER.error("No plugin specified")
        return

    LOGGER.info(f"Downloading Plugin: {plugin}")

    github = f"https://api.github.com/repos/{user}/{repo}/contents/{plugin}"
    requirements = None

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{github}/{plugin}.plugin") as request:

            if request.status == 404:
                LOGGER.error(
                    f"Can't find the plugin file of {plugin} plugin")
                return

            result = await request.json()
        async with session.get(result.get("download_url")) as plugfile:

            text = await plugfile.text(encoding="utf8")

            LOGGER.info("Writing plugin file")
            if not os.path.isdir(f"tg_companion/plugins/{plugin}"):
                os.makedirs(f"tg_companion/plugins/{plugin}")

            with open(f"tg_companion/plugins/{plugin}/{plugin}.plugin", "w+") as file:
                file.write(text)
        config.read(
            f"tg_companion/plugins/{plugin}/{plugin}.plugin")

        modules_to_load = config.get("CORE", "modules").split(",")
        requirements = config.get("CORE", "requirements").split(",")
        if requirements:
            for module in requirements:
                if not importlib.util.find_spec(module.replace(" ", "")):
                    process = await asyncio.create_subprocess_shell(f"{sys.executable} -m pip install {module}", stdin=asyncio.subprocess.PIPE)
                    await process.communicate()
        for module in modules_to_load:

            async with session.get(f"{github}/{module}.py") as request:

                if request.status == 404:
                    LOGGER.error(f"Can't find the py file of {plugin} plugin")
                    return
                result = await request.json()

            async with session.get(result.get("download_url")) as pyfile:

                text = await pyfile.text(encoding="utf8")
                LOGGER.info("Writing python module")
                with open(f"tg_companion/plugins/{plugin}/{module}.py", "w+") as file:
                    file.write(text)
        LOGGER.info(f"Installed {plugin}")
        LOGGER.info(f"Plugin {plugin} Installed")


def remove_plugin(plugin_name):
    path = f"tg_companion/plugins/{plugin_name}"
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        LOGGER.info(f"Plugin {plugin_name} removed")
    else:
        LOGGER.info("Can't find the specified plugin.")


def list_plugins():
    PLUGINS = sorted(load_plugins())
    OUTPUT = ""
    for plugin in PLUGINS:
        installed = plugin.split("/")[-1]
        OUTPUT += f"\n{installed}"
    return OUTPUT


def load_plugin_info(pluginname):

    PLUGINS = sorted(load_plugins())
    plugin_dct = {}
    for plugin in PLUGINS:
        if plugin.split("/")[-1] == pluginname and os.path.isfile(plugin + ".plugin"):
            config.read(plugin + ".plugin")
            for section in config.sections():
                for option in config.options(section):
                    plugin_dct[option] = config.get(section, option)
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
