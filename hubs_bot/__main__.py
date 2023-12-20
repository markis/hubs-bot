from hubs_bot.app import HubTimesBot
from hubs_bot.config import Config
from hubs_bot.context import Context


def run() -> None:
    config = Config()
    context = Context(config)
    bot = HubTimesBot(context, config)
    bot.run()


if __name__ in ("__main__", "hubs_bot"):
    run()
