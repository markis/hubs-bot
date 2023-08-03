import logging
from textwrap import dedent
from typing import TYPE_CHECKING, Any, TypeGuard

import openai
from praw.reddit import Submission
from typing_extensions import NotRequired, TypedDict

from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from praw.models.reddit.submission import SubmissionFlair


class Flair(TypedDict):
    flair_template_id: str
    flair_text: str
    flair_css_class: NotRequired[str]
    flair_text_editable: NotRequired[bool]
    flair_position: NotRequired[str]


def is_flair(value: Any) -> TypeGuard[Flair]:
    return isinstance(value, dict) and all(key in value for key in Flair.__required_keys__)


class Categorizer:
    config: Config
    openai_completion: openai.Completion

    def __init__(self, context: Context, config: Config) -> None:
        self.config = config
        self.openai_completion = context.openai_completion

    def flair_submission(self, submission: Submission) -> None:
        """
        Flair the submission using only the flair available on the subreddit
        """
        flair: SubmissionFlair = submission.flair
        choices = {
            choice["flair_text"]: choice["flair_template_id"]
            for choice in flair.choices()
            if is_flair(choice)
        }

        flair_id = self._ask_openai(submission.title, choices)
        submission.flair.select(flair_id)

    def _ask_openai(self, content_text: str, choices: dict[str, str]) -> str:
        result = self.config.subreddit_flair
        prompt = dedent(
            f"""
            Using only one of the following categories:
            {", ".join(choices.keys())}

            How would you categorize the following news article:

            {content_text}
            """
        )

        resp: Any = self.openai_completion.create(  # type: ignore[no-untyped-call]
            model="text-davinci-003",
            prompt=prompt,
        )

        if resp and len(resp.choices) > 0:
            text: str = resp.choices[0].text
            result = choices.get(text.strip(), result)

        return result
