import asyncio
import os
import time

import asyncssh
from telethon.errors import FloodWaitError

from tg_companion import (ENABLE_SSH, SSH_HOSTNAME, SSH_KEY, SSH_PASSPHRASE,
                          SSH_PASSWORD, SSH_PORT, SSH_USERNAME,
                          SUBPROCESS_ANIM)
from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="term")
async def terminal(event):
    """
    **Execute a bash command on your pc/server**
        __Args:__
            `<command>` - Your bash command that will be executed.
    """

    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, terminal.__doc__)
        return

    cmd = split_text[1]

    await client.update_message(event, "`Connecting..`")

    start_time = time.time() + 10
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    OUTPUT = f"**Query:**\n\n`{cmd}`\n\n**Result:**\n\n"

    if not SUBPROCESS_ANIM:
        stdout, stderr = await process.communicate()

        if len(stdout) > 4096:
            await event.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            return

        if stderr.decode():
            await client.update_message(event, f"{OUTPUT}`{stderr.decode()}`")
            return

        await client.update_message(event, f"{OUTPUT}`{stdout.decode()}`")
        return

    while process:
        if time.time() > start_time:
            if process:
                process.kill()
            await client.update_message(event, f"{OUTPUT}\n__Process killed__: `Time limit reached`")
            break

        stdout = await process.stdout.readline()

        if not stdout:
            _, stderr = await process.communicate()
            if stderr.decode():
                OUTPUT += f"`{stderr.decode()}`"
                try:
                    await client.update_message(event, OUTPUT)
                except Exception:
                    break
                break

        if stdout:
            OUTPUT += f"`{stdout.decode()}`"

        if len(OUTPUT) > 4096:
            if process:
                process.kill()
            await event.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
            break
        try:
            await event.edit(OUTPUT)
        except FloodWaitError:
            stdout, stderr = await process.communicate()
            if stderr:
                await client.update_message(event, f"{OUTPUT}`{stderr}`")
                break

            await client.update_message(event, f"{OUTPUT}`{stdout}`")
            break


@client.CommandHandler(
    outgoing=True,
    func=lambda x: ENABLE_SSH,
    command="rterm",
)
async def ssh_terminal(event):
    """
    **Execute a bash command on your ssh connection**
        __Args:__
            `<command>` - Your bash command that will be executed.
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, ssh_terminal.__doc__)
        return

    cmd = split_text[1]

    OUTPUT = f"**Query:**\n`{cmd}`\n\n**Output:**\n"
    await client.update_message(event, "`Connecting..`")

    async with asyncssh.connect(
        str(SSH_HOSTNAME),
        port=int(SSH_PORT),
        username=str(SSH_USERNAME),
        password=str(SSH_PASSWORD),
        passphrase=str(SSH_PASSPHRASE),
        client_keys=SSH_KEY,
        known_hosts=None,
    ) as conn:

        start_time = time.time() + 10
        async with conn.create_process(cmd) as process:
            if not SUBPROCESS_ANIM:
                stdout, stderr = await process.communicate()

                if len(stdout) > 4096:
                    await event.reply(f"{OUTPUT}\n__Process killed:__ `Messasge too long`")
                    return

                if stderr:
                    await client.update_message(event, f"{OUTPUT}`{stderr}`")
                    return

                await client.update_message(event, f"{OUTPUT}`{stdout}`")
                return

            while True:
                if time.time() > start_time:
                    break

                stdout = await process.stdout.readline()

                if not stdout:
                    _, stderr = await process.communicate()
                    if stderr:
                        OUTPUT += f"`{stderr}`"
                        try:
                            await client.update_message(event, OUTPUT)
                        except Exception:
                            break
                        break

                if stdout:
                    OUTPUT += f"`{stdout}`"

                if len(OUTPUT) > 4096:
                    await event.reply("__Process killed:__ `Messasge too long`")
                    break
                try:
                    await client.update_message(event, OUTPUT)
                except FloodWaitError:
                    stdout, stderr = await process.communicate()
                    if stderr:
                        await client.update_message(event, f"{OUTPUT}`{stderr}`")
                        break

                    await client.update_message(event, f"{OUTPUT}`{stdout}`")
                    break


@client.CommandHandler(outgoing=True, command="upload")
async def upload_file(event):
    """
    **Upload a file or folder from your pc/server**
        __Args:__
            `<path>` - The path to the file or folder you want to upload
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, upload_file.__doc__)
        return

    to_upload = split_text[1]

    await client.send_from_disk(event, to_upload, force_document=True)


@client.CommandHandler(
    outgoing=True,
    command="rupload (.+)",
)
async def ssh_upload_file(event):
    """
    **Upload a file or folder from your ssh connection**
        __Args:__
            `<path>` - The path to the file or folder you want to upload
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, ssh_upload_file.__doc__)
        return

    to_upload = split_text[1]

    await client.update_message(event, "`Connecting...`")

    async with asyncssh.connect(
            str(SSH_HOSTNAME),
            port=int(SSH_PORT),
            username=str(SSH_USERNAME),
            password=str(SSH_PASSWORD),
            passphrase=str(SSH_PASSPHRASE),
            client_keys=SSH_KEY,
            known_hosts=None) as conn:

        async with conn.create_process(f"test -f {to_upload} && echo 1") as process:
            stdout, _ = await process.communicate()
            if stdout:
                async with conn.start_sftp_client() as ftp:
                    await client.update_message(event, "`Downloading...`")
                    await ftp.get(to_upload, to_upload)
                    await client.send_from_disk(event, to_upload, force_document=True)

                os.remove(to_upload)
            else:
                await client.update_message(event, f"__File Not Found__: `{to_upload}`")
