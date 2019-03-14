import sqlalchemy as db
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import (ChannelParticipantCreator,
                               ChannelParticipantsAdmins, ChatBannedRights)

from tg_companion.tgclient import DB_URI, client

engine = db.create_engine(DB_URI)
metadata = db.MetaData()


gbans_tbl = db.Table("global_bans", metadata,
                     db.Column("user_id", db.Integer(), primary_key=True),
                     db.Column("reason", db.String()))

gban_chats_tbl = db.Table("gban_allowed_chats", metadata,
                          db.Column("chat_id", db.Integer(), primary_key=True),
                          db.Column("is_enabled", db.Boolean()))


metadata.create_all(
    bind=engine,
    tables=[gbans_tbl, gban_chats_tbl],
    checkfirst=True
)


GBANNED_USERS = {}

GBAN_ALLOWED_CHATS = []


def _load_gbanned_users():
    GBANNED_USERS.clear()
    connection = engine.connect()
    query = db.select([gbans_tbl])
    for row in connection.execute(query).fetchall():
        if row:
            GBANNED_USERS.update({row[0]: row[1]})
    connection.close()


def _load_gban_enabled_chats():
    GBAN_ALLOWED_CHATS.clear()
    connection = engine.connect()
    query = db.select([gban_chats_tbl.columns.chat_id]).where(
        gban_chats_tbl.columns.is_enabled == db.true())
    for row in connection.execute(query).fetchall():
        if row:
            GBAN_ALLOWED_CHATS.append(row[0])
    connection.close()


_load_gbanned_users()
_load_gban_enabled_chats()


@client.CommandHandler(outgoing=True, command="gban")
async def gban_user(event):
    """
   **Globally ban any user.**
       __Usage:__
           Reply to or mention a user to globally ban him.
           This will only work if the owner accepts global bans from your companion by replying to you with `.enablegbans`.
           The owner can also disable global bans from your companion by replying to you with `.disalegbans`.
   """

    me = await client.get_me()
    reason = ""

    del_cmd_text = event.text.split("gban", 1)[1]
    split_text = del_cmd_text.split(None, 1)

    if event.reply_to_msg_id:
        rep_msg = await event.get_reply_message()
        user = await rep_msg.get_sender()
        reason = del_cmd_text

    else:
        if len(split_text) == 0:
            await client.update_message(event, "`I don't have any user to gban.`")
            return

        if len(split_text) > 1:
            reason = split_text[1]

        try:
            user = int(
                split_text[0]) if split_text[0].isdigit() else split_text[0]
            user = await client.get_entity(split_text[0])
        except Exception:
            await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
            return

    if user.id == me.id:
        await client.update_message(event, "`I can't gban myself`!")
        return

    if user.username:
        banned_user = f"@{user.username}"
    else:
        banned_user = user.first_name

    connection = engine.connect()
    query = db.select([gbans_tbl]).where(gbans_tbl.columns.user_id == user.id)
    extract_db_user = connection.execute(query).fetchall()
    if extract_db_user:
        for user_data in extract_db_user:
            if user_data[0]:
                if reason:
                    await client.update_message(event, f"`This user is already banned but I will update the gban reason`.")
                    query = db.update(gbans_tbl).where(
                        gbans_tbl.columns.user_id == user.id).values(
                        reason=reason)
                    connection.close()
                    _load_gbanned_users()
                    return
                else:
                    await client.update_message(event, "`This user is already gbanned. You can update the gban reason by sending another one`.")
                    connection.close()
                    return

    query = db.insert(gbans_tbl).values(user_id=user.id, reason=reason)
    connection.execute(query)
    connection.close()

    if reason:
        await client.update_message(event, f"__Gbanned:__ `{banned_user}`"
                                    f"\n__Reason:__{reason}"
                                    "\n**This user will be banned in any chat I'm admin and the owner allows/allowed global bans from this companion.="
                                    " using** `.enablegbans` **command**.")
    else:
        await client.update_message(event, f"__Gbanned:__ `{banned_user}`"
                                    "\n**This user will be banned in any chat I'm admin and the owner allows/allowed global bans from this companion"
                                    " using** `.enablegbans` **command**.")
    _load_gbanned_users()


@client.CommandHandler(outgoing=True, command="ungban")
async def un_gban(event):
    """
    **Globally uban any user.**
        __Usage:__
            Reply to or mention a user to globally unban him.
            **Because of the API limitations, you'll need to manually unban the user from your chats.**
    """
    me = await client.get_me()

    del_cmd_text = event.text.split("gban", 1)[1]
    split_text = del_cmd_text.split(None, 1)

    if event.reply_to_msg_id:
        rep_msg = await event.get_reply_message()
        user = await rep_msg.get_sender()

    else:
        if len(split_text) == 0:
            await client.update_message(event, "`I don't have any user to gban.`")
            return

        try:
            user = await client.get_entity(split_text[0])
        except Exception:
            await client.update_message(event, f"`I don't seem to find this user by {split_text[1]}`.")
            return

    if user.id == me.id:
        await client.update_message(event, "`You can't ungban myself.`")
        return

    if user.username:
        unbanned_user = f"@{user.username}"
    else:
        unbanned_user = user.first_name

    connection = engine.connect()
    query = db.select([gbans_tbl]).where(gbans_tbl.columns.user_id == user.id)
    extract_db_user = connection.execute(query).fetchall()
    if extract_db_user:
        query = gbans_tbl.delete().where(
            gbans_tbl.columns.user_id == user.id)
        connection.execute(query)
        await client.update_message(event, f"__Ungbanned:__ `{unbanned_user}`"
                                    "\n**This user have been deleted from the globally banned users database"
                                    " but because of the API limitation you need to manually ungban him in any chat you want him to join again**.")

    else:
        await client.update_message(event, "`This user isn't globally banned`.")
    connection.close()
    _load_gbanned_users()


