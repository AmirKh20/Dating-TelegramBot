from telegram.ext import ConversationHandler

from keyboard_buttons import button_keyboards, inline_keyboards
from utils import *

MAIN_MENU_STATE, CONSULTATION_STATE = range(2)
END = ConversationHandler.END
PROVINCES = 2
PROFILE, PROFILE_CONTACTS, PROFILE_LIKERS, PROFILE_BLOCKS = range(3, 7)


async def StartCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when /start command is sent. The default home keyboards are shown.
    """
    await ReplyMessage(update, 'سلام و خوش آمدید به ربات سوشیانت!', button_keyboards['default_keyboard'])
    await SendMessage(update, context, 'اطلاعاتی درمورد ربات')
    await SendMessage(update, context, 'با دستور /help کمک بگیرید')
    await CheckSubs(update, context)
    return MAIN_MENU_STATE


async def HelpCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs when /help command is sent.
    Doesn't show anything if the users aren't subscribed.
    """
    if not await CheckSubs(update, context):
        return

    await SendMessage(update, context, 'این خروجی هلپ است')


async def ConsultationCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when مشاوره is sent. The consultation keyboard is shown.
    """
    await ReplyMessage(update, 'چه نوع مشاوره می خواهید؟', button_keyboards['consultation_keyboard'])
    await CheckSubs(update, context)
    return CONSULTATION_STATE


async def MainMenuCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when we want to get back to the default keyboard buttons.
    """
    await ReplyMessage(update, 'منوی اصلی:', button_keyboards['default_keyboard'])
    await CheckSubs(update, context)
    return MAIN_MENU_STATE


async def TherapistCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    TODO
    """
    await ReplyMessage(update, 'روانشناس', button_keyboards['no_keyboard'])
    await CheckSubs(update, context)
    return END


async def HamsanGoziniEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when همسان گزینی is sent.
    Shows provinces inline keyboard if the user's profile is completed
    """
    await SendMessage(update, context, 'چک کردن پروفایل...', button_keyboards['no_keyboard'])
    is_profile_completed = True  # TODO

    if is_profile_completed:
        await ReplyMessage(update,
                           'استان مورد نظر را انتخاب کنید',
                           inline_keyboards['hamsan_gozini_keyboard']['provinces'])
        return PROVINCES

    await SendMessage(update, context, 'پروفایل کامل نیست')
    return await MainMenuCallback(update, context)


async def HamsanGoziniProvincesCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user has clicked on one of the provinces.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    await query.edit_message_text('لیست کاربران')  # TODO
    return END


async def ProfileEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    text = (
        "اسم:\n"
        "سن:\n"
        "شهر:\n"
        "استان:\n"
        "جنسیت:\n"
        "گرایش:\n"
        "بیوگرافی:\n"
        "مهارت ها:\n"
        "علاقه مندی ها:\n"
        "تعداد لایک ها:\n"
        "عکس پروفایل:"
    )
    if 'is_likes_on' not in context.user_data:
        context.user_data['is_likes_on'] = True

    if context.user_data['is_likes_on']:
        await ReplyMessage(update, text, inline_keyboards['my_profile']['main_keyboard_likes_on'])
    else:
        await ReplyMessage(update, text, inline_keyboards['my_profile']['main_keyboard_likes_off'])
    return PROFILE


async def ProfileEditCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()
    return PROFILE


async def ProfileContactsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()
    await query.edit_message_text('لیست مخاطبین',
                                  reply_markup=inline_keyboards['my_profile']['contacts_keyboard'])  # TODO
    return PROFILE_CONTACTS


async def ProfileLikersCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()
    await query.edit_message_text('لیست لایک کننده ها:',
                                  reply_markup=inline_keyboards['my_profile']['likers_keyboard'])  # TODO
    return PROFILE_LIKERS


async def ProfileBlocksCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()
    await query.edit_message_text('لیست مسدودی ها:',
                                  reply_markup=inline_keyboards['my_profile']['blocks_keyboard'])  # TODO
    return PROFILE_BLOCKS


async def ProfileNumberOfLikesOnOff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    if context.user_data['is_likes_on']:
        await query.answer(text='اکنون تعداد افرادی که لایک ـتان کرده اند برای بقیه نشان داده نمی شود ❌',
                           show_alert=True)
        await query.edit_message_reply_markup(reply_markup=inline_keyboards['my_profile']['main_keyboard_likes_off'])
        context.user_data['is_likes_on'] = False
    else:
        await query.answer(text='اکنون تعداد افرادی که لایک ـتان کرده اند برای بقیه نشان داده می شود ✅',
                           show_alert=True)
        await query.edit_message_reply_markup(reply_markup=inline_keyboards['my_profile']['main_keyboard_likes_on'])
        context.user_data['is_likes_on'] = True
    return PROFILE


async def BackToProfileCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    text = (
        "اسم:\n"
        "سن:\n"
        "شهر:\n"
        "استان:\n"
        "جنسیت:\n"
        "گرایش:\n"
        "بیوگرافی:\n"
        "مهارت ها:\n"
        "علاقه مندی ها:\n"
        "تعداد لایک ها:\n"
        "عکس پروفایل:"
    )

    query = update.callback_query
    await query.answer()

    if context.user_data['is_likes_on']:
        await query.edit_message_text(text=text, reply_markup=inline_keyboards['my_profile']['main_keyboard_likes_on'])
    else:
        await query.edit_message_text(text=text, reply_markup=inline_keyboards['my_profile']['main_keyboard_likes_off'])

    return PROFILE
