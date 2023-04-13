from os import getenv

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

load_dotenv()
CHANNEL_USERNAME = getenv('CHANNEL_USERNAME')


async def SendMessage(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    This function sends a message in the current chat with the given text.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def ReplyMessage(update: Update, text: str, reply_keyboard_markup: ReplyKeyboardMarkup = None) -> None:
    """
    This function replies to the last message the user sent with the given text
    It also replies the text with the given keyboard buttons if it was specified.
    reply_keyboard_markup: The keyboard buttons
    """
    await update.message.reply_text(text=text,
                                    reply_to_message_id=update.message.message_id,
                                    reply_markup=reply_keyboard_markup)


async def CheckSubs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Checks if the users is subscribed to 'CHANNEL_USERNAME'. CHANNEL_USERNAME should be set in the .env file.
    It also replies that the user should join CHANNEL_USERNAME.
    return True if the user is subscribed. False otherwise
    This function is used in every handler.
    """
    chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=update.effective_user.id)
    if chat_member['status'] in ['left', 'kicked']:
        await ReplyMessage(update, f'لطفا در کانال {CHANNEL_USERNAME} عضو شوید!')
        return False
    return True
