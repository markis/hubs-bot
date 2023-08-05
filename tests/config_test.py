import os
from typing import Any
from unittest import mock

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from hubs_bot.config import Config, create_tuple_factory


@given(st.text(), st.tuples(st.text()))
@settings(max_examples=10)
def test_returned_function_returns_tuple(env_name: str, default: tuple[str, ...]) -> None:
    env: dict[str, tuple[str, ...]] = {}
    factory = create_tuple_factory(env_name, default, env)
    assert isinstance(factory(), tuple)


@given(st.text(), st.tuples(st.text()))
@settings(max_examples=10)
def test_default_value(env_name: str, default: tuple[str, ...]) -> None:
    env: dict[str, tuple[str, ...]] = {}
    factory = create_tuple_factory(env_name, default, env)
    assert factory() == default


@given(st.text(), st.tuples(st.text()), st.text("ab,"))
def test_string_env_value(env_name: str, default: tuple[str, ...], value: str) -> None:
    assume("," in value)
    env = {env_name: value}
    factory = create_tuple_factory(env_name, default, env)
    assert factory() == tuple(value.split(","))


@given(st.text(), st.tuples(st.text()), st.tuples(st.text()))
@settings(max_examples=10)
def test_tuple_env_value(env_name: str, default: tuple[str, ...], value: tuple[str, ...]) -> None:
    env = {env_name: value}
    factory = create_tuple_factory(env_name, default, env)
    assert factory() == value


@given(st.text(), st.tuples(st.text()), st.one_of(st.integers(), st.floats(), st.booleans()))
def test_invalid_env_value(env_name: str, default: tuple[str, ...], value: str) -> None:
    assume(not isinstance(value, str | tuple))
    env = {env_name: value}
    factory = create_tuple_factory(env_name, default, env)
    with pytest.raises(ValueError, match="is not set correctly"):
        factory()


@given(
    environ=st.fixed_dictionaries(
        {
            "BASE_URL": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "HUBTIMES_URL": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "SUBREDDIT": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "SUBREDDIT_FLAIR": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "NEWS_TAGS": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "USERNAME": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "PASSWORD": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "CLIENT_ID": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "CLIENT_SECRET": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
            "OPEN_AI_KEY": st.text(st.characters(min_codepoint=32, max_codepoint=126)),
        }
    )
)
@settings(max_examples=10)
def test_config_instantiation(
    environ: dict[str, Any],
) -> None:
    with mock.patch.dict(os.environ, environ):
        config = Config()
    assert isinstance(config, Config)
    assert isinstance(config.base_url, str)
    assert isinstance(config.hubtimes_url, str)
    assert isinstance(config.subreddit, str)
    assert isinstance(config.subreddit_flair, str)
    assert isinstance(config.news_tags, tuple)
    assert isinstance(config.username, str)
    assert isinstance(config.password, str)
    assert isinstance(config.client_id, str)
    assert isinstance(config.client_secret, str)
    assert isinstance(config.openai_key, str)
