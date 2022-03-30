FROM python:3

WORKDIR /plexannouncer

COPY main.py announcer.py config.py requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 32500/tcp

CMD [ "python", "./main.py" ]