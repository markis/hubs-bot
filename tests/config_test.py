import os
from typing import Any, Final
from unittest import mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hubs_bot.config import Config, create_set_factory


@pytest.mark.unit()
def test_config_with_mock_env() -> None:
    mock_environ = {
        "CLIENT_ID": "test",
        "CLIENT_SECRET": "test",
        "USERNAME": "test",
        "PASSWORD": "test",
    }
    with mock.patch.dict(os.environ, mock_environ):
        config = Config()

    assert config.client_secret != ""
    assert config.client_id != ""
    assert config.password != ""
    assert config.username != ""


@pytest.mark.unit()
def test_set_factory_str_success() -> None:
    result = create_set_factory("foo", set(), {"foo": "bar"})()
    assert result == {"bar"}


@pytest.mark.unit()
def test_set_factory_set_success() -> None:
    result = create_set_factory("foo", set(), {"foo": {"bar"}})()
    assert result == {"bar"}


@pytest.mark.unit()
def test_set_factory_failure() -> None:
    test_env: Any = {"foo": 1}
    with pytest.raises(ValueError, match=r"\$foo is not set correctly"):
        create_set_factory("foo", set(), test_env)()


def build_url_strategy() -> st.SearchStrategy[str]:
    def _create_url(
        scheme: str, domain: str, path: str, query: dict[str, str], fragment: str
    ) -> str:
        from urllib.parse import urlparse, urlunparse

        querystring = "&".join([f"{k}={v}" for k, v in query.items()])
        return urlunparse(urlparse(f"{scheme}://{domain}/{path}?{querystring}#{fragment}"))

    scheme_strategy = st.sampled_from(["http", "https"])
    url_text_strategy = st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd"),
            whitelist_characters=("-",),
            min_codepoint=97,
            max_codepoint=122,
        ),
        min_size=1,
    )
    fragment_strategy = st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd"),
            whitelist_characters=("-",),
            min_codepoint=97,
            max_codepoint=122,
        ),
        min_size=0,
    )
    single_domain_name_strategy = st.lists(url_text_strategy, min_size=1, max_size=5)
    domain_name_strategy = single_domain_name_strategy.map(".".join)
    query_strategy = st.dictionaries(keys=url_text_strategy, values=url_text_strategy)
    return st.builds(
        _create_url,
        scheme=scheme_strategy,
        domain=domain_name_strategy,
        path=url_text_strategy,
        query=query_strategy,
        fragment=fragment_strategy,
    )


STRING_STRATEGY: Final = st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126))
URL_STRATEGY: Final = build_url_strategy()
TAGS_STRATEGY: Final = st.sets(STRING_STRATEGY, min_size=1)


@given(
    base_url=URL_STRATEGY,
    hubtimes_url=URL_STRATEGY,
    subreddit=STRING_STRATEGY,
    subreddit_flair=STRING_STRATEGY,
    news_tags=TAGS_STRATEGY,
    username=STRING_STRATEGY,
    password=STRING_STRATEGY,
    client_id=STRING_STRATEGY,
    client_secret=STRING_STRATEGY,
    openai_key=STRING_STRATEGY,
)
@settings(max_examples=10)
def test_config_instantiation(
    base_url: str,
    hubtimes_url: str,
    subreddit: str,
    subreddit_flair: str,
    news_tags: set[str],
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
    openai_key: str,
) -> None:
    config = Config(
        base_url=base_url,
        hubtimes_url=hubtimes_url,
        subreddit=subreddit,
        subreddit_flair=subreddit_flair,
        news_tags=news_tags,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        openai_key=openai_key,
    )
    assert isinstance(config, Config)
    assert isinstance(config.base_url, str)
    assert isinstance(config.hubtimes_url, str)
    assert isinstance(config.subreddit, str)
    assert isinstance(config.subreddit_flair, str)
    assert isinstance(config.news_tags, set)
    assert isinstance(config.username, str)
    assert isinstance(config.password, str)
    assert isinstance(config.client_id, str)
    assert isinstance(config.client_secret, str)
    assert isinstance(config.openai_key, str)
