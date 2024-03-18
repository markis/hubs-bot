"""Summarizer module."""
import logging

from openai import OpenAI

from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)


class Summarizer:
    """Summarizes articles."""

    config: Config
    openai: OpenAI

    def __init__(self, context: Context, config: Config) -> None:
        """Initialize the summarizer."""
        self.config = config
        self.openai = context.openai

    def generate(self, article: str) -> str:
        """Generate a summary of the article."""
        prompt = (
            "Can you summarize this article? Please respond with just the summary:\n\n" + article
        )
        resp = self.openai.completions.create(
            model=self.config.openai_model,
            prompt=prompt,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        if resp and resp.choices and len(resp.choices) > 0 and (text := resp.choices[0].text):
            return text.strip()
        return ""
