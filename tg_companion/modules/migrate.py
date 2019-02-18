from telethon import errors
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import User

from tg_companion.tgclient import client

CHAT_IDS = []
FAILED_CHATS = []
FAILED_CHATS_COUNT = 0
MIGRATED_CHATS_COUNT = 0

MIGRATE_HELP = """
    **Migrate all your chats to a second account**
        __Args:__
            `<username` - __The username of your second account__
"""


@client.CommandHandler(
    outgoing=True,
    command="migrate")
@client.log_exception
async def account_migrate(event):
    global CHAT_IDS
    global FAILED_CHATS
    global FAILED_CHATS_COUNT

    await event.edit(
        "`Migrating Chats. This might take a while so relax. and check this message later`"
    )

    split_text = event.text.split(None, 1)

    if len(split_text) == 0:
        await event.edit(MIGRATE_HELP)
        return

    username = split_text[1]
    entity = await client.get_entity(username)

    if isinstance(entity, User):
        if entity.contact:
            dialogs = await client.get_dialogs(limit=None)
            for dialog in dialogs:
                if dialog.is_group:
                    if dialog.id not in CHAT_IDS:
                        CHAT_IDS.append(dialog.id)
                if dialog.is_channel:
                    if dialog.is_group:
                        if dialog.id not in CHAT_IDS:
                            CHAT_IDS.append(dialog.id)
            if CHAT_IDS:
                for id in CHAT_IDS:
                    try:
                        await client(
                            AddChatUserRequest(
                                chat_id=id, user_id=username, fwd_limit=1
                            )
                        )
                    except Exception as exc:
                        if isinstance(exc, errors.ChatIdInvalidError):
                            try:
                                await client(
                                    InviteToChannelRequest(channel=id, users=[username])
                                )
                            except Exception:
                                chat = await client.get_entity(id)
                                if id not in FAILED_CHATS:
                                    FAILED_CHATS.append(chat.id)
                                    FAILED_CHATS_COUNT = FAILED_CHATS_COUNT + 1

                                pass
                        else:
                            chat = await client.get_entity(id)
                            if id not in FAILED_CHATS:
                                FAILED_CHATS.append(chat.id)
                                FAILED_CHATS_COUNT = FAILED_CHATS_COUNT + 1

                REPLY = f"Failed to migrate `{FAILED_CHATS_COUNT}` chat because a problem has occurred or you are already in those groups/channels\n"

                await event.reply(REPLY)
        else:
            await event.edit("`The specified user is not a contact.`")
    else:
        await event.edit("The specified username is not a User")
