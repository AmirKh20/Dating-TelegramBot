#!/bin/python3

"""
The Environment variables that need to be set in .env file:
BOT_TOKEN: The bot token
CHANNEL_USERNAME: username of the channel which users should be subscribed into in the format of '@username'
LOG_FILENAME: DEFAULT: bot.log. The filename of the log file which the logs are written into
PROVINCES_FILE: DEFAULT: provinces_cities.json. Json file containing provinces
WEBSITE_URL: the url of the website when clicking on profile edit
FINANCIAL_CHARGE_URL: the url for financial charge button
QA_GROUP_ID: chat_id for the QA group.
QA_CHANNEL: username of the channel which questions are posted.
SUPPORT_GROUP_ID: chat_id for the support group.
BOT_USERNAME: the bot username with @ before it: @botusername
"""

import logging
from os import getenv

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, PicklePersistence

import handlers

load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')
LOG_FILENAME = getenv('LOG_FILENAME', 'bot.log')

logging.basicConfig(
    filename=LOG_FILENAME,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def main():
    persistence = PicklePersistence(filepath='bot_persistence')
    application = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

    application.add_handler(handlers.conversations['Starting'])
    application.add_handler(handlers.commands['Help'])
    application.add_handler(handlers.messages['Main-Menu'])

    # Handlers for accepting/rejecting the user's question in the QA Group
    application.add_handler(handlers.accept_question_query_handler)
    application.add_handler(handlers.reject_question_query_handler)

    # Handler for answering the tickets in the Support Group
    application.add_handler(handlers.messages['Support']['Answer-Ticket'])

    application.add_handler(handlers.given_list_inline_query_handler)
    application.add_handler(handlers.gotten_list_inline_query_handler)

    application.add_handler(handlers.conversations['Chat-Requests'])

    application.run_polling()


if __name__ == '__main__':
    main()
