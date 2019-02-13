from telethon import events

from tg_companion.tgclient import client

USER_AFK = {}


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk?(.+)"))
@client.log_exception
async def afk(event):
    reason = event.pattern_match.group(1)
    if len(reason) <= 2:
        reason = ""
    if not USER_AFK:
        USER_AFK.update({"yes": reason})
        if reason:
            await event.edit(f"**I will be afk for a while.** \n __Reason__: {reason}")
            return

        await event.edit(f"**I will be afk for a while.**")


@client.on(
    events.NewMessage(
        outgoing=True,
        func=lambda e: True if ".afk" not in e.message.text else False))
@client.log_exception
async def no_afk(event):
    chat = await event.get_chat()
    if "yes" in USER_AFK:
        await client.send_message(chat.id, "`I'm no longer afk`")
        del USER_AFK["yes"]


@client.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: True if e.mentioned or e.is_private else False))
@client.log_exception
async def reply_afk(event):
    chat = await event.get_chat()
    if USER_AFK:
        reason = USER_AFK["yes"]
        if not reason:
            await client.send_message(chat.id, "**I'm afk and I will be back soon**", reply_to=event.id)
            return

        await client.send_message(chat.id, f"**I'm afk and I will be back soon**\n__Reason:__: {reason}", reply_to=event.id)
