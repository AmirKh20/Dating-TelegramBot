#!/usr/bin/python3

from telegram import Update
from telegram.ext import ContextTypes

from utils import *
from keyboard_buttons import keyboards

async def StartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ReplyMessageKeyboardButton(update, keyboards['default_keyboard'], 'Hello and welcome to our bot!')
    await SendMessage(update, context, 'Info about the bot')
    await SendMessage(update, context, 'get help using /help')
    await CheckSubs(update, context)

async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await CheckSubs(update, context):
        return

    await SendMessage(update, context, 'This is help!')
