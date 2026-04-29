import os
import json
import logging
import pytest
from unittest.mock import patch, mock_open

import log


class TestAddSuffix:
    def test_replaces_key_at_top_level(self):
        d = {"filename": "$HOME/logs/test.log"}
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d["filename"] == "/home/user/logs/test.log"

    def test_replaces_key_in_nested_dict(self):
        d = {"handlers": {"file": {"filename": "$HOME/logs/test.log"}}}
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d["handlers"]["file"]["filename"] == "/home/user/logs/test.log"

    def test_no_match_leaves_dict_unchanged(self):
        d = {"key": "value", "other": "data"}
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d == {"key": "value", "other": "data"}

    def test_non_matching_value_not_replaced(self):
        d = {"filename": "/already/absolute/path.log"}
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d["filename"] == "/already/absolute/path.log"

    def test_deeply_nested_replacement(self):
        d = {"a": {"b": {"c": {"filename": "$HOME/deep.log"}}}}
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d["a"]["b"]["c"]["filename"] == "/home/user/deep.log"

    def test_multiple_keys_replaced(self):
        d = {
            "handler1": {"filename": "$HOME/info.log"},
            "handler2": {"filename": "$HOME/error.log"},
        }
        log.add_suffix(d, "filename", "/home/user", "$HOME")
        assert d["handler1"]["filename"] == "/home/user/info.log"
        assert d["handler2"]["filename"] == "/home/user/error.log"


class TestSetupLogging:
    def test_uses_basic_config_when_file_missing(self):
        with patch("os.path.exists", return_value=False):
            with patch("logging.basicConfig") as mock_basic:
                log.setup_logging(default_path="nonexistent.json")
                mock_basic.assert_called_once_with(level=logging.INFO)

    def test_uses_default_level_from_arg(self):
        with patch("os.path.exists", return_value=False):
            with patch("logging.basicConfig") as mock_basic:
                log.setup_logging(default_path="nonexistent.json", default_level=logging.DEBUG)
                mock_basic.assert_called_once_with(level=logging.DEBUG)

    def test_env_key_overrides_path(self):
        with patch.dict(os.environ, {"LOG_CFG": "/custom/logging.json"}):
            with patch("os.path.exists", return_value=False) as mock_exists:
                with patch("logging.basicConfig"):
                    log.setup_logging()
                    mock_exists.assert_called_with("/custom/logging.json")

    def test_loads_json_config_when_file_exists(self):
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {},
            "root": {"level": "INFO", "handlers": []},
        }
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(config))):
                with patch("logging.config.dictConfig") as mock_dict:
                    with patch.dict(os.environ, {"HOME": "/home/user"}):
                        log.setup_logging()
                        mock_dict.assert_called_once_with(config)

    def test_home_substitution_in_config(self):
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "$HOME/logs/test.log",
                }
            },
            "root": {"level": "INFO", "handlers": ["file"]},
        }
        captured = {}
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(config))):
                with patch("logging.config.dictConfig") as mock_dict:
                    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
                        log.setup_logging()
                        called_config = mock_dict.call_args[0][0]
                        assert called_config["handlers"]["file"]["filename"] == "/home/testuser/logs/test.log"

    def test_default_path_is_logging_json(self):
        with patch("os.path.exists", return_value=False) as mock_exists:
            with patch("logging.basicConfig"):
                log.setup_logging()
                mock_exists.assert_called_with("logging.json")
