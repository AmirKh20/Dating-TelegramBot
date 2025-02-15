#!/bin/env python

"""
The Environment variables that need to be set in .env file:
BOT_TOKEN: The bot token
CHANNEL_USERNAME: username of the channel which users should be subscribed into in the format of '@username'
LOG_FILENAME: DEFAULT: bot.log. The filename of the log file which the logs are written into
WEBSITE_URL: the url of the website when clicking on profile edit
FINANCIAL_CHARGE_URL: the url for financial charge button
QA_GROUP_ID: chat_id for the QA group.
QA_CHANNEL: username of the channel which questions are posted.
SUPPORT_GROUP_ID: chat_id for the support group.
BOT_USERNAME: the bot username with @ before it: @botusername
COINS_PRICE: the price of the coins.
FINANCIAL_RECEIVE_MONEY_URL: the url for financial receive button
CHATBOT_URL: the url for Chatbot button
THERAPISTS_URL: the url for Therapist button
BALANCE_URL: the url for balance button
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
    application = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .persistence(persistence) \
        .read_timeout(20.0) \
        .write_timeout(20.0) \
        .build()

    # Conversation handler for chatting between users
    application.add_handler(handlers.conversations['Chatting'])

    # Parent conversation handler for every button
    application.add_handler(handlers.conversations['Starting'])

    application.add_handler(handlers.commands['Help'])
    application.add_handler(handlers.messages['Main-Menu'])

    # Handlers for accepting/rejecting the user's question in the QA Group
    application.add_handler(handlers.accept_question_query_handler)
    application.add_handler(handlers.reject_question_query_handler)

    # Handler for answering the tickets in the Support Group
    application.add_handler(handlers.messages['Support']['Answer-Ticket'])

    # Handlers for showing the users' given/gotten chat requests list
    application.add_handler(handlers.given_list_inline_query_handler)
    application.add_handler(handlers.gotten_list_inline_query_handler)

    # Conversation handlers which show other users' options when clicking on a user in the given/gotten list
    application.add_handlers([handlers.conversations['Chat-Requests']['Given'],
                              handlers.conversations['Chat-Requests']['Gotten']])

    application.add_error_handler(handlers.ErrorHandler)

    application.run_polling()


if __name__ == '__main__':
    main()
