from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup
)

keyboards = {
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
