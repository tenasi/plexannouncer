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
import re

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



class ConfigError(Exception):
    pass

def _get_key(key: str, config: dict):
    if key in config:
        return config[key]
    elif key.upper() in config:
        return config[key.upper()]
    elif key.lower() in config:
        return config[key.lower()]
    raise ConfigError(f"{key} is not defined")

def _get_discord_webhook_id(config: dict):
    discord_webhook_id = _get_key("discord_webhook_id", config)
    if not discord_webhook_id.isnumeric():
        raise ConfigError("Invalid discord webhook id")
    return discord_webhook_id
    
def _get_discord_webhook_token(config: dict):
    discord_webhook_token = _get_key("discord_webhook_token", config)
    if re.fullmatch(r"[a-zA-Z0-9-_]*", discord_webhook_token) is None:
        raise ConfigError("Invalid discord webhook token")
    return discord_webhook_token
    
def _get_plex_webhook_token(config: dict):
    plex_webhook_token = _get_key("plex_webhook_token", config)
    if re.fullmatch(r"[a-zA-Z0-9-_]*", plex_webhook_token) is None:
        raise ConfigError("Invalid plex webhook token")
    return plex_webhook_token

def _get_plex_server_url(config: dict):
    plex_server_url = _get_key("plex_server_url", config)
    if re.search(r"\/desktop#!\/server\/[a-zA-Z0-9]*\/?$", plex_server_url) is None:
        raise ConfigError("Invalid plex server url")
    return plex_server_url

def _get_discord_webhook_url(config: dict):
    discord_webhook_url = _get_key("discord_webhook_url", config)
    if re.fullmatch(r"https://discord\.com/api/webhooks/[0-9]*/[a-zA-Z0-9-_]*$", discord_webhook_url) is None:
        raise ConfigError("Invalid discord webhook url")
    return discord_webhook_url

def _split_discord_webhook_url(discord_webhook_url):
    return discord_webhook_url.replace("https://discord.com/api/webhooks/", "").split("/")

if __name__ == "__main__":
    if pathlib.Path("/config/config.json").is_file():
        try:
            with open("/config/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            print("Error reading configuration, please check your config file")
            exit(-1)
    else:
        config = dict(os.environ)
    
    try:
        try:
            discord_webhook_url = _get_discord_webhook_url(config)
            DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN = _split_discord_webhook_url(discord_webhook_url)
        except ConfigError as e:
            print(e, flush=True)
            print("Falling back to manual discord webhook configuration", flush=True)
            DISCORD_WEBHOOK_ID = _get_discord_webhook_id(config)
            DISCORD_WEBHOOK_TOKEN = _get_discord_webhook_token(config)
        
        PLEX_WEBHOOK_TOKEN = _get_plex_webhook_token(config)
        PLEX_SERVER_URL = _get_plex_server_url(config)
        if PLEX_SERVER_URL.endswith("/"):
            PLEX_SERVER_URL = PLEX_SERVER_URL[:-1]
    except ConfigError as e:
        print(e, flush=True)
        exit(-1)

    port = "32500"
    if os.getenv("TCP_PORT_32500"):
        port = os.getenv("TCP_PORT_32500")
    # running web server and discord webhook client
    print(f"Plex webhook URL: http://localhost:{port}/{PLEX_WEBHOOK_TOKEN}", flush=True)
    app = web.Application()
    app.add_routes([web.post(f"/{PLEX_WEBHOOK_TOKEN}", handle)])
    webhook = discord.Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN, adapter=discord.RequestsWebhookAdapter())
    web.run_app(app, port=32500)
