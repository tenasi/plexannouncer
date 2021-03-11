# Plex Announcer

A Discord bot that sends updates about newly added Plex media to a Discord channel using webhooks.

## Getting Started

To get started you first have to setup a webhook within your discord server / channel settings and obtain the webhook url:
```
https://discord.com/api/webhooks/DISCORD_WEBHOOK_ID/DISCORD_WEBHOOK_TOKEN
```
For more information about how you create webhooks and what they are check [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Usage

First run the container to create a default config file with in your config folder:
```
docker run -v /path/to/config/dir:/config -p 32500:32500 tenasi/plexannouncer:latest
```

Edit your plex server url and insert your Discord webhook id and token you obtained from the url above.
```json
{
    "plex_server_url": "https://app.plex.tv/desktop#!/server/SERVERID",
    "plex_webhook_token": "RANDOM_TOKEN",
    "discord_webhook_id": "ID",
    "discord_webhook_token": "TOKEN"
}
```

Run the container again with the command above and register the bot in Plex under Settings/Webhooks with the link being:

```
http://IP:PORT/RANDOM_TOKEN
```

Note that the container bust me reachable from your plex host. If you running both of them on the same server just enter `localhost` instead. You can obtain the RANDOM_TOKEN from your generated config file or replace them in both places with your own token. Make sure to restart the container after any changes made to the configuration file.

## Sources

* [GitLab](https://gitlab.tenasi.de/tenasi/plex-announcer)
