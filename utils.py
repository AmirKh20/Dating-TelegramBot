import pickle
from os import getenv
from uuid import uuid4

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ContextTypes,
    filters
)

load_dotenv()
CHANNEL_USERNAME = getenv('CHANNEL_USERNAME')
WEBSITE_URL = getenv('WEBSITE_URL')
FINANCIAL_CHARGE_URL = getenv('FINANCIAL_CHARGE_URL')
QA_GROUP_ID = int(getenv('QA_GROUP_ID'))
QA_CHANNEL = getenv('QA_CHANNEL')
SUPPORT_GROUP_ID = int(getenv('SUPPORT_GROUP_ID'))
BOT_USERNAME = getenv('BOT_USERNAME')
COINS_PRICE = int(getenv('COINS_PRICE'))

try:
    with open('chatting_filter.pkl', 'rb') as pkl_file:
        chatting_filter = pickle.load(pkl_file)
except FileNotFoundError:
    chatting_filter = filters.Chat()


async def SendMessage(update: Update,
                      context: ContextTypes.DEFAULT_TYPE,
                      text: str,
                      reply_markup=None,
                      **kwargs) -> None:
    """
    This function sends a message in the current chat with the given text.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text,
                                   reply_markup=reply_markup,
                                   **kwargs)


async def ReplyMessage(update: Update,
                       text: str,
                       reply_keyboard_markup=None,
                       **kwargs) -> None:
    """
    This function replies to the last message the user sent with the given text
    It also replies the text with the given keyboard buttons if it was specified.
    reply_keyboard_markup: The keyboard buttons
    """
    await update.message.reply_text(text=text,
                                    reply_to_message_id=update.message.message_id,
                                    reply_markup=reply_keyboard_markup,
                                    **kwargs)


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


def GetChatRequestsGivenList(user_id):
    results = []

    if user_id == 66541247:
        message_text_content = (
            "درخواست داده به:\n"
            "/user_545132150"
        )
        results.append(InlineQueryResultArticle(id=uuid4().hex,
                                                title='امیر',
                                                input_message_content=InputTextMessageContent(
                                                    message_text=message_text_content
                                                ),
                                                )
                       )

    elif user_id == 545132150:
        message_text_content = (
            "درخواست داده به:\n"
            "/user_66541247"
        )
        results.append(InlineQueryResultArticle(id=uuid4().hex,
                                                title='علی',
                                                input_message_content=InputTextMessageContent(
                                                    message_text=message_text_content
                                                ),
                                                )
                       )

    return results


def GetChatRequestsGottenList(user_id):
    results = []

    if user_id == 66541247:
        message_text_content = (
            "درخواست گرفته از:\n"
            "/user_545132150"
        )
        results.append(InlineQueryResultArticle(id=uuid4().hex,
                                                title='امیر',
                                                input_message_content=InputTextMessageContent(
                                                    message_text=message_text_content
                                                ),
                                                )
                       )

    elif user_id == 545132150:
        message_text_content = (
            "درخواست گرفته از:\n"
            "/user_66541247"
        )
        results.append(InlineQueryResultArticle(id=uuid4().hex,
                                                title='علی',
                                                input_message_content=InputTextMessageContent(
                                                    message_text=message_text_content
                                                ),
                                                )
                       )

    return results


def GetReplyMessageId(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data = context.bot_data

    this_user_id = update.effective_user.id
    other_user_id = bot_data['chatting_with'][this_user_id]

    if 'message_ids' not in bot_data:
        bot_data['message_ids'] = {}

    if this_user_id not in bot_data['message_ids']:
        bot_data['message_ids'][this_user_id] = {}

    if other_user_id not in bot_data['message_ids']:
        bot_data['message_ids'][other_user_id] = {}

    reply_message = update.message.reply_to_message
    reply_to_message_id = None

    if reply_message and reply_message.message_id in bot_data['message_ids'][this_user_id]:
        reply_to_message_id = bot_data['message_ids'][this_user_id][reply_message.message_id]

    return reply_to_message_id


def GetEditedMessageId(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data = context.bot_data

    this_user_id = update.effective_user.id
    other_user_id = bot_data['chatting_with'][this_user_id]

    if 'message_ids' not in bot_data:
        bot_data['message_ids'] = {}

    if this_user_id not in bot_data['message_ids']:
        bot_data['message_ids'][this_user_id] = {}

    if other_user_id not in bot_data['message_ids']:
        bot_data['message_ids'][other_user_id] = {}

    edited_message = update.edited_message
    edited_message_id = None

    if edited_message and edited_message.message_id in bot_data['message_ids'][this_user_id]:
        edited_message_id = bot_data['message_ids'][this_user_id][edited_message.message_id]

    return edited_message_id
