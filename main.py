#!/bin/python3

"""
The Environment variables that need to be set in .env file:
BOT_TOKEN: The bot token
CHANNEL_USERNAME: username of the channel which users should be subscribed into in the format of '@username'
LOG_FILENAME: The filename of the log file which the logs are written into
"""

import logging
from os import getenv

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

import handlers

load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')
LOG_FILENAME = getenv('LOG_FILENAME')

logging.basicConfig(
    filename=LOG_FILENAME,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', handlers.StartHandler))
    application.add_handler(CommandHandler('help', handlers.HelpHandler))
    application.add_handler(MessageHandler(filters.Regex('^مشاوره$'), handlers.ConsultationHandler))
    application.add_handler(MessageHandler(filters.Regex('^بازگشت به منوی اصلی$'), handlers.MainMenuHandler))

    application.run_polling()


if __name__ == '__main__':
    main()
