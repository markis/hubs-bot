from unittest.mock import ANY, Mock

import pytest
from openai import Completion
from praw import Reddit
from praw.models.reddit.redditor import Redditor
from praw.models.reddit.submission import SubmissionFlair
from praw.reddit import Submission, Subreddit

from hubs_bot.app import HubTimesBot, HubTimesLink
from hubs_bot.config import Config
from hubs_bot.context import Context


@pytest.fixture()
def hub_times_bot() -> HubTimesBot:
    config = Config()
    context = Context(config)
    return HubTimesBot(context, config)


@pytest.mark.integration()
@pytest.mark.vcr()
def test_bot_run(hub_times_bot: HubTimesBot) -> None:
    hub_times_bot.run()


@pytest.mark.integration()
@pytest.mark.vcr(record_mode="none")
def test_bot_with_real_duplicate_link(hub_times_bot: HubTimesBot) -> None:
    # This test will fail if the link is already submitted
    # DO NOT DELETE THE CASSETTE FOR THIS TEST
    link = hub_times_bot.get_hub_times_link()
    assert link
    submitted = hub_times_bot.submit_link(link)
    assert not submitted


def get_mock_hub_times_bot() -> tuple[HubTimesBot, Mock, Mock]:
    mock_reddit = Mock(
        spec=Reddit, subreddit=Mock(spec=Subreddit), user=Mock(me=Mock(spec=Redditor))
    )
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = []
    mock_me = mock_reddit.user.me()
    mock_me.new.return_value = []
    mock_openai_completion = Mock(
        spec=Completion, create=Mock(return_value=Mock(choices=[Mock(text="test")]))
    )
    mock_context = Mock(spec=Context, reddit=mock_reddit, openai_completion=mock_openai_completion)
    mock_config = Mock(spec=Config, base_url="http://test.com", news_tags={"LOCAL"})
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
    test_page = """
    <html>
        <a href="/test-page">
            Headline
            <div data-c-ms="LOCAL"></div>
        </a>
    </html>
    """
    mock_context.http_get.return_value = test_page

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


@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_submit_link() -> None:
    bot, _, mock_reddit = get_mock_hub_times_bot()
    mock_link = Mock(spec=HubTimesLink, headline="test", url="http://test.com")
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    bot.submit_link(mock_link)

    mock_sr.submit.assert_called_with(title="test", url="http://test.com", flair_id=ANY)


@pytest.mark.unit()
@pytest.mark.block_network()
def test_bot_submit_duplicate_link() -> None:
    bot, _, mock_reddit = get_mock_hub_times_bot()
    mock_link = Mock(
        spec=HubTimesLink,
        headline="test",
        url="http://dupetest.com",
    )
    mock_sr = mock_reddit.subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    bot.submit_link(mock_link)

    mock_sr.submit.assert_not_called()
