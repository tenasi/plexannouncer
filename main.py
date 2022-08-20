import os
import logging
from aiohttp import web, hdrs

from config import Config, ConfigError
from announcer import Announcer

log = logging.getLogger("main")


async def handle(request):
    """Handle inbound request for web server"""
    log.info("Inbound request")

    # handle custom announcement
    if request.content_type == "text/plain":
        message = await request.read()
        message = message.decode("utf-8")
        announcer.announce_custom(message)
        log.info("Handling custom announcement")
        return web.Response()

    # discard all other requests not of type multipart/form-data
    if not request.content_type == "multipart/form-data":
        log.info("Request rejected: Invalid content type, possibly not from plex")
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
            if part.headers[hdrs.CONTENT_TYPE] == "application/json":
                metadata = await part.json()
                continue
            thumbnail = await part.read(decode=False)
    except Exception:
        log.info("Request rejected: Error reading thumbnail")
        return web.Response(status=400)

    # try reading event type
    try:
        event = metadata["event"]
    except KeyError:
        log.info("Request rejected: No event type specified, possibly not from plex")
        return web.Response()

    # check if event is library.new event and handle it accordingly
    if event == "library.new":
        try:
            handle_library_new(metadata["Metadata"], thumbnail)
        except Exception as e:
            log.error("Error handling library.new event")
            log.exception(e)
            return web.Response(status=400)
    else:
        log.info(f"Request rejected. Event type of {event}")

    return web.Response()


def handle_library_new(metadata, thumbnail):
    """Check added type and call designated handler method"""
    log.debug(metadata)
    library = metadata["librarySectionTitle"]
    if ALLOWED_LIBRARIES:
        if library not in ALLOWED_LIBRARIES:
            log.info(f"Ignoring library.new event from library {library}")
            return
    ptype = metadata["type"]
    if ptype == "movie":
        log.info("Handling new movie announcement")
        announcer.announce_movie(metadata, thumbnail)
    elif ptype == "show":
        log.info("Handling new show announcement")
        announcer.announce_show(metadata, thumbnail)
    elif ptype == "episode":
        log.info("Handling new show announcement")
        announcer.announce_episode(metadata, thumbnail)
    elif ptype == "track":
        log.info("Handling new track announcement")
        announcer.announce_track(metadata, thumbnail)
    else:
        log.error(f"ERROR: Unknown type {ptype}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=os.environ.get("LOGLEVEL", "INFO"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log.debug("Logger initialized")

    try:
        config = Config()
        announcer = Announcer(
            config.get_discord_webhook_urls(), config.get_plex_server_url()
        )
        ALLOWED_LIBRARIES = config.get_allowed_libraries()
        PLEX_WEBHOOK_TOKEN = config.get_plex_webhook_token()
    except ConfigError as e:
        log.critical(e, exc_info=True)
        exit(-1)

    # set default port as specified in Dockerfile
    port = "32500"
    # get actual port mapping from docker context
    if os.getenv("TCP_PORT_32500"):
        port = os.getenv("TCP_PORT_32500")
    # running web server and discord webhook client
    log.info(f"Plex webhook URL: http://localhost:{port}/{PLEX_WEBHOOK_TOKEN}")
    app = web.Application()
    app.add_routes([web.post(f"/{PLEX_WEBHOOK_TOKEN}", handle)])
    web.run_app(app, port=32500, access_log=None)
