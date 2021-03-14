# Plex Announcer

A Discord bot that sends updates about newly added Plex media to a Discord channel using webhooks.

## Getting Started

To get started you first have to setup a webhook within your discord server / channel settings and copy the webhook url.

For more information about how you create webhooks and what they are check [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Usage

Note that the container bust me accessible from your plex host. If you running both of them on the same server just enter `localhost` instead.

#### With Env Variables

Run the container and specify your PLEX_SERVER_URL, PLEX_WEBHOOK_TOKEN and DISCORD_WEBHOOK_URL as environment variables:
```bash
docker run -p 32500:32500 -e PLEX_SERVER_URL="https://app.plex.tv/desktop#!/server/SERVER_ID" -e PLEX_WEBHOOK_TOKEN="SOME_RANDOM_TOKEN" -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN" tenasi/plexannouncer:latest
```

#### With Config File

First create a config file somewhere and insert your plex server url, your Discord webhook url and some random token.
```json
{
    "plex_server_url": "https://app.plex.tv/desktop#!/server/SERVERID",
    "plex_webhook_token": "RANDOM_TOKEN",
    "discord_webhook_url": "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
}
```

Then run the container and point to your config folder:
```bash
docker run -v /path/to/config/dir:/config -p 32500:32500 tenasi/plexannouncer:latest
```

#### Register the Webhook in Plex

Register the bot in Plex under Settings/Webhooks with the link being:

```
http://IP:PORT/RANDOM_TOKEN
```

## Sources

* [GitHub](https://github.com/tenasi/plexannouncer)
