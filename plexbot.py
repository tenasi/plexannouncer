import aiohttp
import asyncio
import urllib
import discord
import io
import datetime
import json

async def handle(request):
    if not request.content_type == "multipart/form-data":
        return aiohttp.web.Response()
    
    reader = await request.multipart()
    metadata = None
    thumbnail = None
    while True:
        part = await reader.next()
        if part is None: break
        if part.headers[aiohttp.hdrs.CONTENT_TYPE] == "application/json":
            metadata = await part.json()
            continue
        thumbnail = await part.read(decode=False)

    handle_plex_events(metadata, thumbnail)

    return aiohttp.web.Response()

def handle_plex_events(metadata, thumbnail):
    event = metadata["event"]
    if event == "library.new":
        handle_library_new(metadata["Metadata"], thumbnail)

def handle_library_new(metadata, thumbnail):
    ptype = metadata["type"]
    if ptype == "movie":
        handle_new_movie(metadata, thumbnail)
    elif ptype == "show":
        handle_new_show()
    elif ptype == "track":
        handle_new_track()
    else:
        print(f"ERROR: Unknown ptype {ptype}")

def handle_new_movie(metadata, thumbnail):
    thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
    key = urllib.parse.quote(metadata["key"])
    embed = discord.Embed()
    embed.title = f"New Movie: {metadata['title']}"
    embed.set_thumbnail(url="attachment://cover.jpg")
    if "summary" in metadata:
        embed.description = metadata["summary"]
    if "duration" in metadata:
        embed.add_field(name="Duration", value=str(datetime.timedelta(0,0,0,metadata["duration"])))
    if "year" in metadata:
        embed.add_field(name="Year", value=metadata["year"])
    if "rating" in metadata:
        embed.add_field(name="Rating", value=metadata["rating"])
    embed.url = f"{PLEX_SERVER_URL}/details?key={key}"
    embed.color = 0xe5a00d
    webhook.send(embed=embed, file=thumbnail)

def handle_new_show():
    pass

def handle_new_track():
    pass
        
if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as cfg:
        cfgdict = json.load(cfg)

    PLEX_SERVER_URL = cfgdict["plex_server_url"]
    PLEX_WEBHOOK_TOKEN = cfgdict["plex_webhook_token"]
    PLEX_WEBHOOK_PORT = cfgdict["plex_webhook_port"]
    DISCORD_WEBHOOK_ID = cfgdict["discord_webhook_id"]
    DISCORD_WEBHOOK_TOKEN = cfgdict["discord_webhook_token"]
    
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post(f"/{PLEX_WEBHOOK_TOKEN}", handle)])
    webhook = discord.Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN, adapter=discord.RequestsWebhookAdapter())
    aiohttp.web.run_app(app, port=PLEX_WEBHOOK_PORT)