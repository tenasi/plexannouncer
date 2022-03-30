import aiohttp
import os
from aiohttp import web

from config import Config, ConfigError
from announcer import Announcer


async def handle(request):
    """Handle inbound request for web server"""
    print("Inbound request", flush=True)
    # discard all requests not of type multipart/form-data
    if not request.content_type == "multipart/form-data":
        print(
            "Request rejected. Invalid content type, possibly not from plex.",
            flush=True,
        )
        return web.Response()

    # try reading attached thumbnail
    try:
        reader = await request.multipart()
        metadata = None
        thumbnail = None
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.headers[aiohttp.hdrs.CONTENT_TYPE] == "application/json":
                metadata = await part.json()
                continue
            thumbnail = await part.read(decode=False)
    except Exception:
        print("Request rejected. Error reading thumbnail.", flush=True)
        return web.Response()

    # try reading event type
    try:
        event = metadata["event"]
    except KeyError:
        print(
            "Request rejected. No event type specified, possibly not from plex.",
            flush=True,
        )
        return web.Response()

    # check if event is library.new event and handle it accordingly
    if event == "library.new":
        try:
            handle_library_new(metadata["Metadata"], thumbnail)
        except Exception:
            print("Error handling library.new event.", flush=True)
    else:
        print(f"Request rejected. Event type of {event}.")

    return web.Response()


def handle_library_new(metadata, thumbnail):
    """Check added type and call designated handler method"""
    library = metadata["librarySectionTitle"]
    if ALLOWED_LIBRARIES:
        if library not in ALLOWED_LIBRARIES:
            print(f"Ignoring library.new event from library {library}", flush=True)
            return
    ptype = metadata["type"]
    if ptype == "movie":
        print("Handling new movie announcement.", flush=True)
        announcer.announce_movie(metadata, thumbnail)
    elif ptype == "show":
        print("Handling new show announcement.", flush=True)
        announcer.announce_show(metadata, thumbnail)
    elif ptype == "track":
        print("Handling new track announcement.", flush=True)
        announcer.announce_track(metadata, thumbnail)
    else:
        print(f"ERROR: Unknown ptype {ptype}", flush=True)


if __name__ == "__main__":

    try:
        config = Config()
        announcer = Announcer(
            config.get_discord_webhook_urls(), config.get_plex_server_url()
        )
        ALLOWED_LIBRARIES = config.get_allowed_libraries()
        PLEX_WEBHOOK_TOKEN = config.get_plex_webhook_token()
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
    web.run_app(app, port=32500)
