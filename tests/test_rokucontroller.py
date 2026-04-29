import sys
import pytest
from unittest.mock import MagicMock, patch, call

from tests.conftest import make_mock_device, MOCK_COMMANDS


@pytest.fixture
def controller_and_device():
    """Fixture providing a RokuController with one mocked device."""
    device = make_mock_device()
    with patch("roku.Roku.discover", return_value=[device]):
        from rokucontroller.rokucontroller import RokuController
        ctrl = RokuController(timeout=1)
    return ctrl, device


@pytest.fixture
def two_device_controller():
    """Fixture with two mocked devices."""
    dev0 = make_mock_device(host="192.168.1.100", port=8060)
    dev1 = make_mock_device(host="192.168.1.101", port=8060)
    with patch("roku.Roku.discover", return_value=[dev0, dev1]):
        from rokucontroller.rokucontroller import RokuController
        ctrl = RokuController(timeout=1)
    return ctrl, dev0, dev1


class TestRokuControllerInit:
    def test_exits_when_no_devices_found(self):
        with patch("roku.Roku.discover", return_value=[]):
            from rokucontroller.rokucontroller import RokuController
            with pytest.raises(SystemExit):
                RokuController(timeout=1)

    def test_exits_when_discover_returns_none(self):
        with patch("roku.Roku.discover", return_value=None):
            from rokucontroller.rokucontroller import RokuController
            with pytest.raises(SystemExit):
                RokuController(timeout=1)

    def test_stores_discovered_devices(self, controller_and_device):
        ctrl, device = controller_and_device
        assert len(ctrl.devices) == 1
        assert ctrl.devices[0] is device

    def test_stores_multiple_devices(self, two_device_controller):
        ctrl, dev0, dev1 = two_device_controller
        assert len(ctrl.devices) == 2


class TestGetDevices:
    def test_returns_list_with_id_host_port(self, controller_and_device):
        ctrl, device = controller_and_device
        result = ctrl.get_devices()
        assert len(result) == 1
        assert result[0] == {"id": 0, "host": "192.168.1.100", "port": 8060}

    def test_returns_correct_device_count(self, two_device_controller):
        ctrl, dev0, dev1 = two_device_controller
        result = ctrl.get_devices()
        assert len(result) == 2

    def test_ids_are_sequential(self, two_device_controller):
        ctrl, dev0, dev1 = two_device_controller
        result = ctrl.get_devices()
        assert result[0]["id"] == 0
        assert result[1]["id"] == 1

    def test_second_device_host(self, two_device_controller):
        ctrl, dev0, dev1 = two_device_controller
        result = ctrl.get_devices()
        assert result[1]["host"] == "192.168.1.101"


class TestGetCommands:
    def test_returns_commands_list(self, controller_and_device):
        ctrl, device = controller_and_device
        commands = ctrl.get_commands(0)
        assert commands == MOCK_COMMANDS

    def test_commands_contain_expected_keys(self, controller_and_device):
        ctrl, device = controller_and_device
        commands = ctrl.get_commands(0)
        for expected in ["home", "back", "play", "up", "down", "left", "right"]:
            assert expected in commands


class TestExecCommand:
    def test_calls_command_method_on_device(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.exec_command(0, "home")
        device.home.assert_called_once()

    def test_returns_executed_message(self, controller_and_device):
        ctrl, device = controller_and_device
        result = ctrl.exec_command(0, "home")
        assert result == "home executed"

    def test_back_command(self, controller_and_device):
        ctrl, device = controller_and_device
        result = ctrl.exec_command(0, "back")
        assert result == "back executed"
        device.back.assert_called_once()

    def test_invalid_command_raises(self, controller_and_device):
        ctrl, device = controller_and_device
        device.nonexistent.side_effect = AttributeError("not a valid method")
        with pytest.raises(AttributeError):
            ctrl.exec_command(0, "nonexistent")


class TestGetApps:
    def test_returns_apps_dict(self, controller_and_device):
        ctrl, device = controller_and_device
        apps = ctrl.get_apps(0)
        assert "12" in apps
        assert apps["12"]["name"] == "Netflix"
        assert apps["12"]["version"] == "4.1.218"

    def test_returns_all_apps(self, controller_and_device):
        ctrl, device = controller_and_device
        apps = ctrl.get_apps(0)
        assert len(apps) == 2
        assert "13" in apps

    def test_app_structure(self, controller_and_device):
        ctrl, device = controller_and_device
        apps = ctrl.get_apps(0)
        for app_id, app_data in apps.items():
            assert "name" in app_data
            assert "version" in app_data


class TestLaunchApp:
    def test_calls_launch_on_correct_app(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.launch_app(0, 0)
        device.apps[0].launch.assert_called_once()

    def test_launch_second_app(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.launch_app(0, 1)
        device.apps[1].launch.assert_called_once()


class TestStoreApp:
    def test_calls_store_on_correct_app(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.store_app(0, 0)
        device.apps[0].store.assert_called_once()


class TestActiveApp:
    def test_returns_active_app_name(self, controller_and_device):
        ctrl, device = controller_and_device
        result = ctrl.active_app(0)
        assert result == "Netflix"

    def test_uses_active_app_property(self, controller_and_device):
        ctrl, device = controller_and_device
        device.active_app.name = "Hulu"
        result = ctrl.active_app(0)
        assert result == "Hulu"


class TestLiteral:
    def test_passes_text_to_device(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.literal(0, "hello")
        device.literal.assert_called_once_with("hello")

    def test_returns_device_result(self, controller_and_device):
        ctrl, device = controller_and_device
        device.literal.return_value = "ok"
        result = ctrl.literal(0, "test")
        assert result == "ok"

    def test_passes_empty_string(self, controller_and_device):
        ctrl, device = controller_and_device
        ctrl.literal(0, "")
        device.literal.assert_called_once_with("")
