import datetime

from tg_companion.tgclient import CMD_HANDLER, client
from telethon.tl.functions.account import GetPrivacyRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, PrivacyValueAllowContacts

AFK_HELP = """
    **Mark yourself as AFK.**
        __Args:__
            `<reason>` - **(optional)** __Optional afk reason__
"""

USER_AFK = {}
ALLOW_SEEN_STATUS = None
afk_time = None


intervals = (
    ('weeks', 604800),
    ('days', 86400),
    ('hours', 3600),
    ('minutes', 60),
    ('seconds', 1),
    )


@client.CommandHandler(outgoing=True, command="afk", help=AFK_HELP)
@client.log_exception
async def afk(event):
    global afk_time
    global ALLOW_SEEN_STATUS

    reason = None
    split_text = event.text.split(None, 1)

    if len(split_text) > 1:
        reason = split_text[1]

    if not USER_AFK:
        last_seen_status = await client(GetPrivacyRequest(InputPrivacyKeyStatusTimestamp()))
        if last_seen_status.rules or not isinstance(last_seen_status.rules, PrivacyValueAllowContacts):
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
    afk_since = "**a while ago**"

    if event.mentioned or event.is_private:
        if USER_AFK:
            reason = USER_AFK["yes"]
            if afk_time:
                now = datetime.datetime.now()

                dt = now - afk_time
                time = float(dt.seconds)
                days = time // (24 * 3600)
                time = time % (24 * 3600)
                hours = time // 3600
                time %= 3600
                minutes = time // 60
                time %= 60
                seconds = time

                if days == 1:
                    afk_since = "**Yesterday**"
                elif days > 1:
                    if days > 6:
                        date = now + \
                            datetime.timedelta(days=-days, hours=-hours, minutes=-minutes)
                        afk_since = date.strftime('%A, %Y %B %m, %H:%I')
                    else:
                        wday = now + datetime.timedelta(days=-days)
                        afk_since = wday.strftime('%A')
                elif hours > 1:
                    afk_since = f"`{int(hours)}h{int(minutes)}m` **ago**"
                elif minutes > 0:
                    afk_since = f"`{int(minutes)}m{int(seconds)}s` **ago**"
                else:
                    afk_since = f"`{int(seconds)}s` **ago**"

            if not reason:
                await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**", reply_to=event.id)
                return

            await client.send_message(chat.id, f"**I'm afk since** {afk_since} **and I will be back soon**"
                                      f" \n__Reason:__ {reason}", reply_to=event.id)
