from hubs_bot.app import HubTimesBot
from hubs_bot.config import Config
from hubs_bot.context import Context

config = Config()
context = Context(config)
bot = HubTimesBot(context, config)
bot.run()
