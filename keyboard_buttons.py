from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from utils import (
    WEBSITE_URL,
    FINANCIAL_CHARGE_URL,
    FINANCIAL_RECEIVE_MONEY_URL,
    CHATBOT_URL,
    THERAPISTS_URL,
    BALANCE_URL
)

button_keyboards = {
    'no_keyboard': ReplyKeyboardRemove(),

    'default_keyboard': ReplyKeyboardMarkup([
        [KeyboardButton('همسان گزینی')],
        [KeyboardButton('پروفایل'), KeyboardButton('مالی'), KeyboardButton('مشاوره')],
        [KeyboardButton('راهنما'), KeyboardButton('زیر مجموعه گیری')],
        [KeyboardButton('پشتیبانی'), KeyboardButton('درباره ما')]
    ]),

    'consultation_keyboard': ReplyKeyboardMarkup([
        [KeyboardButton('چت بات', web_app=WebAppInfo(url=CHATBOT_URL)),
         KeyboardButton('روانشناس', web_app=WebAppInfo(url=THERAPISTS_URL))],
        [KeyboardButton('بازگشت به منوی اصلی'), KeyboardButton('پرسش و پاسخ')]
    ]),

}

inline_keyboards = {
    'hamsan_gozini': {
        'main_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('جستجوی کاربران', callback_data='search_users')],
            [InlineKeyboardButton('لیست درخواست ها', callback_data='chat_requests_list')]
        ]),

        'chat_requests': InlineKeyboardMarkup([
            [InlineKeyboardButton('درخواست های چت داده شده',
                                  switch_inline_query_current_chat='درخواست های داده شده:'),
             InlineKeyboardButton('درخواست های چت گرفته شده',
                                  switch_inline_query_current_chat='درخواست های گرفته شده:')],

            [InlineKeyboardButton('بازگشت', callback_data='back')]
        ])
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

    'financial': {
        'main_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton(text='موجودی', web_app=WebAppInfo(url=BALANCE_URL)),
             InlineKeyboardButton(text='خرید پلن', callback_data='buy_plan')],

            [InlineKeyboardButton(text='دریافت وجه', web_app=WebAppInfo(url=FINANCIAL_RECEIVE_MONEY_URL)),
             InlineKeyboardButton(text='تبدیل', callback_data='financial_change')],

            [InlineKeyboardButton(text='شارژ سکه و الماس', web_app=WebAppInfo(url=FINANCIAL_CHARGE_URL))],

            [InlineKeyboardButton(text='بازگشت به منوی اصلی', callback_data='back_to_main_menu')]
        ]),

        'changes_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('الماس به سکه', callback_data='gems_to_coins'),
             InlineKeyboardButton('سکه به الماس', callback_data='coins_to_gems')],

            [InlineKeyboardButton('گیفت به سکه', callback_data='gifts_to_coins'),
             InlineKeyboardButton('گیفت به الماس', callback_data='gifts_to_gems')]
        ]),

        'receive-money_confirm': InlineKeyboardMarkup([
            [InlineKeyboardButton('تایید', callback_data='receive-money_confirm')]
        ]),

        'buy-plan': InlineKeyboardMarkup([
            [InlineKeyboardButton('برنز: 15 الماس + 2 سکه = 32,000 تومان',
                                  callback_data='bronze',
                                  url='google.com')],

            [InlineKeyboardButton('نقره: 30 الماس + 4 سکه = 58,000 تومان',
                                  callback_data='silver',
                                  url='google.com')],

            [InlineKeyboardButton('طلایی: 60 الماس + 8 سکه = 108,000 تومان',
                                  callback_data='gold',
                                  url='google.com')],
        ]),

        'charge': InlineKeyboardMarkup([
            [InlineKeyboardButton('پرداخت',
                                  callback_data='pay',
                                  url='google.com')],
        ]),

    },

    'consultation': {
        'QA': {
            'enter-question': InlineKeyboardMarkup([
                [InlineKeyboardButton('تایید ✅', callback_data='send_question'),
                 InlineKeyboardButton('نفرست ❌', callback_data='dont_send_question')]
            ]),
            # TODO: Add block inline button, And reason inline button
            'accept_question': InlineKeyboardMarkup([
                [InlineKeyboardButton('تایید ✅', callback_data='accept_question'),
                 InlineKeyboardButton('رد ❌', callback_data='reject_question')]
            ])
        }
    },

    'support': {
        'answered': InlineKeyboardMarkup([
            [InlineKeyboardButton('✅', callback_data='ticket_answered')]
        ]),
        'not_answered': InlineKeyboardMarkup([
            [InlineKeyboardButton('❌', callback_data='ticked_not_answered')]
        ])
    },

    'user_profile': {
        'chat_requests': {
            'given_menu': {
                'main_menu': InlineKeyboardMarkup([
                    [InlineKeyboardButton('مشاهده پروفایل', callback_data='show_given_user_profile')],

                    [InlineKeyboardButton('حذف از لیست و پس گرفتن درخواست', callback_data='delete_from_given_list')]
                ]),

                'profile': InlineKeyboardMarkup([
                    [InlineKeyboardButton('لایک', callback_data='like_user'),
                     InlineKeyboardButton('مسدود کردن', callback_data='block_user_from_user')],

                    [InlineKeyboardButton('افزودن به مخاطبین', callback_data='add_to_contacts'),
                     InlineKeyboardButton('گزارش کاربر', callback_data='report_user')],

                    [InlineKeyboardButton('اعلان ها', callback_data='notifications'),
                     InlineKeyboardButton('پیام دایرکت', callback_data='direct_message_request')],

                    [InlineKeyboardButton('هدیه', callback_data='gift')],

                    [InlineKeyboardButton('بازگشت', callback_data='back_to_given_menu')]
                ])
            },

            'gotten_menu': {
                'main_menu': InlineKeyboardMarkup([
                    [InlineKeyboardButton('مشاهده پروفایل', callback_data='show_gotten_user_profile')],

                    [InlineKeyboardButton('قبول ✅', callback_data='accept_chat_request'),
                     InlineKeyboardButton('رد ❌', callback_data='reject_chat_request')]
                ]),

                'profile': InlineKeyboardMarkup([
                    [InlineKeyboardButton('لایک', callback_data='like_user'),
                     InlineKeyboardButton('مسدود کردن', callback_data='block_user_from_user')],

                    [InlineKeyboardButton('افزودن به مخاطبین', callback_data='add_to_contacts'),
                     InlineKeyboardButton('گزارش کاربر', callback_data='report_user')],

                    [InlineKeyboardButton('اعلان ها', callback_data='notifications'),
                     InlineKeyboardButton('هدیه', callback_data='gift')],

                    [InlineKeyboardButton('بازگشت', callback_data='back_to_gotten_menu')]
                ])
            }
        }
    },

    'chatting': {
        'edited_keyboard': InlineKeyboardMarkup([
            [InlineKeyboardButton('ویرایش شده', callback_data='chatting_edited_message')]
        ])
    }
}
