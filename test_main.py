from aiohttp import web, FormData
from PIL import Image
import main
import pytest
import io
import json


def thumbnail():
    b = io.BytesIO()
    img = Image.new(mode="RGB", size=(1000, 1500), color=(255, 0, 255))
    img.save(b, "JPEG")
    b.seek(0)
    return b

@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_post("/", main.handle)
    return loop.run_until_complete(aiohttp_client(app))


async def test_get_request(cli):
    resp = await cli.post("/")
    assert resp.status == 200


async def test_no_event(cli):
    form = FormData()
    form.add_field("metadata", "{}", content_type="application/json")
    form.add_field("thumbnail", thumbnail())
    resp = await cli.post("/", data=form)
    assert resp.status == 200


async def test_unknown_event(cli):
    form = FormData()
    data = dict(event="unknown")
    form.add_field("metadata", json.dumps(data), content_type="application/json")
    form.add_field("thumbnail", thumbnail())
    resp = await cli.post("/", data=form)
    assert resp.status == 200


async def test_unknown_type(cli):
    form = FormData()
    main.ALLOWED_LIBRARIES = ""
    meta = dict(type="unknown", librarySectionTitle="Movies")
    data = dict(event="library.new", Metadata=meta)
    form.add_field("metadata", json.dumps(data), content_type="application/json")
    form.add_field("thumbnail", thumbnail())
    resp = await cli.post("/", data=form)
    assert resp.status == 200
