from tg_companion import LOGGER
import os
import configparser


def load_plugins():
    config = configparser.ConfigParser()
    plugins = []
    for root, dirs, files in os.walk("tg_companion/plugins/"):
        for dir in dirs:
            if not dir.endswith("__"):
                for file in os.listdir(root + dir):
                    if file.endswith(".plugin"):
                        config.read(root + dir + "/" + file)
                        plugins.append(
                            root +
                            dir +
                            "/" +
                            config.get(
                                "CORE",
                                "main"))
    return plugins


PLUGINS = sorted(load_plugins())

for plugin_name in PLUGINS:
    plugin_to_load = plugin_name.split("/")[-1]
    LOGGER.info(f"Loading Plugin: {plugin_to_load}")
__all__ = PLUGINS + ["PLUGINS"]
