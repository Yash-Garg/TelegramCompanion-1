import sqlalchemy as db

from tg_companion.tgclient import DB_URI, client

NOTES = {}

engine = db.create_engine(DB_URI)
metadata = db.MetaData()

notes_tbl = db.Table("notes", metadata,
                     db.Column("notename", db.String(), primary_key=True),
                     db.Column("note", db.String()))


metadata.create_all(engine, [notes_tbl], checkfirst=True)


def _load_notes():
    NOTES.clear()
    query = db.select([notes_tbl])
    connection = engine.connect()
    for row in connection.execute(query).fetchall():
        if row:
            NOTES.update({row[0]: row[1]})
    connection.close()


_load_notes()

SAVE_HELP = """
    **Globally save a note.**
        __Args:__
            `<notename>` `<notecontent>` **The notecontent argument is required only if you don't reply to a message**
"""

GET_HELP = """
    **Get a globally saved note.**
        __Args:__
            `<notename>`
"""

REMOVE_HELP = """
    **Remove a globally saved note.**
        __Args:__
            `<notename>`
"""


@client.CommandHandler(outgoing=True, command="save", help=SAVE_HELP)
async def save_note(event):
    split_text = event.text.split(None, 2)

    if event.reply_to_msg_id:
        repl_msg = await event.get_reply_message()
        if len(split_text) == 1:
            await event.edit(SAVE_HELP)
            return
        note_name = split_text[1]
        note_content = repl_msg.text

    else:
        if len(split_text) <= 2:
            await event.edit(SAVE_HELP)
            return

        note_name = split_text[1]
        note_content = split_text[2]

    connection = engine.connect()

    if note_name not in NOTES:
        query = db.insert(notes_tbl).values(
            notename=note_name, note=note_content)
    else:
        query = db.update(notes_tbl).where(
            notes_tbl.columns.notename == note_name).values(
            note=note_content)
    connection.execute(query)
    connection.close()

    await event.edit(f"Globally saved `{note_name}`. Get it with using the command `get {note_name}")
    _load_notes()


@client.CommandHandler(outgoing=True, command="get", help=GET_HELP)
async def get_note(event):
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await event.edit(GET_HELP)
        return

    note_name = split_text[1]

    if note_name not in NOTES:
        await event.edit("There's no note with that name")
        return

    await event.edit(NOTES.get(note_name))


@client.CommandHandler(outgoing=True, command="remove", help=REMOVE_HELP)
async def remove_note(event):
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await event.edit(REMOVE_HELP)
        return

    note_name = split_text[1]

    if note_name not in NOTES:
        await event.edit("There's no note with that name")
        return

    query = notes_tbl.delete().where(notes_tbl.columns.notename == note_name)
    connection = engine.connect()
    connection.execute(query)
    connection.close()
    _load_notes()
    await event.edit(f"Deleted `{note_name}` from database")
