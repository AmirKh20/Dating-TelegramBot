#!/usr/bin/python3

from telegram import Update
from telegram.ext import ContextTypes

from utils import *
from keyboard_buttons import keyboards

async def StartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ReplyMessageKeyboardButton(update, keyboards['default_keyboard'],
                                     'سلام و خوش آمدید به ربات سوشیانت!')
    await SendMessage(update, context, 'اطلاعاتی درمورد ربات')
    await SendMessage(update, context, 'با دستور /help کمک بگیرید')
    await CheckSubs(update, context)

async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await CheckSubs(update, context):
        return

    await SendMessage(update, context, 'این خروجی هلپ است')

async def ConsultationHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ReplyMessageKeyboardButton(update, keyboards['consultation_keyboard'],
                                     'چه نوع مشاوره می خواهید؟')
    await CheckSubs(update, context)

async def MainMenuHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ReplyMessageKeyboardButton(update, keyboards['default_keyboard'],
                                                       'منوی اصلی')
    await CheckSubs(update, context)
