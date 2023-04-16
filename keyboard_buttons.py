from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup
)
from utils import GetProvinceNamesInlineSequence

button_keyboards = {
    'no_keyboard': ReplyKeyboardRemove(),
    'default_keyboard': ReplyKeyboardMarkup([
        [KeyboardButton('همسان گزینی')],
        [KeyboardButton('پروفایل'), KeyboardButton('خرید پلن'), KeyboardButton('مشاوره')],
        [KeyboardButton('راهنما'), KeyboardButton('زیر مجموعه گیری')],
        [KeyboardButton('پشتیبانی'), KeyboardButton('درباره ما')]
    ]),
    'consultation_keyboard': ReplyKeyboardMarkup([
        [KeyboardButton('چت بات'), KeyboardButton('روانشناس')],
        [KeyboardButton('پرسش و پاسخ'), KeyboardButton('بازگشت به منوی اصلی')]
    ])
}

inline_keyboards = {
    'hamsan_gozini_keyboard': {
        'provinces': InlineKeyboardMarkup(GetProvinceNamesInlineSequence())
    }
}
