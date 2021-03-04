from aiohttp import web, hdrs, MultipartWriter, ClientSession
import asyncio
import urllib
import discord
import io
import datetime

PLEX_SERVER_URL="https://plex.tenasi.de/web/index.html#!/server/9343ce14020b85edb29c9b0058b76c78aace83cf"
PLEX_WEBHOOK_TOKEN="UIhxo1kQV6W65adqiO6TQLMwH9DqNTx7POo6xiI6SE2PEXnIemUpGZNf0L5f7mQX"
DISCORD_WEBHOOK_ID="817154178161573942"
DISCORD_WEBHOOK_TOKEN="LAlcPwYDSlOEPV-7xpxkkG9RgblqHnoIyglbe_tfGYZJnbQPO6PnI4FejoIVKqKxt1aw"

async def handle(request):
    if not request.content_type == "multipart/form-data":
        return web.Response()
    
    reader = await request.multipart()
    metadata = None
    thumbnail = None
    while True:
        part = await reader.next()
        if part is None: break
        if part.headers[hdrs.CONTENT_TYPE] == "application/json":
            metadata = await part.json()
            continue
        thumbnail = await part.read(decode=False)

    handle_plex_events(metadata, thumbnail)

    return web.Response()

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
        
app = web.Application()
app.add_routes([web.post(f"/{PLEX_WEBHOOK_TOKEN}", handle)])
webhook = discord.Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN, adapter=discord.RequestsWebhookAdapter())

if __name__ == '__main__':
    web.run_app(app, port=8000)
