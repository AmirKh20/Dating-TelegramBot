#!/usr/bin/python3

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', handlers.StartHandler))
    application.add_handler(CommandHandler('help', handlers.HelpHandler))
    application.add_handler(MessageHandler(filters.Regex('^مشاوره$'), handlers.ConsultationHandler))
    application.add_handler(MessageHandler(filters.Regex('^بازگشت به منوی اصلی$'), handlers.MainMenuHandler))

    application.run_polling()


if __name__ == '__main__':
    main()
