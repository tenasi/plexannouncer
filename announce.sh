#!/bin/sh
curl -d "$1" -X POST -H "Content-Type: text/plain" http://localhost:32500/$PLEX_WEBHOOK_TOKEN