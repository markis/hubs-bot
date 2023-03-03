from unittest import TestCase
from unittest.mock import ANY, Mock, patch

from hubs_bot.app import HubTimesLink, main, submit_link


@patch("hubs_bot.app.requests")
@patch("hubs_bot.app.Reddit")
class TestApp(TestCase):
    def test_main(self, mock_reddit: Mock, mock_requests: Mock) -> None:
        test_page = """
        <html>
            <a href="/test-page">
                Headline
                <div data-c-ms="LOCAL"></div>
            </a>
        </html>
        """
        mock_sr = mock_reddit().subreddit()
        mock_requests.get.return_value = Mock(text=test_page)

        main()

        mock_sr.submit.assert_called_with(
            title="Headline", url="https://www.beaconjournal.com/test-page", flair_id=ANY
        )

    def test_main_no_link(self, mock_reddit: Mock, mock_requests: Mock) -> None:
        test_page = "<html></html>"
        mock_sr = mock_reddit().subreddit()
        mock_requests.get.return_value = Mock(text=test_page)

        main()

        mock_sr.submit.assert_not_called()

    def test_submit_link(self, mock_reddit: Mock, *_: list[Mock]) -> None:
        mock_link = Mock(spec=HubTimesLink, headline="test", url="http://test.com")
        mock_sr = mock_reddit().subreddit()
        mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

        submit_link(mock_link)

        mock_sr.submit.assert_called_with(title="test", url="http://test.com", flair_id=ANY)

    def test_submit_duplicate_link(self, mock_reddit: Mock, *_: list[Mock]) -> None:
        mock_link = Mock(spec=HubTimesLink, headline="test", url="http://dupetest.com")
        mock_sr = mock_reddit().subreddit()
        mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

        submit_link(mock_link)

        mock_sr.submit.assert_not_called()
