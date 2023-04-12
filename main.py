#!/usr/bin/python3

import logging
from dotenv import load_dotenv
from os import getenv

from telegram import Update
from telegram.ext import (
        ApplicationBuilder,
        ContextTypes,
        CommandHandler
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

    application.run_polling()

if __name__ == '__main__':
    main()
