import os
from collections.abc import Iterable
from typing import Any
from unittest import mock

import pytest

from hubs_bot.config import Config, create_set_factory


@pytest.fixture(autouse=True)
def mock_settings_env_vars() -> Iterable[None]:
    mock_environ = dict(
        CLIENT_ID="test",
        CLIENT_SECRET="test",
        USERNAME="test",
        PASSWORD="test",
    )
    with mock.patch.dict(os.environ, mock_environ):
        yield


def test_config_with_mock_env() -> None:
    config = Config()

    assert config.client_secret != ""
    assert config.client_id != ""
    assert config.password != ""
    assert config.username != ""


def test_set_factory_str_success() -> None:
    result = create_set_factory("foo", set(), {"foo": "bar"})()
    assert result == {"bar"}


def test_set_factory_set_success() -> None:
    result = create_set_factory("foo", set(), {"foo": {"bar"}})()
    assert result == {"bar"}


def test_set_factory_failure() -> None:
    with pytest.raises(ValueError):
        test_env: Any = {"foo": 1}
        create_set_factory("foo", set(), test_env)()
