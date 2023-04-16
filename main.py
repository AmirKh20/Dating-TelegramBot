#!/bin/python3

"""
The Environment variables that need to be set in .env file:
BOT_TOKEN: The bot token
CHANNEL_USERNAME: username of the channel which users should be subscribed into in the format of '@username'
LOG_FILENAME: DEFAULT: bot.log. The filename of the log file which the logs are written into
PROVINCES_FILE: DEFAULT: provinces_cities.json. Json file containing provinces
"""

import logging
from os import getenv

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

import handlers

load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')
LOG_FILENAME = getenv('LOG_FILENAME', 'bot.log')

logging.basicConfig(
    filename=LOG_FILENAME,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(handlers.conversations['Starting'])
    application.add_handler(handlers.commands['Help'])
    application.add_handler(handlers.messages['Main-Menu'])

    application.run_polling()


if __name__ == '__main__':
    main()
