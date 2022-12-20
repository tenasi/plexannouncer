FROM python:3

WORKDIR /plexannouncer

COPY ./requirements.txt .devcontainer/dev-requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r dev-requirements.txt

EXPOSE 32500/tcp