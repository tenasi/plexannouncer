FROM python:3

WORKDIR /plexannouncer

COPY .devcontainer/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 32500/tcp