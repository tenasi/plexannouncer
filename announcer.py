import discord
import urllib.parse
import io
import datetime


class Announcer(object):
    def __init__(self, urls: list, plex: str) -> None:
        self.plex = plex
        self.webhooks = list()
        for url in urls:
            id, token = self._parse_url(url)
            webhook = self._create_webhook(id, token)
            self.webhooks.append(webhook)

    def _parse_url(self, url):
        return (
            url.replace("https://discord.com/api/webhooks/", "")
            .replace("https://discordapp.com/api/webhooks/", "")
            .split("/")
        )

    def _create_webhook(self, id, token):
        return discord.Webhook.partial(
            id,
            token,
            adapter=discord.RequestsWebhookAdapter(),
        )

    def announce_movie(self, metadata, thumbnail):
        """Handle newly movies added to plex"""
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing movie and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        # build discord embed message
        embed = discord.Embed()
        embed.title = f"{metadata['title']}"
        embed.set_thumbnail(url="attachment://cover.jpg")
        # add custom fields
        if "summary" in metadata:
            embed.description = metadata["summary"]
        if "duration" in metadata:
            embed.add_field(
                name="Duration",
                value=str(datetime.timedelta(0, 0, 0, metadata["duration"])),
            )
        if "year" in metadata:
            embed.add_field(name="Year", value=metadata["year"])
        if "rating" in metadata:
            embed.add_field(name="Rating", value=metadata["rating"])
        # set hyperlink to movie on plex
        embed.url = f"{self.plex}/details?key={key}"
        embed.color = 0xE5A00D
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_show(self, metadata, thumbnail):
        """Handle newly tv shows added to plex"""
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing show and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        key = key.replace("%2Fchildren", "")
        # build discord embed message
        embed = discord.Embed()
        embed.title = f"New episodes of {metadata['title']}"
        embed.set_thumbnail(url="attachment://cover.jpg")
        # add custom fields
        if "summary" in metadata:
            embed.description = metadata["summary"]
        if "duration" in metadata:
            embed.add_field(
                name="Duration",
                value=str(datetime.timedelta(0, 0, 0, metadata["duration"])),
            )
        if "year" in metadata:
            embed.add_field(name="Year", value=metadata["year"])
        if "rating" in metadata:
            embed.add_field(name="Rating", value=metadata["rating"])
        # set hyperlink to show on plex
        embed.url = f"{self.plex}/details?key={key}"
        embed.color = 0xE5A00D
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_track(self, metadata, thumbnail):
        """Handle newly music tracks added to plex"""
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing track and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        # build discord embed message
        embed = discord.Embed()
        # TODO
        # set hyperlink to track on plex
        embed.url = f"{self.plex}/details?key={key}"
        embed.color = 0xE5A00D
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)
