#!/usr/bin/python3

from telegram import (
        KeyboardButton,
        ReplyKeyboardMarkup
)

keyboards = {'default_keyboard':
             ReplyKeyboardMarkup([
                [KeyboardButton('همسان گزینی')],
                [KeyboardButton('پروفایل'), KeyboardButton('خرید پلن'), KeyboardButton('مشاوره')],
                [KeyboardButton('راهنما'), KeyboardButton('زیر مجموعه گیری')],
                [KeyboardButton('پشتیبانی'), KeyboardButton('درباره ما')]
            ])
             }
