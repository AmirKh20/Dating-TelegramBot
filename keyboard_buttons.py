from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils import GetProvinceNamesInlineSequence, WEBSITE_URL

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
    },
    'my_profile': {
        'main_keyboard_likes_on': InlineKeyboardMarkup([
            [InlineKeyboardButton('ویرایش پروفایل', callback_data='profile_edit', url=WEBSITE_URL)],

            [InlineKeyboardButton('مخاطبین', callback_data='contacts'),
             InlineKeyboardButton('لایک کننده ها', callback_data='likers')],

            [InlineKeyboardButton('لیست مسدودی ها', callback_data='blocks'),
             InlineKeyboardButton('فعال/غیر فعال لایک ✅', callback_data='on_off_number_likes')]
        ]),
        'main_keyboard_likes_off': InlineKeyboardMarkup([
            [InlineKeyboardButton('ویرایش پروفایل', callback_data='profile_edit', url=WEBSITE_URL)],

            [InlineKeyboardButton('مخاطبین', callback_data='contacts'),
             InlineKeyboardButton('لایک کننده ها', callback_data='likers')],

            [InlineKeyboardButton('لیست مسدودی ها', callback_data='blocks'),
             InlineKeyboardButton('فعال/غیرفعال لایک ❌', callback_data='on_off_number_likes')]
        ]),
        'contacts_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('بازگشت', callback_data='back_to_profile')]
        ]),
        'likers_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('بازگشت', callback_data='back_to_profile')]
        ]),
        'blocks_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('بازگشت', callback_data='back_to_profile')]
        ]),
    },
}
