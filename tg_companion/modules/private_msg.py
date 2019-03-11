import sqlalchemy as db
from telethon.tl.functions.contacts import BlockRequest

from tg_companion import BLOCK_PM, NOPM_SPAM
from tg_companion.tgclient import DB_URI, client

PM_WARNS = {}


ACCEPTED_USERS = []

engine = db.create_engine(DB_URI)
metadata = db.MetaData()

private_messages_tbl = db.Table("private_messages", metadata,
                                db.Column("chat_id", db.Integer()))


connection = engine.connect()

metadata.create_all(
    bind=engine,
    tables=[private_messages_tbl],
    checkfirst=True)

query = db.select([private_messages_tbl])
load_privates = connection.execute(query).fetchall()
for row in load_privates:
    if row:
        ACCEPTED_USERS.append(row[0])


@client.CommandHandler(incoming=True, func=lambda e: BLOCK_PM and e.is_private)
async def block_pm(event):
    sender = await event.get_sender()
    if BLOCK_PM and not sender.bot:
        chat = await event.get_chat()
        if chat.id not in ACCEPTED_USERS:
            await client(BlockRequest(chat.id))


@client.CommandHandler(
    incoming=True,
    func=lambda e: not BLOCK_PM and e.is_private)
async def await_permission(event):
    global PM_WARNS
    global ACCEPTED_USERS
    sender = await event.get_sender()

    if NOPM_SPAM and not sender.bot:
        me = await client.get_me()
        chat = await event.get_chat()
        if chat.id not in ACCEPTED_USERS and chat.id != me.id:

            if chat.id not in PM_WARNS:
                PM_WARNS.update({chat.id: 0})

            if PM_WARNS[chat.id] == 3:
                await client.send_message(
                    chat.id,
                    message="You are spamming this user. I will ban you until he decides to unban you. Thanks "
                )
                await client(BlockRequest(chat.id))
                return

            await client.send_message(
                chat.id,
                message="`Hi! This user will answer to your message soon. Please wait for his response and don't spam his PM. Thanks`"
            )

            PM_WARNS[chat.id] += 1


@client.CommandHandler(outgoing=True, command="approve")
async def accept_permission(event):
    """
    **Aprove a private message from a user. Works only if NOPM_SPAM is enabled in config.env or exported!**
        __Usage:__
            Send in in PM of any unaproved user. **Works only in private!**
    """
    chat = await event.get_chat()
    if NOPM_SPAM or BLOCK_PM:
        if event.is_private:
            if chat.id not in ACCEPTED_USERS:

                if chat.id in PM_WARNS:
                    del PM_WARNS[chat.id]
                connection = engine.connect()
                query = db.insert(private_messages_tbl).values(chat_id=chat.id)
                ACCEPTED_USERS.append(chat.id)
                connection.execute(query)
                connection.close()
                await client.update_message(event, "Private Message Accepted")
