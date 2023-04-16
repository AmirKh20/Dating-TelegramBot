from os import getenv
from dotenv import load_dotenv
import json

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

load_dotenv()
CHANNEL_USERNAME = getenv('CHANNEL_USERNAME')
PROVINCES_FILE = getenv('PROVINCES_FILE', 'provinces_cities.json')


async def SendMessage(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None) -> None:
    """
    This function sends a message in the current chat with the given text.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text,
                                   reply_markup=reply_markup)


async def ReplyMessage(update: Update, text: str, reply_keyboard_markup=None) -> None:
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
    Return True if the user is subscribed. False otherwise
    This function is used in every handler.
    """
    chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=update.effective_user.id)
    if chat_member['status'] in ['left', 'kicked']:
        await ReplyMessage(update, f'لطفا در کانال {CHANNEL_USERNAME} عضو شوید!')
        return False
    return True


def GetProvinceNames() -> list[str]:
    with open(PROVINCES_FILE, 'r') as json_file:
        data = json.load(json_file)
    names = [province['name'] for province in data]
    return names


def GetProvinceNamesInlineSequence():
    names = GetProvinceNames()
    number_of_provinces = len(names)
    number_of_3_rows_elements = number_of_provinces - number_of_provinces % 3

    l = []
    for i in range(0, number_of_3_rows_elements, 3):
        l.append([
            InlineKeyboardButton(names[i], callback_data=names[i]),
            InlineKeyboardButton(names[i+1], callback_data=names[i+1]),
            InlineKeyboardButton(names[i+2], callback_data=names[i+2])
            ])
    for i in range(number_of_3_rows_elements, number_of_provinces):
        l.append([InlineKeyboardButton(names[i], callback_data=names[i])])

    return l
