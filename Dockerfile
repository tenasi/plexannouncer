FROM python:3

VOLUME /config

WORKDIR /plexannouncer

COPY plexannouncer.py requirements.txt example_config.json .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 32500/tcp

CMD [ "python", "./plexannouncer.py" ]