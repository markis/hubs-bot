from unittest.mock import ANY, Mock

import pytest
from openai.types import Completion, CompletionChoice, CompletionUsage
from praw import Reddit
from praw.models.reddit.redditor import Redditor
from praw.models.reddit.submission import SubmissionFlair
from praw.reddit import Submission, Subreddit

from hubs_bot.app import HubTimesArticle, HubTimesBot
from hubs_bot.config import Config
from hubs_bot.context import Context


def get_mock_hub_times_bot() -> tuple[HubTimesBot, Mock, Mock]:
    mock_reddit = Mock(
        spec=Reddit, subreddit=Mock(spec=Subreddit), user=Mock(me=Mock(spec=Redditor))
    )
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = []
    mock_me = mock_reddit.user.me()
    mock_me.new.return_value = []
    mock_openai = Mock()
    mock_openai.completions.create.return_value = Completion(
        id="cmpl-123abc",
        choices=[CompletionChoice(finish_reason="stop", index=0, logprobs=None, text="Test")],
        created=123456,
        model="gpt-model",
        object="text_completion",
        system_fingerprint=None,
        usage=CompletionUsage(completion_tokens=2, prompt_tokens=73, total_tokens=75),
    )
    mock_context = Mock(spec=Context, reddit=mock_reddit, openai=mock_openai)
    mock_config = Mock(spec=Config, base_url="http://test.com", news_tags=("LOCAL",))
    mock_submission = Mock(
        spec=Submission,
        title="Test post",
        id="t3_123",
        flair=Mock(
            spec=SubmissionFlair,
            choices=Mock(return_value=[{"flair_text": "test", "flair_template_id": "1"}]),
        ),
    )
    mock_sr.submit.return_value = mock_submission

    return HubTimesBot(mock_context, mock_config), mock_context, mock_reddit


@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_with_link() -> None:
    bot, mock_context, mock_reddit = get_mock_hub_times_bot()
    test_listing_page = """
    <html>
        <a href="/test-page">
            Headline
            <div data-c-ms="LOCAL"></div>
        </a>
    </html>
    """
    test_article_page = """
    <html>
        <article>
            <h1>Headline</h1>
        </article>
    </html>
    """
    mock_context.http_get.side_effect = [test_listing_page, test_article_page]

    bot.run()

    mock_reddit.subreddit().submit.assert_called_with(
        title="Headline", url="http://test.com/test-page", flair_id=ANY
    )


@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_with_no_link() -> None:
    bot, mock_context, mock_reddit = get_mock_hub_times_bot()
    test_page = "<html></html>"
    mock_context.http_get.return_value = test_page

    bot.run()

    mock_reddit.subreddit().submit.assert_not_called()


@pytest.mark.skip(reason="TODO: update tests")
@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_submit_link() -> None:
    bot, _, mock_reddit = get_mock_hub_times_bot()
    mock_link = Mock(spec=HubTimesArticle, headline="test", url="http://test.com")
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    bot.submit_link(mock_link)

    mock_sr.submit.assert_called_with(title="test", url="http://test.com", flair_id=ANY)


@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_submit_duplicate_link() -> None:
    bot, _, mock_reddit = get_mock_hub_times_bot()
    mock_link = Mock(
        spec=HubTimesArticle,
        headline="test",
        url="http://dupetest.com",
    )
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    bot.submit_link(mock_link)

    mock_sr.submit.assert_not_called()
