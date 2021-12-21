from unittest.mock import ANY
from unittest.mock import Mock
from unittest.mock import patch

from hubs_bot.app import get_hub_times_link
from hubs_bot.app import HubTimesLink
from hubs_bot.app import submit_link


def test_get_hub_times_link() -> None:
    link = get_hub_times_link()
    assert link


@patch("hubs_bot.app.Reddit")
def test_submit_link(mock_reddit: Mock) -> None:
    mock_link = Mock(spec=HubTimesLink, headline="test", url="http://test.com")
    mock_sr = mock_reddit().subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    submit_link(mock_link)

    mock_sr.submit.assert_called_with(title="test", url="http://test.com", flair_id=ANY)


@patch("hubs_bot.app.Reddit")
def test_submit_duplicate_link(mock_reddit: Mock) -> None:
    mock_link = Mock(spec=HubTimesLink, headline="test", url="http://dupetest.com")
    mock_sr = mock_reddit().subreddit()
    mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

    submit_link(mock_link)

    mock_sr.submit.assert_not_called()
