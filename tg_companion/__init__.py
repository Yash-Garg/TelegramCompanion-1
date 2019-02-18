from distutils.util import strtobool as sb
import socks
import sys
import os
import logging
import dotenv


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this."
    )
    quit(1)

dotenv.load_dotenv("config.env")

APP_ID = os.environ.get("APP_ID", None)
APP_HASH = os.environ.get("APP_HASH", None)
SESSION_NAME = os.environ.get("SESSION_NAME", "tg_companion")
DB_URI = os.environ.get("DB_URI", None)
DEBUG = sb(os.environ.get("DEBUG", "False"))
CMD_HANDLER = os.environ.get("CMD_HANDLER", ".")

try:
    if CMD_HANDLER[0].isalpha():
        LOGGER.info("Invalid command handler symbol")
        quit(1)
except IndexError:
    LOGGER.info("CMD_HANDLER can't be None")

PROXY_TYPE = os.environ.get("PROXY_TYPE", None)
HOST = os.environ.get("HOST", None)
PORT = os.environ.get("PORT", None)
USERNAME = os.environ.get("USERNAME", None)
PASSWORD = os.environ.get("PASSWORD", None)

BLOCK_PM = sb(os.environ.get("BLOCK_PM", "False"))
NOPM_SPAM = sb(os.environ.get("NOPM_SPAM", "False"))
STATS_TIMER = int(os.environ.get("STATS_TIMER", 3600))
SUBPROCESS_ANIM = sb(os.environ.get("SUBPROCESS_ANIM", "False"))

ENABLE_SSH = sb(os.environ.get('ENABLE_SSH', "False"))
SSH_HOSTNAME = os.environ.get('SSH_HOSTNAME', '::1')
SSH_PORT = os.environ.get('SSH_PORT', 22)
SSH_USERNAME = os.environ.get('SSH_USERNAME', None)
SSH_PASSWORD = os.environ.get('SSH_PASSWORD', None)
SSH_PASSPHRASE = os.environ.get('SSH_PASSPHRASE', None)
SSH_KEY = os.environ.get('SSH_KEY', None)

proxy = None
proxy_type = None
proxy_addr = HOST
proxy_port = PORT
proxy_username = USERNAME
proxy_password = PASSWORD
if PROXY_TYPE:
    if PROXY_TYPE == "HTTP":
        proxy_type = socks.HTTP
    elif PROXY_TYPE == "SOCKS4":
        proxy_type = socks.SOCKS4
    elif PROXY_TYPE == "SOCKS5":
        proxy_type = socks.SOCKS5
    else:
        proxy_type = None

    proxy = (proxy_type, proxy_addr, int(proxy_port), False)
if USERNAME and PASSWORD:
    proxy = (
        proxy_type,
        proxy_addr,
        proxy_port,
        False,
        proxy_username,
        proxy_password)
