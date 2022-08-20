FROM python:alpine

WORKDIR /plexannouncer

COPY main.py announcer.py config.py requirements.txt announce.sh .

RUN pip install --no-cache-dir -r requirements.txt && \
    mv announce.sh /usr/bin/announce

EXPOSE 32500/tcp

CMD [ "python", "./main.py" ]