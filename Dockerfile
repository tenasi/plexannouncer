FROM python:3

VOLUME /config

WORKDIR /plexannouncer

COPY plexannouncer.py requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./plexannouncer.py" ]