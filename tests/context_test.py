from unittest.mock import Mock, patch

from praw import Reddit

from hubs_bot.config import Config
from hubs_bot.context import Context


def test_context_init() -> None:
    context = Context(Mock(spec=Config))

    assert context
    assert isinstance(context.reddit, Reddit)
    assert isinstance(context.openai_completion, type)


def test_context_http_get() -> None:
    with patch("hubs_bot.context.requests") as mock_requests:
        mock_requests.get().text = "html"

        context = Context(Mock(spec=Config))

        assert context.http_get("url") == "html"
