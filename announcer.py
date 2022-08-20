import discord
import urllib.parse
import io
import datetime
import logging

log = logging.getLogger("announcer")
color = 0xE5A00D


class Announcer(object):
    def __init__(self, urls: list, plex: str) -> None:
        self.plex = plex
        self.webhooks = list()
        for url in urls:
            log.debug(f"Creating webhook for {url}")
            webhook = self._create_webhook(url)
            self.webhooks.append(webhook)

    def _create_webhook(self, url):
        return discord.SyncWebhook.from_url(url)

    def announce_movie(self, metadata, thumbnail):
        """Handle new movies added to plex"""
        log.debug("Announcing new movie")
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
        embed.color = color
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_show(self, metadata, thumbnail):
        """Handle new tv shows added to plex"""
        log.debug("Announcing new show")
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing show and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        key = key.replace("%2Fchildren", "")
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
        # set hyperlink to show on plex
        embed.url = f"{self.plex}/details?key={key}"
        embed.color = color
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_episode(self, metadata, thumbnail):
        """Handle new episodes added to plex"""
        log.debug("Announcing new episode")
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing show and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        key = key.replace("%2Fchildren", "")
        # build discord embed message
        embed = discord.Embed()
        embed.title = f"{metadata['grandparentTitle']}: {metadata['title']}"
        embed.set_thumbnail(url="attachment://cover.jpg")
        # add custom fields
        if "summary" in metadata:
            embed.description = metadata["summary"]
        if "index" in metadata and "parentIndex" in metadata:
            embed.add_field(name="Season", value=str(metadata["parentIndex"]))
            embed.add_field(name="Episode", value=str(metadata["index"]))
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
        embed.color = color
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_track(self, metadata, thumbnail):
        """Handle new music tracks added to plex"""
        log.debug("Announcing new track")
        # setup thumbnail object
        thumbnail = discord.File(io.BytesIO(thumbnail), "cover.jpg")
        # read key for identifing track and create link to plex
        key = urllib.parse.quote_plus(metadata["key"])
        # build discord embed message
        embed = discord.Embed()
        # TODO
        log.error("Tracks are not full< implemented yet")
        # set hyperlink to track on plex
        embed.url = f"{self.plex}/details?key={key}"
        embed.color = color
        # send embed message to discord
        for webhook in self.webhooks:
            webhook.send(embed=embed, file=thumbnail)

    def announce_custom(self, message):
        """Handle a custom announcement"""
        log.debug("Announcing custom message")
        # read alert icon
        with open("alert.png", "rb") as f:
            alert = discord.File(f, "alert.png")
            # build discord embed message
            embed = discord.Embed()
            embed.title = "Announcement"
            embed.set_thumbnail(url="attachment://alert.png")
            embed.description = message
            embed.color = color
            # send embed message to discord
            for webhook in self.webhooks:
                webhook.send(embed=embed, file=alert)
