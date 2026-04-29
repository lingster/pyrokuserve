"""Tests for pyrokuserve.py Sanic REST API routes."""
import sys
import pytest
from unittest.mock import MagicMock, patch

from tests.conftest import make_mock_device, MOCK_COMMANDS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_app_with_mock():
    """Import pyrokuserve with Roku.discover mocked out.

    Returns the module so tests can swap out rokuc.
    """
    import importlib
    if "pyrokuserve" not in sys.modules:
        with patch("roku.Roku.discover", return_value=[make_mock_device()]):
            import pyrokuserve as prs
    else:
        import pyrokuserve as prs
    return prs


# Ensure the app is importable before any test collects.
with patch("roku.Roku.discover", return_value=[make_mock_device()]):
    import pyrokuserve as _prs_module  # noqa: E402  (module-level, intentional)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sanic_app(mock_controller):
    """Sanic app with the module-level RokuController swapped for a mock."""
    _prs_module.rokuc = mock_controller
    yield _prs_module.app


# ---------------------------------------------------------------------------
# /device/list/
# ---------------------------------------------------------------------------

class TestDeviceList:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/list/")
        assert resp.status_code == 200

    async def test_returns_device_list(self, sanic_app, mock_controller):
        mock_controller.get_devices.return_value = [
            {"id": 0, "host": "192.168.1.100", "port": 8060}
        ]
        _, resp = await sanic_app.asgi_client.get("/device/list/")
        data = resp.json
        assert isinstance(data, list)
        assert data[0]["host"] == "192.168.1.100"
        assert data[0]["port"] == 8060

    async def test_calls_get_devices(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/list/")
        mock_controller.get_devices.assert_called()


# ---------------------------------------------------------------------------
# /device/<id>/commandlist/
# ---------------------------------------------------------------------------

class TestCommandList:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/0/commandlist/")
        assert resp.status_code == 200

    async def test_returns_commands(self, sanic_app, mock_controller):
        mock_controller.get_commands.return_value = MOCK_COMMANDS
        _, resp = await sanic_app.asgi_client.get("/device/0/commandlist/")
        data = resp.json
        assert "message" in data
        assert "home" in data["message"]
        assert "back" in data["message"]

    async def test_calls_get_commands_with_device_id(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/0/commandlist/")
        mock_controller.get_commands.assert_called_once_with(0)

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.get_commands.side_effect = IndexError("device not found")
        _, resp = await sanic_app.asgi_client.get("/device/99/commandlist/")
        assert resp.status_code == 400
        assert "ERROR" in resp.json


# ---------------------------------------------------------------------------
# /device/<id>/command/<command>
# ---------------------------------------------------------------------------

class TestExecCommand:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/0/command/home")
        assert resp.status_code == 200

    async def test_returns_message(self, sanic_app, mock_controller):
        mock_controller.exec_command.return_value = "home executed"
        _, resp = await sanic_app.asgi_client.get("/device/0/command/home")
        assert resp.json["message"] == "home executed"

    async def test_calls_exec_command_with_correct_args(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/0/command/back")
        mock_controller.exec_command.assert_called_once_with(0, "back")

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.exec_command.side_effect = AttributeError("bad command")
        _, resp = await sanic_app.asgi_client.get("/device/0/command/home")
        assert resp.status_code == 400
        assert "ERROR" in resp.json


# ---------------------------------------------------------------------------
# /device/<id>/apps/list/
# ---------------------------------------------------------------------------

class TestAppsList:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/list/")
        assert resp.status_code == 200

    async def test_returns_apps_dict(self, sanic_app, mock_controller):
        mock_controller.get_apps.return_value = {
            "12": {"name": "Netflix", "version": "4.1"}
        }
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/list/")
        data = resp.json
        assert "12" in data
        assert data["12"]["name"] == "Netflix"

    async def test_calls_get_apps_with_device_id(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/list/")
        mock_controller.get_apps.assert_called_once_with(0)

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.get_apps.side_effect = IndexError("no device")
        _, resp = await sanic_app.asgi_client.get("/device/99/apps/list/")
        assert resp.status_code == 400
        assert "error" in resp.json


# ---------------------------------------------------------------------------
# /device/<id>/apps/launch/<app_id>
# ---------------------------------------------------------------------------

class TestLaunchApp:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/launch/12")
        assert resp.status_code == 200

    async def test_calls_launch_app_with_correct_args(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/launch/12")
        mock_controller.launch_app.assert_called_once_with(0, 12)

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.launch_app.side_effect = IndexError("app not found")
        _, resp = await sanic_app.asgi_client.get("/device/0/apps/launch/999")
        assert resp.status_code == 400
        assert "ERROR" in resp.json


# ---------------------------------------------------------------------------
# /device/<id>/activeapp/
# ---------------------------------------------------------------------------

class TestActiveApp:
    async def test_returns_200(self, sanic_app):
        _, resp = await sanic_app.asgi_client.get("/device/0/activeapp/")
        assert resp.status_code == 200

    async def test_returns_active_app_name(self, sanic_app, mock_controller):
        mock_controller.active_app.return_value = "Netflix"
        _, resp = await sanic_app.asgi_client.get("/device/0/activeapp/")
        assert resp.json == "Netflix"

    async def test_calls_active_app_with_device_id(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.get("/device/0/activeapp/")
        mock_controller.active_app.assert_called_once_with(0)

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.active_app.side_effect = IndexError("no device")
        _, resp = await sanic_app.asgi_client.get("/device/99/activeapp/")
        assert resp.status_code == 400
        assert "ERROR" in resp.json


# ---------------------------------------------------------------------------
# /device/<id>/literal/  (POST)
# ---------------------------------------------------------------------------

class TestLiteral:
    async def test_returns_200_with_text(self, sanic_app):
        _, resp = await sanic_app.asgi_client.post(
            "/device/0/literal/", json={"text": "hello"}
        )
        assert resp.status_code == 200

    async def test_calls_literal_with_text(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.post(
            "/device/0/literal/", json={"text": "hello"}
        )
        mock_controller.literal.assert_called_once_with(device_id=0, text="hello")

    async def test_empty_text_fallback(self, sanic_app, mock_controller):
        _, resp = await sanic_app.asgi_client.post(
            "/device/0/literal/", json={}
        )
        assert resp.status_code == 200
        mock_controller.literal.assert_called_once_with(device_id=0, text="")

    async def test_returns_400_on_exception(self, sanic_app, mock_controller):
        mock_controller.literal.side_effect = IndexError("no device")
        _, resp = await sanic_app.asgi_client.post(
            "/device/99/literal/", json={"text": "hi"}
        )
        assert resp.status_code == 400
        assert "ERROR" in resp.json
