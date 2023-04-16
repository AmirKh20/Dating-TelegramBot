from telegram.ext import ConversationHandler

from keyboard_buttons import button_keyboards, inline_keyboards
from utils import *

MAIN_MENU_STATE, CONSULTATION_STATE = range(2)
END = ConversationHandler.END
PROVINCE1, PROVINCE2, PROVINCE3 = range(2, 5)


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
    await SendMessage(update, context, 'چک کردن پروفایل...', button_keyboards['no_keyboard'])
    is_profile_completed = True  # TODO

    if is_profile_completed:
        await ReplyMessage(update,
                           'استان مورد نظر را انتخاب کنید',
                           inline_keyboards['hamsan_gozini_keyboard']['provinces']['page_1'])
        return PROVINCE1

    await SendMessage(update, context, 'پروفایل کامل نیست')
    return await MainMenuCallback(update, context)


async def HamsanGoziniProvincesCallback_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    if query.data == 'بعدی':
        await query.edit_message_text(text='استان مورد نظر را انتخاب کنید',
                                      reply_markup=inline_keyboards['hamsan_gozini_keyboard']['provinces']['page_2'])
        return PROVINCE2
    else:  # TODO
        await query.edit_message_text('لیست کاربران')
        return END


async def HamsanGoziniProvincesCallback_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    if query.data == 'بعدی':
        await query.edit_message_text(text='استان مورد نظر را انتخاب کنید',
                                      reply_markup=inline_keyboards['hamsan_gozini_keyboard']['provinces']['page_3'])
        return PROVINCE3
    elif query.data == 'قبلی':
        await query.edit_message_text(text='استان مورد نظر را انتخاب کنید',
                                      reply_markup=inline_keyboards['hamsan_gozini_keyboard']['provinces']['page_1'])
        return PROVINCE1
    else:  # TODO
        await query.edit_message_text('لیست کاربران')
        return END


async def HamsanGoziniProvincesCallback_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    if query.data == 'قبلی':
        await query.edit_message_text(text='استان مورد نظر را انتخاب کنید',
                                      reply_markup=inline_keyboards['hamsan_gozini_keyboard']['provinces']['page_2'])
        return PROVINCE2
    else:  # TODO
        await query.edit_message_text('لیست کاربران')
        return END
