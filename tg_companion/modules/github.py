import aiohttp
from telethon import events

from tg_companion.tgclient import client


@client.CommandHandler(outgoing=True, command="github (.*)")
@client.log_exception
async def github(event):

    URL = f"https://api.github.com/users/{event.pattern_match.group(1)}"
    chat = await event.get_chat()
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                await event.reply("`" + event.pattern_match.group(1) + " not found`")
                return

            result = await request.json()

            url = result.get("html_url", None)
            name = result.get("name", None)
            company = result.get("company", None)
            bio = result.get("bio", None)
            created_at = result.get("created_at", "Not Found")

            REPLY = f"""
            GitHub Info for `{event.pattern_match.group(1)}`

            Username: `{name}`
            Bio: `{bio}`
            URL: `{url}`
            Company: `{company}`
            Created at: `{created_at}`
            """
            if not result.get("repos_url", None):
                await client.send_message(chat.id, message=REPLY, reply_to=event.id, link_preview=False)
                return
            async with session.get(result.get("repos_url", None)) as request:
                result = request.json

                if request.status == 404:
                    await event.edit(REPLY)
                    return

                result = await request.json()

                REPLY += "\nRepos: \n\n"

                for nr in range(len(result)):
                    REPLY += f"  [{result[nr].get('name', None)}]({result[nr].get('html_url', None)})\n"

                await client.send_message(chat.id, message=REPLY, reply_to=event.id, link_preview=False)
