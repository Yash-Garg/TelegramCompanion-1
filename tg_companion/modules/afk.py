from telethon import events
import datetime
from tg_companion.tgclient import client


USER_AFK = {}
afk_time = None


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk?(.+)"))
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
    global afk_time
    chat = await event.get_chat()
    if event.mentioned or event.is_private:
        if USER_AFK:
            reason = USER_AFK["yes"]
            now = datetime.datetime.now()

            dt = now - afk_time
            offset = dt.seconds + (dt.days * 60 * 60 * 24)

            delta_s = int(offset % 60)
            offset /= 60
            delta_m = int(offset % 60)
            print(delta_m)
            offset /= 60
            delta_h = int(offset % 24)
            offset /= 24
            delta_d = int(offset)

            if int(delta_d) > 1:
                if delta_d > 6:
                    date = now + \
                        datetime.timedelta(days=-delta_d, hours=-delta_h, minutes=-delta_m)
                    print(date)
                    afk_since = date.strftime('%A, %Y %B %m, %H:%I')
                else:
                    wday = now + datetime.timedelta(days=-delta_d)
                    afk_since = wday.strftime('%A')
            if delta_d == 1:
                afk_since = "**Yesterday**"
            if delta_h > 0:
                afk_since = f"`{delta_h}h{delta_m}m` **ago**"
            if delta_m > 0:
                afk_since = f"`{delta_m}m{delta_s}s` **ago**"
            else:
                afk_since = f"`{delta_s}s` **ago**"

            if not reason:
                await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**", reply_to=event.id)
                return

            await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**"
                                      f" \n__Reason:__ {reason}", reply_to=event.id)
