FROM python:alpine3.11

WORKDIR /plexannouncer

COPY main.py announcer.py config.py requirements.txt alert.png announce.sh .

RUN apk update && apk upgrade && apk add curl && \
    pip install --no-cache-dir -r requirements.txt && \
    mv announce.sh /usr/bin/announce && \
    chmod u+x /usr/bin/announce

EXPOSE 32500/tcp

CMD [ "python", "./main.py" ]