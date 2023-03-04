from unittest import TestCase
from unittest.mock import ANY, Mock

from praw import Reddit
from praw.reddit import Subreddit

from hubs_bot.app import HubTimesBot, HubTimesLink
from hubs_bot.config import Config
from hubs_bot.context import Context


class TestHubTimesBot(TestCase):
    def setUp(self) -> None:
        self.mock_reddit = Mock(spec=Reddit, subreddit=Mock(spec=Subreddit))
        self.mock_reddit.subreddit().new.return_value = []
        self.mock_context = Mock(spec=Context, reddit=self.mock_reddit)
        self.mock_config = Mock(spec=Config, base_url="http://test.com", news_tags={"LOCAL"})

        self.bot = HubTimesBot(self.mock_context, self.mock_config)

    def test_bot_with_link(self) -> None:
        test_page = """
        <html>
            <a href="/test-page">
                Headline
                <div data-c-ms="LOCAL"></div>
            </a>
        </html>
        """
        self.mock_context.http_get.return_value = test_page

        self.bot.run()

        self.mock_reddit.subreddit().submit.assert_called_with(
            title="Headline", url="http://test.com/test-page", flair_id=ANY
        )

    def test_bot_with_no_link(self) -> None:
        test_page = "<html></html>"
        self.mock_context.http_get.return_value = test_page

        self.bot.run()

        self.mock_reddit.subreddit().submit.assert_not_called()

    def test_bot_submit_link(self) -> None:
        mock_link = Mock(spec=HubTimesLink, headline="test", url="http://test.com")
        mock_sr = self.mock_reddit.subreddit()
        mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

        self.bot.submit_link(mock_link)

        mock_sr.submit.assert_called_with(title="test", url="http://test.com", flair_id=ANY)

    def test_bot_submit_duplicate_link(self) -> None:
        mock_link = Mock(spec=HubTimesLink, headline="test", url="http://dupetest.com")
        mock_sr = self.mock_reddit.subreddit()
        mock_sr.new.return_value = [Mock(url="http://dupetest.com")]

        self.bot.submit_link(mock_link)

        mock_sr.submit.assert_not_called()
