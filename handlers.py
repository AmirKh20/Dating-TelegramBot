#!/usr/bin/python3

from keyboard_buttons import keyboards
from utils import *


async def StartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs when /start command is sent. The default home keyboards are shown.
    """
    await ReplyMessage(update, 'سلام و خوش آمدید به ربات سوشیانت!', keyboards['default_keyboard'])
    await SendMessage(update, context, 'اطلاعاتی درمورد ربات')
    await SendMessage(update, context, 'با دستور /help کمک بگیرید')
    await CheckSubs(update, context)


async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs when /help command is sent.
    Doesn't show anything if the users is not subscribed.
    """
    if not await CheckSubs(update, context):
        return

    await SendMessage(update, context, 'این خروجی هلپ است')


async def ConsultationHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs when مشاوره is sent. The consultation keyboard is shown.
    """
    await ReplyMessage(update, 'چه نوع مشاوره می خواهید؟', keyboards['consultation_keyboard'])
    await CheckSubs(update, context)


async def MainMenuHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs when we want to get back to the default keyboard buttons.
    """
    await ReplyMessage(update, 'منوی اصلی:', keyboards['default_keyboard'])
    await CheckSubs(update, context)