@client.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        chats=GBAN_ALLOWED_CHATS,
        from_users=[id for id, _ in GBANNED_USERS.items()]))
async def ban_on_msg(event):
    chat = await event.get_chat()
    user = await event.get_sender()
    reason = GBANNED_USERS.get(user.id)
    if reason:
        await client.update_message(event, "**This user is curently banned on this companion and it shouldn't be here**\n"
                                    f"__Reason:__ {reason}.")
    else:
        await client.update_message(event, "**This user is curently banned on this companion and it shouldn't be here**.")
    rights = ChatBannedRights(
        until_date=None,
        view_messages=True,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True
    )
    await client(EditBannedRequest(chat.id, user, rights))


@client.on(events.ChatAction(chats=GBAN_ALLOWED_CHATS))
async def ban_on_join(event):
    chat = await event.get_chat()
    user = await event.get_user()
    if event.user_joined:
        if chat.creator or chat.admin_rights:
            if user.id in GBANNED_USERS:
                reason = GBANNED_USERS.get(user.id)
                if reason:
                    await client.update_message(event, "**This user is curently banned on this companion and it shouldn't be here**\n"
                                                f"__Reason:__ {reason}.")
                else:
                    await client.update_message(event, "**This user is curently banned on this companion and it shouldn't be here**.")
                rights = ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
                )
                await client(EditBannedRequest(chat.id, user, rights))


@client.on(
    events.NewMessage(
        outgoing=True,
        incoming=True,
        pattern=r"\.disablegbans"))
async def disable_gbans(event):
    if not await event.get_reply_message() or (await event.get_reply_message()).id != (await client.get_me()).id:
        return

    chat = await event.get_chat()
    user = await event.get_sender()
    for admin in await client.get_participants(chat.id, filter=ChannelParticipantsAdmins):
        if isinstance(admin.participant, ChannelParticipantCreator):
            if user.id == admin.participant.user_id:
                connection = engine.connect()
                query = db.select(
                    [gban_chats_tbl]).where(
                    gban_chats_tbl.columns.chat_id == chat.id)
                for row in connection.execute(query).fetchall():
                    if row:
                        if row[1] is True:
                            query = db.update(
                                [gban_chats_tbl]).where(
                                gban_chats_tbl.columns.chat_id == chat.id).values(
                                is_enabled=False)
                            await event.reply("`Disabled global bans from this companion.\n`"
                                              "**Because of the API limitations you'll need to manually unban gbanned users from this group**.")
                            connection.execute(query)
                            connection.close()
                            _load_gban_enabled_chats()
                            return
                    else:
                        await event.reply("This chat doesn't have the companion's global bans enabled.")
            
            await client.event.reply("`Only chat owners can disable global bans from this companion`!")
            


@client.on(
    events.NewMessage(
        outgoing=True,
        incoming=True,
        pattern=r"\.enablegbans"))
async def enable_gbans(event):
    if not await event.get_reply_message() or (await event.get_reply_message()).id != (await client.get_me()).id:
        return

    chat = await event.get_chat()
    user = await event.get_sender()
    for admin in await client.get_participants(chat.id, filter=ChannelParticipantsAdmins):
        if isinstance(admin.participant, ChannelParticipantCreator):
            if user.id == admin.participant.user_id:
                connection = engine.connect()
                query = db.select(
                    [gban_chats_tbl]).where(
                    gban_chats_tbl.columns.chat_id == chat.id)
                for row in connection.execute(query).fetchall():
                    if row:
                        if row[1] is False:
                            query = db.update(
                                [gban_chats_tbl]).where(
                                gban_chats_tbl.columns.chat_id == chat.id).values(
                                is_enabled=True)
                            await event.reply("`Enabled global bans from this companion\n`"
                                              "**Because of the API limitations you'll need to manually unban gbanned users from this group**.")
                        else:
                            await event.reply("This chat already has enabled the companion's global bans")
                    else:
                        query = db.insert(gban_chats_tbl).values(
                            chat_id=chat.id, is_enabled=True)
                    connection.execute(query)
                    connection.close()
                    _load_gban_enabled_chats()
                    return
            await event.reply("`Only chat owners can enable global bans from this companion`!")



@client.CommandHandler(incoming=True, outgoing=True, command="enablegbans")
async def cmd_enable_gbans(event):
    """
    **Enable global bans from a companion**
    __Usage:__
        Reply to a user that has a companion. Works only on reply and only the owner can use it
        even if he's not using the companion.
    """
    return await enable_gbans(event)


@client.CommandHandler(incoming=True, outgoing=True, command="disablegbans")
async def cmd_disable_gbans(event):
    """
    **Disable global bans from a companion**
    __Usage:__
        Reply to a user that has a companion. Works only on reply and only the owner can use it
        even if he's not using the companion.
    """
    return await disable_gbans(event)
