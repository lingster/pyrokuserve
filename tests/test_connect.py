# simple pytests to run some checks that sanic apis work
import pytest
import json
from pyrokuserve import app as sanicapp


@pytest.yield_fixture
def app():
    app = sanicapp
    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


# tests
async def test_list_roku_devices(test_cli):
    # resp = await sanic_server.get('/device/list')
    resp = await test_cli.get('/device/list')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json[0].get('host', None) is not None
    assert resp_json[0].get('port', None) is not None


async def test_list_commands(test_cli):
    resp = await test_cli.get('/device/0/commandlist')
    assert resp.status == 200
    expected = {'back', 'backspace', 'down', 'enter', 'forward', 'home', 'info', 'left', 'literal', 'play', 'replay',
                'reverse', 'right', 'search', 'select', 'up'}
    assert expected.issubset(set(resp.json[0]))


