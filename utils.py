#!/usr/bin/python3

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from dotenv import load_dotenv
from os import getenv

load_dotenv()
CHANNEL_USERNAME = getenv('CHANNEL_USERNAME')


async def SendMessage(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def ReplyMessage(update: Update, text: str) -> None:
    await update.message.reply_text(text, reply_to_message_id=update.message.message_id)


async def CheckSubs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=update.message.chat_id)
    if chat_member['status'] in ['left', 'kicked']:
        await ReplyMessage(update, f'لطفا در کانال {CHANNEL_USERNAME} عضو شوید!')
        return False
    return True


async def ReplyMessageKeyboardButton(update: Update, reply_keyboard_markup: ReplyKeyboardMarkup, text: str = None) -> None:
    await update.message.reply_text(text,
                                    reply_to_message_id=update.message.message_id,
                                    reply_markup=reply_keyboard_markup)
