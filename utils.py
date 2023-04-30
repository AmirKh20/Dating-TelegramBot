import json
from os import getenv
from uuid import uuid4

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup
from telegram.ext import ContextTypes

load_dotenv()
CHANNEL_USERNAME = getenv('CHANNEL_USERNAME')
PROVINCES_FILE = getenv('PROVINCES_FILE', 'provinces_cities.json')
WEBSITE_URL = getenv('WEBSITE_URL')
FINANCIAL_CHARGE_URL = getenv('FINANCIAL_CHARGE_URL')
QA_GROUP_ID = int(getenv('QA_GROUP_ID'))
QA_CHANNEL = getenv('QA_CHANNEL')
SUPPORT_GROUP_ID = int(getenv('SUPPORT_GROUP_ID'))


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
    """
    Utility to get the provinces' names from a json file
    :return: list of strings containing the names of the provinces.
    """
    with open(PROVINCES_FILE, 'r') as json_file:
        data = json.load(json_file)
    names = [province['name'] for province in data]
    return names


def GetProvinceNamesInlineSequence():
    """
    Utility to get provinces' names in a 2D list of InlineKeyboardButton with 3 columns.
    :return: 2D list of InlineKeyboardButton.
    """
    names = GetProvinceNames()
    number_of_provinces = len(names)
    number_of_3_rows_elements = number_of_provinces - number_of_provinces % 3  # for 31 provinces, this is equal to 30

    buttons = []
    for i in range(0, number_of_3_rows_elements, 3):
        buttons.append([
            InlineKeyboardButton(names[i], callback_data=names[i]),
            InlineKeyboardButton(names[i + 1], callback_data=names[i + 1]),
            InlineKeyboardButton(names[i + 2], callback_data=names[i + 2])
        ])
    # The rest of the provinces:
    for i in range(number_of_3_rows_elements, number_of_provinces):
        buttons.append([InlineKeyboardButton(names[i], callback_data=names[i])])

    return buttons


def GetChatRequestsGivenList(user_id):
    results = []
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('مشاهده پروفایل', callback_data='show_user_profile')],
        [InlineKeyboardButton('حذف از لیست و پس گرفتن درخواست', callback_data='delete_from_given_list')]
    ])
    results.append(InlineQueryResultArticle(id=uuid4().hex,
                                            title='امیر',
                                            input_message_content=InputTextMessageContent(
                                                'پروفایل فرد شامل شهر و سن و عکس و ...'
                                            ),
                                            reply_markup=reply_markup
                                            )
                   )
    results.append(InlineQueryResultArticle(id=uuid4().hex,
                                            title='علی',
                                            input_message_content=InputTextMessageContent(
                                                'پروفایل فرد شامل شهر و سن و عکس و ...'
                                            ),
                                            reply_markup=reply_markup
                                            )
                   )

    return results
