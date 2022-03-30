import re
import os


class ConfigError(Exception):
    pass


class Config:
    def __init__(self) -> None:
        self.config = dict(os.environ)

    def _get_key(self, key: str, default: str = None):
        if key in self.config:
            return self.config[key]
        elif key.upper() in self.config:
            return self.config[key.upper()]
        elif key.lower() in self.config:
            return self.config[key.lower()]
        elif default is not None:
            return default
        raise ConfigError(f"{key.upper()} not specified")

    def get_plex_webhook_token(self):
        token = self._get_key("plex_webhook_token")
        if re.fullmatch(r"[a-zA-Z0-9-_]*", token) is None:
            raise ConfigError("Invalid plex webhook token")
        return token

    def get_plex_server_url(self):
        url = self._get_key("plex_server_url")
        if re.search(r"\/desktop#!\/server\/[a-zA-Z0-9]*\/?$", url) is None:
            raise ConfigError("Invalid plex server url")
        if url.endswith("/"):
            url = url[:-1]
        return url

    def get_discord_webhook_urls(self):
        urls = self._get_key(
            "discord_webhook_urls", self._get_key("discord_webhook_url", "")
        ).split(",")
        for url in urls:
            if (
                re.fullmatch(
                    r"https://discord(app)?\.com/api/webhooks/[0-9]*/[a-zA-Z0-9-_]*$",
                    url,
                )
                is None
            ):
                raise ConfigError(f"Invalid discord webhook url: {url}")
        if not urls:
            raise ConfigError("Please specify at least one discord webhook url")
        return urls

    def get_allowed_libraries(self):
        allowed_libraries = self._get_key("updated_libraries", "")
        return [lib.strip() for lib in allowed_libraries.split(",") if lib.strip()]
