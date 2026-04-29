import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MOCK_COMMANDS = [
    "back", "backspace", "channel_down", "channel_up", "down", "enter",
    "find_remote", "forward", "home", "info", "input_av1", "input_hdmi1",
    "input_hdmi2", "input_hdmi3", "input_hdmi4", "input_tuner", "left",
    "literal", "play", "power", "poweroff", "poweron", "replay", "reverse",
    "right", "search", "select", "up", "volume_down", "volume_mute",
    "volume_up",
]


def make_mock_device(host="192.168.1.100", port=8060):
    device = MagicMock()
    device.host = host
    device.port = port
    device.commands = MOCK_COMMANDS

    app1 = MagicMock()
    app1.id = "12"
    app1.name = "Netflix"
    app1.version = "4.1.218"

    app2 = MagicMock()
    app2.id = "13"
    app2.name = "Amazon Video"
    app2.version = "3.0.1"

    device.apps = [app1, app2]

    active = MagicMock()
    active.name = "Netflix"
    device.active_app = active

    return device


@pytest.fixture
def mock_device():
    return make_mock_device()


@pytest.fixture
def mock_controller():
    ctrl = MagicMock()
    ctrl.get_devices.return_value = [
        {"id": 0, "host": "192.168.1.100", "port": 8060}
    ]
    ctrl.get_commands.return_value = MOCK_COMMANDS
    ctrl.exec_command.return_value = "home executed"
    ctrl.get_apps.return_value = {
        "12": {"name": "Netflix", "version": "4.1.218"},
        "13": {"name": "Amazon Video", "version": "3.0.1"},
    }
    ctrl.launch_app.return_value = None
    ctrl.active_app.return_value = "Netflix"
    ctrl.literal.return_value = None
    return ctrl


@pytest.fixture
def sanic_app(mock_controller):
    """Return Sanic app with RokuController fully mocked out."""
    with patch("rokucontroller.rokucontroller.Roku.discover", return_value=[make_mock_device()]):
        import importlib
        import pyrokuserve as prs
        # Swap the module-level controller for our mock
        prs.rokuc = mock_controller
        yield prs.app
