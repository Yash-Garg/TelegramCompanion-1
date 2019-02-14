from telethon import events
import datetime
from tg_companion.tgclient import client, CMD_HANDLER


USER_AFK = {}
afk_time = None

@client.CommandHandler(outgoing=True, command="afk?(.+)")
@client.log_exception
async def afk(event):
    global afk_time
    reason = event.pattern_match.group(1)
    if len(reason) <= 2:
        reason = ""
    if not USER_AFK:
        afk_time = datetime.datetime.now()
        USER_AFK.update({"yes": reason})
        if reason:
            await event.edit(f"**I will be afk for a while.** \n __Reason__: {reason}")
            return

        await event.edit(f"**I will be afk for a while.**")

@client.CommandHandler(
                outgoing=True,
                func=lambda e: True if f"{CMD_HANDLER}afk" not in e.message.text else False)
@client.log_exception
async def no_afk(event):
    chat = await event.get_chat()
    if "yes" in USER_AFK:
        await client.send_message(chat.id, "`I'm no longer afk`")
        del USER_AFK["yes"]

@client.CommandHandler(
                incoming=True,
                func=lambda e: True if e.mentioned or e.is_private else False)
@client.log_exception
async def reply_afk(event):
    global afk_time
    chat = await event.get_chat()
    if event.mentioned or event.is_private:
        if USER_AFK:
            reason = USER_AFK["yes"]
            now = datetime.datetime.now()

            dt = now - afk_time
            days, hours, minutes, seconds = dt.days, dt.seconds // 3600, dt.seconds // 60, dt.seconds

            if days == 1:
                afk_since = "**Yesterday**"
            elif days > 1:
                if days > 6:
                    date = now + datetime.timedelta(days=-days, hours=-hours, minutes=-minutes)
                    afk_since = date.strftime('%A, %Y %B %m, %H:%I')
                else:
                    wday = now + datetime.timedelta(days=-days)
                    afk_since = wday.strftime('%A')
            elif hours > 1:
                afk_since = f"`{hours}h{minutes}m` **ago**"
            elif minutes > 0:
                afk_since = f"`{minutes}m{seconds}s` **ago**"
            else:
                afk_since = f"`{seconds}s` **ago**"


            if not reason:
                await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**", reply_to=event.id)
                return

            await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**"
                                      f" \n__Reason:__ {reason}", reply_to=event.id)
