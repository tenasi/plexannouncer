import aiohttp
from aiohttp import web
import asyncio
import urllib.parse
import discord
import io
import datetime
import json
import pathlib
import os
import random
import string

async def handle(request):
    """Handle inbound request for web server"""
    print("Inbound request", flush=True)
    # discard all requests not of type multipart/form-data
    if not request.content_type == "multipart/form-data":
        print("Request rejected invalid content type", flush=True)
        return web.Response()
    
    # try reading attached thumbnail
    try:
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
    except Exception:
        print("Error reading thumbnails, discarding request", flush=True)
        return web.Response()

    # try reading event type
    try:
        event = metadata["event"]
    except KeyError:
        print("Error handling inbound request, possibly not from plex", flush=True)
        return web.Response()

    # check if event is library.new event and handle it accordingly
    if event == "library.new":
        try:
            handle_library_new(metadata["Metadata"], thumbnail)
        except Exception:
            print("Error handling library.new event or quering metadata", flush=True)
    else:
        print("Ignoring request, event type not of library.new")

    return web.Response()

def handle_library_new(metadata, thumbnail):
    """Check added type and call designated handler method"""
    ptype = metadata["type"]
    if ptype == "movie":
        print("Handling new movie announcement", flush=True)
        handle_new_movie(metadata, thumbnail)
    elif ptype == "show":
        print("Handling new show announcement", flush=True)
        handle_new_show(metadata, thumbnail)
    elif ptype == "track":
        print("Handling new track announcement", flush=True)
        handle_new_track(metadata, thumbnail)
    else:
        print(f"ERROR: Unknown ptype {ptype}", flush=True)

def handle_new_movie(metadata, thumbnail):
    """Handle newly movies added to plex"""
    # setup thumbnail object
    thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
    # read key for identifing movie and create link to plex
    key = urllib.parse.quote_plus(metadata["key"])
    # build discord embed message
    embed = discord.Embed()
    embed.title = f"New Movie: {metadata['title']}"
    embed.set_thumbnail(url="attachment://cover.jpg")
    # add custom fields
    if "summary" in metadata:
        embed.description = metadata["summary"]
    if "duration" in metadata:
        embed.add_field(name="Duration", value=str(datetime.timedelta(0,0,0,metadata["duration"])))
    if "year" in metadata:
        embed.add_field(name="Year", value=metadata["year"])
    if "rating" in metadata:
        embed.add_field(name="Rating", value=metadata["rating"])
    # set hyperlink to movie on plex
    embed.url = f"{PLEX_SERVER_URL}/details?key={key}"
    embed.color = 0xe5a00d
    # send embed message to discord
    webhook.send(embed=embed, file=thumbnail)

def handle_new_show(metadata, thumbnail):
    """Handle newly tv shows added to plex"""
    # setup thumbnail object
    thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
    # read key for identifing show and create link to plex
    key = urllib.parse.quote_plus(metadata["key"])
    # build discord embed message
    embed = discord.Embed()
    # TODO
    # set hyperlink to show on plex
    embed.url = f"{PLEX_SERVER_URL}/details?key={key}"
    embed.color = 0xe5a00d
    # send embed message to discord
    webhook.send(embed=embed, file=thumbnail)

def handle_new_track(metadata, thumbnail):
    """Handle newly music tracks added to plex"""
    # setup thumbnail object
    thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
    # read key for identifing track and create link to plex
    key = urllib.parse.quote_plus(metadata["key"])
    # build discord embed message
    embed = discord.Embed()
    # TODO
    # set hyperlink to track on plex
    embed.url = f"{PLEX_SERVER_URL}/details?key={key}"
    embed.color = 0xe5a00d
    # send embed message to discord
    webhook.send(embed=embed, file=thumbnail)

def gen_token():
    """Generates a random token"""
    choices = string.ascii_letters + string.digits
    selection = [random.choice(choices) for _ in range(64)]
    return "".join(selection)

if __name__ == "__main__":
    # create default config if no config file found
    if not pathlib.Path("/config/config.json").is_file():
        with open("/plexannouncer/example_config.json", "r", encoding="utf-8") as default_cfg:
            current_cfg = default_cfg.read().replace("RANDOM_TOKEN", gen_token())
            with open("/config/config.json", "w", encoding="utf-8") as cfg:
                cfg.write(current_cfg)

    # try reading webhook configuration
    try:
        with open("/config/config.json", "r", encoding="utf-8") as cfg:
            cfgdict = json.load(cfg)

        PLEX_SERVER_URL = cfgdict["plex_server_url"]
        PLEX_WEBHOOK_TOKEN = cfgdict["plex_webhook_token"]
        DISCORD_WEBHOOK_ID = cfgdict["discord_webhook_id"]
        DISCORD_WEBHOOK_TOKEN = cfgdict["discord_webhook_token"]
        print(f"Plex webhook URL: http://localhost:32500/{PLEX_WEBHOOK_TOKEN}", flush=True)
    except Exception:
        print("Error reading configuration, please check your config file")
        exit()
    
    if not PLEX_SERVER_URL or PLEX_SERVER_URL.endswith("SERVERID"):
        print("Config error: Invalid plex server url")
        exit()
    if not DISCORD_WEBHOOK_ID or DISCORD_WEBHOOK_ID == "ID":
        print("Config error: Invalid discord webhook id")
        exit()
    if not DISCORD_WEBHOOK_TOKEN or DISCORD_WEBHOOK_TOKEN == "TOKEN":
        print("Config error: Invalid discord webhook token")
        exit()

    # running web server and discord webhook client
    print("Start listening on port 32500", flush=True)
    app = web.Application()
    app.add_routes([web.post(f"/{PLEX_WEBHOOK_TOKEN}", handle)])
    webhook = discord.Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN, adapter=discord.RequestsWebhookAdapter())
    web.run_app(app, port=32500)