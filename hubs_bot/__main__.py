import logging

from hubs_bot.app import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hubs-bot")

logger.info("starting")

main()
