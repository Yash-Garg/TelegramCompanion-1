from io import BytesIO

import sqlalchemy as db
from telethon.tl.types import (DocumentAttributeFilename,
                               InputMediaUploadedDocument, MessageMediaPhoto)

from tg_companion.tgclient import DB_URI, client

engine = db.create_engine(DB_URI)
metadata = db.MetaData()

notes_tbl = db.Table("global_notes", metadata,
                     db.Column("notename", db.String()),
                     db.Column("notetext", db.String()),
                     db.Column("file", db.LargeBinary()),
                     db.Column("filetype", db.String()),
                     db.Column("filename", db.String()),
                     db.Column("mimetype", db.String()))

metadata.create_all(engine, [notes_tbl], checkfirst=True)


@client.CommandHandler(outgoing=True, command="save")
async def save_note(event):
    """
    **Globally save a note.**
        __Args:__
            `<notename>` `<notecontent>` The notecontent argument is required only if you don't reply to a message.
    """
    message = event.message
    split_text = event.text.split(None, 2)

    if event.reply_to_msg_id:
        message = await event.get_reply_message()
        if len(split_text) == 1:
            await client.update_message(event, save_note.__doc__)
            return
        note_name = split_text[1]
        note_text = message.text
    else:
        if len(split_text) <= 2:
            await client.update_message(event, event, save_note.__doc__)
            return
        note_text = split_text[2]

    note_name = split_text[1]
    msg_file = None
    file_type = None
    file_name = None
    mime_type = None
    if message.media or message.document:
        msg_file = message.document or message.media
        if message.media and not message.document:
            if isinstance(message.media, MessageMediaPhoto):
                file_type = "media"
                file_name = "unknown.png"
                mime_type = "image/png"
            else:
                await event.reply("Unsuported Media Type")
        if message.document:
            file_type = "document"
            mime_type = message.document.mime_type
            for attribute in message.document.attributes:
                if isinstance(attribute, DocumentAttributeFilename):
                    file_name = attribute.file_name

    if msg_file:
        msg_file = await client.download_file(msg_file)
        msg_file = msg_file
    with engine.connect() as conn:
        query = (
            db.select(
                [notes_tbl]).where(
                notes_tbl.columns.notename == note_name))
        if conn.execute(query).fetchall():
            query = (
                db.update(notes_tbl).where(
                    notes_tbl.columns.notename == note_name).values(
                    notename=note_name,
                    notetext=note_text,
                    file=msg_file,
                    filetype=file_type,
                    filename=file_name,
                    mimetype=mime_type,
                ))
        else:
            query = (
                db.insert(notes_tbl).values(
                    notename=note_name,
                    notetext=note_text,
                    file=msg_file,
                    filetype=file_type,
                    filename=file_name,
                    mimetype=mime_type))
        conn.execute(query)
    await client.update_message(event, f"Globally saved `{note_name}`. Get it using the command `get {note_name}`")


@client.CommandHandler(outgoing=True, command="get")
async def get_note(event):
    """
    **Get a globally saved note.**
        __Args:__
            `<notename>` - The name of the note.
    """
    split_text = event.text.split(None, 1)
    chat = await event.get_chat()

    if len(split_text) == 1:
        await client.update_message(event, get_note.__doc__)
        return

    note_name = split_text[1]
    note_text = None
    msg_file = None
    file_type = None
    file_name = None
    mime_type = None

    with engine.connect() as conn:
        query = (
            db.select(
                [notes_tbl]).where(
                notes_tbl.columns.notename == note_name))
        for row in conn.execute(query).fetchall():
            note_text = row.notetext
            msg_file = row.file
            file_type = row.filetype
            file_name = row.filename
            mime_type = row.mimetype
    if msg_file:
        with BytesIO(msg_file) as mem_file:
            uploaded_file = await client.upload_file(mem_file.read(), file_name=file_name)
            if file_type == "document":
                await client.send_file(chat.id, InputMediaUploadedDocument(file=uploaded_file, mime_type=mime_type, attributes=[DocumentAttributeFilename(file_name)]), caption=note_text, force_document=True)
            else:
                mem_file.name = "photo.png"
                file_name = "photo.png"
                await client.send_file(chat.id, uploaded_file, caption=note_text)
            return
    await client.update_message(event, note_text)


@client.CommandHandler(outgoing=True, command="remove")
async def remove_note(event):
    """
    **Remove a globally saved note.**
        __Args:__
            `<notename>` - The name of the note.
    """
    split_text = event.text.split(None, 1)

    if len(split_text) == 1:
        await client.update_message(event, remove_note.__doc__)
        return
    note_name = split_text[1]

    query = (
        db.select(
            [notes_tbl]).where(
            notes_tbl.columns.notename == note_name))
    with engine.connect() as conn:
        if not conn.execute(query).fetchall():
            await client.update_message(event, "`There's no note with that name`")
            return
        query = notes_tbl.delete().where(notes_tbl.columns.notename == note_name)
        conn.execute(query)
    await client.update_message(event, f"Deleted `{note_name}` from database")


@client.CommandHandler(outgoing=True, command="notes")
async def list_notes(event):
    """
    **Get a list with all of the globally saved notes.**
    """
    listnotes = []
    with engine.connect() as conn:
        query = (db.select([notes_tbl]))
        for row in conn.execute(query).fetchall():
            listnotes.append(row.notename)
    if not listnotes:
        await client.update_message(event, "`There are no notes saved`")
        return
    await client.update_message(event, "`Globally saved notes:`\n-" + "\n-".join(listnotes))
