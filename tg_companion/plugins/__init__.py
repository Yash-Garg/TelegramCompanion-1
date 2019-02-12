from tg_companion import LOGGER
from os.path import dirname, basename, isfile
import glob



def load_plugins():

    path = glob.glob(dirname(__file__) + "/*.py")

    plugins = [
        basename(plugin)[:-3]
        for plugin in path
        if isfile(plugin) and plugin.endswith(".py") and not plugin.endswith("__init__.py")
    ]
    return plugins


PLUGINS = sorted(load_plugins())

for plugin_name in PLUGINS:
    LOGGER.info(f"Loading Plugin: {plugin_name}")
__all__ = PLUGINS + ["PLUGINS"]
