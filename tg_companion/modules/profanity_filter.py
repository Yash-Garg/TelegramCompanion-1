import sqlalchemy as db
from profanity_check import predict

from tg_companion.tgclient import DB_URI, client

engine = db.create_engine(DB_URI)
metadata = db.MetaData()

profanity_tbl = db.Table("profanity", metadata,
                         db.Column("chat_id", db.Integer(), primary_key=True),
                         db.Column("profanity_filter", db.Boolean()))


connection = engine.connect()

metadata.create_all(
    bind=engine,
    tables=[profanity_tbl],
    checkfirst=True)

PROFANITY_CHECK_CHATS = []

PROFANITY_HELP = """
    **Toggle the profanity filter on/off.**
        __Args:__
            `<on/off>` - **(admin only)** **(optional)** __The state of the profanity filter.
                            If activated will delete any messages that contains profanity
                            from the chat where it was enabled
                            Will display the filter status in the chat if sent without any value.__
"""

query = db.select([profanity_tbl.columns.chat_id]).where(
    profanity_tbl.columns.profanity_filter == db.true())
load_profanity_tbl = connection.execute(query).fetchall()
for row in load_profanity_tbl:
    if row:
        PROFANITY_CHECK_CHATS.append(row[0])
connection.close()


@client.CommandHandler(
    outgoing=True,
    command="profanity",
    func=lambda e: not e.is_private)
async def profanity_switch(event):
    global PROFANITY_CHECK_CHATS
    chat = await event.get_chat()
    split_text = event.text.split(None, 1)

    if len(split_text) == 1 or len(split_text) > 2:
        await client.update_message(event, PROFANITY_HELP)
        return

    on_off = split_text[1]

    if not chat.admin_rights:
        await client.update_message(event, "I need admin righs to disable or enable the profanity filter in this chat.")
        return

    if on_off.lower() == "on":
        if chat.id in PROFANITY_CHECK_CHATS:
            await client.update_message(event, "The profanity filter is already on."
                                        " All the incoming messages containing profanity will be deleted.")
            return

        connection = engine.connect()
        query = db.select([profanity_tbl.columns.profanity_filter]).where(
            profanity_tbl.columns.chat_id == chat.id)

        load_profanity_tbl = connection.execute(query).fetchall()

        if load_profanity_tbl:
            for profanity_bool in load_profanity_tbl:
                if profanity_bool[0] is False:
                    query = db.update(profanity_tbl).where(
                        profanity_tbl.columns.chat_id == chat.id).values(
                        profanity_filter=True)
        else:
            query = db.insert(profanity_tbl).values(
                chat_id=chat.id, profanity_filter=True)

        PROFANITY_CHECK_CHATS.append(chat.id)
        connection.execute(query)
        connection.close()
        await client.update_message(event, "The profanity filter is on."
                                    " All the incoming messages containing profanity will be deleted.")

    if on_off.lower() == "off":
        if chat.id not in PROFANITY_CHECK_CHATS:
            await client.update_message(event, "The profanity filter is already off."
                                        " All the incoming messages containing profanity will be ignored.")
            return

        connection = engine.connect()
        query = db.select([profanity_tbl.columns.profanity_filter]).where(
            profanity_tbl.columns.chat_id == chat.id)

        load_profanity_tbl = connection.execute(query).fetchall()
        if load_profanity_tbl:
            for profanity_bool in load_profanity_tbl:  # query the result

                if profanity_bool[0] is True:
                    query = db.update(profanity_tbl).where(
                        profanity_tbl.columns.chat_id == chat.id).values(
                        profanity_filter=False)
        else:
            db.insert(profanity_tbl).values(
                chat_id=chat.id, profanity_filter=False)

        PROFANITY_CHECK_CHATS.remove(chat.id)
        connection.execute(query)
        connection.close()
        await client.update_message(event, "The profanity filter is off."
                                    " Users can use swear words here!")


@client.CommandHandler(
    incoming=True,
    outgoing=True,
    allow_edited=True,
    func=lambda e: not e.is_private)
async def check_profanity_filter(event):
    chat = await event.get_chat()
    text = event.text

    if chat.id in PROFANITY_CHECK_CHATS:
        if chat.admin_rights:
            if chat.admin_rights.delete_messages:
                if text:
                    predict_profanity = predict([text])
                    if predict_profanity[0] == 1:
                        await event.delete()


@client.CommandHandler(
    incoming=True,
    outgoing=True,
    command="profanity",
    func=lambda e: not e.is_private and not any(
        x in e.text for x in [
            "on",
            "off"]))
async def profanity_filter_status(event):
    chat = await event.get_chat()
    if chat.id in PROFANITY_CHECK_CHATS:
        await client.update_message(event, "The profanity filter is on."
                                    " All the incoming messages containing profanity will be deleted!")
    else:
        await client.update_message(event, "The profanity filter is off."
                                    " All the incoming messages containing profanity will be ignored!")
