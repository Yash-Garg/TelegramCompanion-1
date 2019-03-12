import asyncio
import io
import os
import zipfile
from getpass import getpass
import inspect
from alchemysession import AlchemySessionContainer
from telethon import TelegramClient, events
from telethon.client.users import UserMethods
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError

from tg_companion import (APP_HASH, APP_ID, CMD_HANDLER, DB_URI, LOGGER,
                          SESSION_NAME, proxy)
from tg_companion._version import __version__

loop = asyncio.get_event_loop()


CMD_HELP = {}


class CustomDisconnect(UserMethods):
    async def _run_until_disconnected(self):
        try:
            await self.disconnected
        except KeyboardInterrupt:
            LOGGER.info("Thanks for using Telegram Companion. Goodbye!")
            self.disconnect()

    def loop_until_disconnected(self):
        if self.loop.is_running():
            return self._run_until_disconnected()
        try:
            return self.loop.run_until_complete(self.disconnected)
        except KeyboardInterrupt:
            LOGGER.info("Thanks for using Telegram Companion. Goodbye!")
            self.disconnect()


class CustomClient(TelegramClient):

    def __init__(self, session_name, app_id, app_hash):
        super().__init__(
            session_name,
            app_id,
            app_hash,
            proxy=proxy,
            app_version=__version__.public())

        LOGGER.info("Connecting to Telegram servers")
        try:
            loop.run_until_complete(self.connect())
        except ConnectionError:
            LOGGER.info("Failed to connect to Telegram Server.. Retrying")
            loop.run_until_complete(self.connect())

        if not loop.run_until_complete(self.is_user_authorized()):
            LOGGER.info("Welcome to Telegram Companion!")
            LOGGER.info(
                "Telegram Companion is a python app trying to bring new features to other official or unofficial Telegram clients")
            LOGGER.info(
                "You can report a bug or a give a suggestion in our telegram group at https://t.me/tgcompanion")
            LOGGER.info(
                "Because this is your first time using the companion, you have to sign in with your telegram account:\n\n")
            phone = input("Enter your phone: ")
            loop.run_until_complete(self.sign_in(phone))

            self_user = None
            while self_user is None:

                code = input(
                    "Please enter the code you just recieved.. Press enter to send the code via SMS: ")
                loop.run_until_complete(
                    self.send_code_request(
                        phone, force_sms=False))
                if not code:
                    loop.run_until_complete(
                        self.send_code_request(
                            phone, force_sms=True))
                    code = input(
                        "Please Enter the code you just recieved: ")
                try:
                    self_user = loop.run_until_complete(
                        self.sign_in(code=code))
                except Exception as exc:
                    if isinstance(exc, PhoneCodeInvalidError):
                        code = input(
                            "The phone code entered was invalid. Press enter to try again")
                    elif isinstance(exc, SessionPasswordNeededError):
                        password = getpass(
                            "Two step verification is enabled. Please enter your password: ")

                        self_user = loop.run_until_complete(
                            self.sign_in(password=password))

        LOGGER.info("Connected!!")

    def CommandHandler(
            self,
            func=None,
            command=None,
            allow_edited=False,
            help=None,
            **kwargs):
        def decorator(f):
            """
            Decorator alternative for `client.on()` which uses the same arguments but with some exceptions

            Optional Args:
                command (str):
                    If set to any str instance the decorated function will only work if
                            the message matches the command handler symbol ( default "." ) + the word/regex in the command argument
                            if the command is not set or None it will execute the decorated function when a message event is triggered

                allow_edited (bool):
                    If set True the command will also work when the message is edited.

                help (str):
                    The help message used for displaying the command usage

            """
            global CMD_HELP
            pattern = None
            if help:
                LOGGER.warning(
                    f"Deprecated help argument in: {inspect.getmodule(f).__name__}. Please make sure you updated the your companion and plugins")
            if command:
                CMD_SYMBOL = ""
                for symbol in CMD_HANDLER:
                    CMD_SYMBOL += "\\" + symbol
                pattern = CMD_SYMBOL + command
            self.add_event_handler(
                f, events.NewMessage(
                    pattern=pattern, func=func, **kwargs))

            if f.__doc__ and command:
                cmd_name = command.split(None, 1)[0]
                if cmd_name not in CMD_HELP.keys():
                    CMD_HELP.update({cmd_name: f.__doc__})

            if allow_edited:
                self.add_event_handler(
                    f, events.MessageEdited(
                        pattern=pattern, func=func, **kwargs))
            return f
        return decorator

    async def update_message(self, entity, text):
        """ Alternative for `client.edit_message()`
            which edit a message and if the edit is not allowed is replying to the respective message.
        """
        try:
            await self.edit_message(await entity.get_chat(), entity, text)
        except Exception:

            await self.send_message(await entity.get_chat(), text, reply_to=entity)

    async def send_from_disk(self, event, path, caption=None, force_document=False, use_cache=None, reply_to=None):
        if os.path.isfile(path):
            if os.path.getsize(path) >= 1500000000:
                await self.update_message(event, "`File size too big. Max 1.5GB.`")
                return
            f_name = os.path.basename(path)
            f_size, unit = self.convert_file_size(os.path.getsize(f_name))
            await self.update_message(event,
                                      f"**Uploading**:\n\n"
                                      f"  __File Name:__ `{f_name}`\n"
                                      f"  __Size__: `{f_size}` {unit}\n"
                                      )

            await self.send_file(event.chat_id, path, file_name=f_name,
                                 force_document=force_document, reply_to=reply_to, progress_callback=None)
            await event.delete()

        elif os.path.isdir(path):
            d_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    d_size += os.path.getsize(fp)
                    if d_size >= 1500000000:
                        await self.update_message(event, "`Folder size too big. Max 1.5GB`")
                        return

            d_name = os.path.dirname(path)

            try:
                with io.BytesIO() as memzip:
                    with zipfile.ZipFile(memzip, mode="w") as zf:
                        await self.update_message(event, "Processing ZipFile from folder")
                        for file in os.listdir(path):
                            zf.write(f"{path}{file}")

                    memzip.name = f"{d_name}.zip"
                    memzip.seek(0)
                    d_size, unit = self.convert_file_size(d_size)
                    await self.update_message(event,
                                              f"**Uploading**:\n\n"
                                              f"  __Folder Name:__ `{d_name}`\n"
                                              f"  __Size__: `{d_size}` {unit}\n"
                                              )

                    await self.send_file(event.chat_id, file=memzip, allow_cache=None, progress_callback=None)
                    await event.delete()
            except FileNotFoundError:
                await self.update_message(event, f"`{path}` doesn't exist.")
                return
        else:
            await self.update_message(event, f"{path} doesn't exist.")
            return

    @staticmethod
    async def is_user_admin(chat):
        if chat.admin_rights:
            return True
        elif chat.creator:
            return True
        else:
            return False

    @staticmethod
    def convert_file_size(size):
        power = 2**10
        n = 0
        units = {
            0: '',
            1: 'kilobytes',
            2: 'megabytes',
            3: 'gigabytes',
            4: 'terabytes'}
        while size > power:
            size /= power
            n += 1
        return round(size, 2), units[n]

    def on_timer(self, seconds):
        """
        A decorator that runs a decorated function every x seconds.

        Args:

        seconds (int): Updates the function every given second
        """
        def decorator(fcn):
            async def wrapper():
                while not self.is_connected():
                    await asyncio.sleep(1)
                while True:
                    if int(seconds) == 0:
                        break
                    await fcn()
                    await asyncio.sleep(seconds)
            loop.create_task(wrapper())

            return wrapper
        return decorator


class CompanionClient(CustomClient, CustomDisconnect):
    pass


container = AlchemySessionContainer(DB_URI)
session = container.new_session(SESSION_NAME)

client = CompanionClient(session, APP_ID, APP_HASH)
