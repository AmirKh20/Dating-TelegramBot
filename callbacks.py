import json
import logging

from telegram import ForceReply, error
from telegram.ext import ConversationHandler

from keyboard_buttons import button_keyboards, inline_keyboards
from utils import *

logger = logging.getLogger('__main__')

# States in the conversation handlers

MAIN_MENU_STATE = 0

HAMSAN_GOZINI_MENU = 1

(PROFILE,
 PROFILE_CONTACTS,
 PROFILE_LIKERS,
 PROFILE_BLOCKS
 ) = range(2, 6)

FINANCIAL = 6

(FINANCIAL_CHANGES,
 FINANCIAL_CHANGES_GEMS_TO_COINS,
 FINANCIAL_CHANGES_COINS_TO_GEMS,
 FINANCIAL_CHANGES_GIFTS_TO_COINS,
 FINANCIAL_CHANGES_GIFTS_TO_GEMS
 ) = range(7, 12)

(FINANCIAL_RECEIVE_MONEY,
 FINANCIAL_RECEIVE_MONEY_ENTER_CARD
 ) = range(12, 14)

CONSULTATION = 14

(CONSULTATION_QA,
 CONSULTATION_QA_ENTER_QUESTION,
 ) = range(15, 17)

SUPPORT = 17

HAMSAN_GOZINI_CHAT_REQUESTS = 18

CHAT_REQUESTS_GIVEN = 19
CHAT_REQUESTS_GIVEN_PROFILE = 20
CHAT_REQUESTS_GOTTEN = 21
CHAT_REQUESTS_GOTTEN_PROFILE = 22

CHATTING = 23

END = ConversationHandler.END


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


async def ConsultationEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when مشاوره is sent.
    """
    await ReplyMessage(update, 'چه نوع مشاوره می خواهید؟', button_keyboards['consultation_keyboard'])
    await CheckSubs(update, context)
    return CONSULTATION


async def ConsultationTherapistCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when روانشناس is sent.
    """
    await ReplyMessage(update, 'روانشناس', button_keyboards['no_keyboard'])
    await CheckSubs(update, context)
    return END


async def ConsultationQACallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when پرسش و پاسخ is sent.
    """
    if not await CheckSubs(update, context):
        return END

    info_text = (
        'پیام توضیحات..\n'
        'لطفا سوال خود را بپرسید:'
    )
    await ReplyMessage(update, text=info_text, reply_keyboard_markup=ForceReply())

    return CONSULTATION_QA


async def ConsultationQAEnterQuestionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when after the user has sent their question.
    """
    if not await CheckSubs(update, context):
        return END

    question = update.message.text
    context.user_data['question'] = question

    text = (
        "سوال شما این است:\n"
        f"{question}\n"
        "آیا مطمئن هستید؟"
    )
    await ReplyMessage(update, text=text,
                       reply_keyboard_markup=inline_keyboards['consultation']['QA']['enter-question'])

    return CONSULTATION_QA_ENTER_QUESTION


async def ConsultationQASendQuestionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user has clicked on تایید inline button after they sent their question.
    TODO: Check if the user is blocked.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    question = context.user_data['question']

    alert_text = (
        "پیام شما فرستاده شد ✅ منتظر تایید سوال خود بمانید."
    )
    await query.answer(text=alert_text, show_alert=True)

    message_text_to_user = (
        "سوال:\n"
        f"{question}\n"
        "به ادمین ها فرستاده شد ✅ منتظر تایید سوال خود بمانید."
    )
    await query.edit_message_text(text=message_text_to_user, reply_markup=None)

    # Message that is sent to the QA Group for the admins to accept or reject:
    message_text_to_group = (
        f"user {update.effective_user.id}\n"
        "سوال:\n"
        f"{question}"
    )
    await context.bot.send_message(chat_id=QA_GROUP_ID, text=message_text_to_group,
                                   reply_markup=inline_keyboards['consultation']['QA']['accept_question'])

    await SendMessage(update, context, text='بازگشت',
                      reply_markup=button_keyboards['consultation_keyboard'])

    return CONSULTATION


async def ConsultationQADontSendQuestionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user has clicked on نفرست inline button after they sent their question.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    question = context.user_data['question']

    alert_text = (
        "پیام شما فرستاده نشد ❌"
    )
    await query.answer(text=alert_text, show_alert=True)

    message_text_to_user = (
        "سوال:\n"
        f"{question}\n"
        "فرستاده نشد ❌"
    )
    await query.edit_message_text(text=message_text_to_user, reply_markup=None)

    await SendMessage(update, context, text='بازگشت',
                      reply_markup=button_keyboards['consultation_keyboard'])

    return CONSULTATION


async def ConsultationQAAcceptQuestionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs when one of the admins in QA Group clicks on تایید inline button for a user's question
    """
    query = update.callback_query
    await query.answer()

    # The ID of the user that sent the question
    user_id = query.message.text.split()[1]
    # The question of the user
    question = query.message.text.split(':', maxsplit=1)[1]

    # The text that is sent to QA_CHANNEL
    channel_text = (
        "سوال:\n"
        f"{question}\n"
    )
    channel_message = await context.bot.send_message(chat_id=QA_CHANNEL, text=channel_text)

    # The message for QA Group
    accepting_message_to_group = (
        "سوال با موفقیت به کانال فرستاده شد\n"
        "لینک پست:\n"
        f"https://t.me/{QA_CHANNEL[1:]}/{channel_message.message_id}"
    )
    await query.edit_message_text(text=accepting_message_to_group, reply_markup=None)

    # The message for the user that has sent the question
    accepting_message_to_user = (
        "پیام شما با موفقیت تایید شد ✅\n"
        "لینک پیام در کانال:\n"
        f"https://t.me/{QA_CHANNEL[1:]}/{channel_message.message_id}"
    )
    await context.bot.send_message(chat_id=user_id, text=accepting_message_to_user)


async def ConsultationQARejectQuestionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs when one of the admins in QA Group clicks on رد inline button for a user's question
    """
    query = update.callback_query
    await query.answer()

    # The ID of the user that sent the question
    user_id = query.message.text.split()[1]
    # The question of the user
    question = query.message.text.split(':', maxsplit=1)[1]

    # The message for QA Group
    rejecting_message_to_group = (
        "سوال:\n"
        f"{question}\n"
        "رد شد ❌"
    )
    await query.edit_message_text(text=rejecting_message_to_group, reply_markup=None)

    # The message for the user that has sent the question
    rejecting_message_to_user = (
        "سوال:\n"
        f"{question}\n"
        "رد شد ❌\n"
        "لطفا سوال دیگری بفرمایید"
    )
    await context.bot.send_message(chat_id=user_id, text=rejecting_message_to_user)


async def MainMenuCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when we want to get back to the default keyboard buttons.
    """
    await ReplyMessage(update, 'منوی اصلی:', button_keyboards['default_keyboard'])
    await CheckSubs(update, context)
    return MAIN_MENU_STATE


async def HamsanGoziniEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when همسان گزینی is sent.
    Shows provinces inline keyboard if the user's profile is completed
    """
    await SendMessage(update, context, 'چک کردن پروفایل...', button_keyboards['no_keyboard'])
    is_profile_completed = True  # TODO

    if not is_profile_completed:
        await SendMessage(update, context, 'پروفایل کامل نیست')
        return await MainMenuCallback(update, context)

    message_text = (
        "یک گزینه را انتخاب کنید:"
    )
    await ReplyMessage(update,
                       text=message_text,
                       reply_keyboard_markup=inline_keyboards['hamsan_gozini']['main_keyboard'])
    return HAMSAN_GOZINI_MENU


async def HamsanGoziniChatRequestsListCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    message_text = (
        "کدام یک از لیست ها را می خواهید؟"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['hamsan_gozini']['chat_requests'])

    return HAMSAN_GOZINI_CHAT_REQUESTS


async def HamsanGoziniGoBackMenu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    message_text = (
        "یک گزینه را انتخاب کنید:"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['hamsan_gozini']['main_keyboard'])

    return HAMSAN_GOZINI_MENU


async def HamsanGoziniChatRequestsGivenListCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await CheckSubs(update, context):
        return

    query = update.inline_query

    results = GetChatRequestsGivenList(update.effective_user.id)

    await query.answer(results=results, is_personal=True, cache_time=60)


async def HamsanGoziniChatRequestsGottenListCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await CheckSubs(update, context):
        return

    query = update.inline_query

    results = GetChatRequestsGottenList(update.effective_user.id)

    await query.answer(results=results, is_personal=True, cache_time=60)


async def ChatRequestsGivenMenuCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    other_user_id = update.message.text.split()[-1].split('_', maxsplit=1)[-1]

    message_text = (
        f"{other_user_id}\n"
        "با این کاربر چیکار میخواهی کنی:"
    )
    await ReplyMessage(update,
                       text=message_text,
                       reply_keyboard_markup=inline_keyboards['user_profile']['chat_requests']['given_menu'][
                           'main_menu'])

    return CHAT_REQUESTS_GIVEN


async def ChatRequestsGivenShowProfileCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = query.message.text.split(maxsplit=1)[0]
    message_text = (
        f"{other_user_id}\n"
        "پروفایل طرف شامل فیلد های فلان..."
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['user_profile']['chat_requests']['given_menu'][
                                      'profile'])

    return CHAT_REQUESTS_GIVEN_PROFILE


async def ChatRequestsGivenProfileGoBackCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = query.message.text.split(maxsplit=1)[0]
    message_text = (
        f"{other_user_id}\n"
        "با این کاربر چیکار میخواهی کنی:"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['user_profile']['chat_requests']['given_menu'][
                                      'main_menu'])

    return CHAT_REQUESTS_GIVEN


async def ChatRequestsGottenMenuCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    other_user_id = update.message.text.split()[-1].split('_', maxsplit=1)[-1]

    message_text = (
        f"{other_user_id}\n"
        "با این کاربر چیکار میخواهی کنی:"
    )
    await ReplyMessage(update,
                       text=message_text,
                       reply_keyboard_markup=inline_keyboards['user_profile']['chat_requests']['gotten_menu'][
                           'main_menu'])

    return CHAT_REQUESTS_GOTTEN


async def ChatRequestsGottenAcceptRequestCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = int(query.message.text.split(maxsplit=1)[0])
    this_user_id = int(update.effective_user.id)

    message_text_to_this_user = (
        "درخواست "
        f"{other_user_id} "
        "پذیرفته شد!"
    )
    await query.edit_message_text(text=message_text_to_this_user)

    start_chatting_message_to_this_user = (
        "شروع به چت با "
        f"{other_user_id} "
        "کنید.\n"
        "برای پایان و کنسل کردن چت "
        "/end_chat "
        "رو بفرست."
    )
    await SendMessage(update,
                      context,
                      text=start_chatting_message_to_this_user,
                      reply_markup=button_keyboards['no_keyboard'])

    start_chatting_message_to_other_user = (
        "درخواست چت شما از طرف "
        f"{this_user_id} "
        "قبول شد!\n"
        "شروع به چت کردن کن\n"
        "برای پایان و کنسل کردن چت "
        "/end_chat "
        "رو بفرست."
    )
    await context.bot.send_message(chat_id=other_user_id,
                                   text=start_chatting_message_to_other_user,
                                   reply_markup=button_keyboards['no_keyboard'])

    chatting_filter.add_chat_ids([other_user_id, this_user_id])
    with open('chatting_filter.pkl', 'wb') as file:
        pickle.dump(chatting_filter, file)

    context.bot_data[other_user_id] = this_user_id
    context.bot_data[this_user_id] = other_user_id

    return END


async def ChatRequestsGottenRejectRequestCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = int(query.message.text.split(maxsplit=1)[0])
    this_user_id = int(update.effective_user.id)

    message_text_to_this_user = (
        "درخواست "
        f"{other_user_id} "
        "رد شد!"
    )
    await query.edit_message_text(text=message_text_to_this_user)

    rejecting_message_to_other_user = (
        "درخواست چت شما از طرف "
        f"{this_user_id} "
        "رد شد!\n"
    )
    await context.bot.send_message(chat_id=other_user_id,
                                   text=rejecting_message_to_other_user)

    # TODO: Deleting from both lists the ids of the users

    return END


async def ChatRequestsGottenShowProfileCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = query.message.text.split(maxsplit=1)[0]
    message_text = (
        f"{other_user_id}\n"
        "پروفایل طرف شامل فیلد های فلان..."
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['user_profile']['chat_requests']['gotten_menu'][
                                      'profile'])

    return CHAT_REQUESTS_GOTTEN_PROFILE


async def ChatRequestsGottenProfileGoBackCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    other_user_id = query.message.text.split(maxsplit=1)[0]
    message_text = (
        f"{other_user_id}\n"
        "با این کاربر چیکار میخواهی کنی:"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['user_profile']['chat_requests']['gotten_menu'][
                                      'main_menu'])

    return CHAT_REQUESTS_GOTTEN


async def ChattingCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bot_data = context.bot_data
    this_user_id = update.effective_user.id

    if this_user_id not in bot_data:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data[this_user_id]

    message = update.message
    reply_message = message.reply_to_message
    reply_to_message_id = None

    if reply_message and reply_message.message_id in bot_data:
        reply_to_message_id = bot_data[reply_message.message_id]

    message_bot_sent = await context.bot.send_message(chat_id=other_user_id,
                                                      text=message.text,
                                                      write_timeout=30,
                                                      connect_timeout=30,
                                                      reply_to_message_id=reply_to_message_id)

    bot_data[message_bot_sent.message_id] = message.message_id
    bot_data[message.message_id] = message_bot_sent.message_id

    return CHATTING


async def ErrorHandler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not isinstance(update, Update):
        return

    logger.exception(f"Exception in error handler for user {update.effective_user.id}:", exc_info=context.error)

    if isinstance(context.error, error.TimedOut):
        await ReplyMessage(update,
                           text='مشکلی پیش آمد. لطفا دوباره پیام خود را بفرستید',
                           **{"write_timeout": 30, "connect_timeout": 30})


async def ChattingEndChatCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bot_data = context.bot_data
    this_user_id = update.effective_user.id

    if this_user_id not in bot_data:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = context.bot_data[this_user_id]

    chatting_filter.remove_chat_ids([this_user_id, other_user_id])
    with open('chatting_filter.pkl', 'wb') as file:
        pickle.dump(chatting_filter, file)

    del bot_data[this_user_id]
    del bot_data[other_user_id]

    message_text_to_other_user = (
        "چت با "
        f"/user_{this_user_id} "
        "توسط ایشان پایان یافت!"
    )
    await context.bot.send_message(chat_id=other_user_id,
                                   text=message_text_to_other_user,
                                   connect_timeout=30)
    canceling_message_text = (
        "برای بازگشت به منوی اصلی روی "
        "/main_menu "
        "کلیک کنید"
    )
    await context.bot.send_message(chat_id=other_user_id,
                                   text=canceling_message_text,
                                   connect_timeout=30)

    message_text_to_this_user = (
        "چت با "
        f"/user_{other_user_id} "
        "پایان یافت!"
    )
    await ReplyMessage(update,
                       text=message_text_to_this_user,
                       **{"connect_timeout": 30})

    canceling_message_text = (
        "بازگشت به منوی اصلی"
    )
    await SendMessage(update, context,
                      text=canceling_message_text,
                      reply_markup=button_keyboards['default_keyboard'],
                      **{"connect_timeout": 30})
    return END


async def ProfileEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when پروفایل is sent. It's the entry point of the profile conversation handler.
    """
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
    """
    Runs when ویرایش پروفایل is sent in profile conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    return PROFILE


async def ProfileContactsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when مخاطبین is sent in profile conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    await query.edit_message_text('لیست مخاطبین',
                                  reply_markup=inline_keyboards['my_profile']['contacts_keyboard'])  # TODO

    return PROFILE_CONTACTS


async def ProfileLikersCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when لایک کننده ها is sent in profile conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    await query.edit_message_text('لیست لایک کننده ها:',
                                  reply_markup=inline_keyboards['my_profile']['likers_keyboard'])  # TODO

    return PROFILE_LIKERS


async def ProfileBlocksCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when لیست مسدودی ها is sent in profile conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    await query.edit_message_text('لیست مسدودی ها:',
                                  reply_markup=inline_keyboards['my_profile']['blocks_keyboard'])  # TODO

    return PROFILE_BLOCKS


async def ProfileNumberOfLikesOnOff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when فعال/غیر فعال کردن لایک is sent in profile conversation handler.
    """
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
    """
    Runs when بازگشت is sent in profile conversation handler.
    """
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


async def FinancialEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when مالی is sent. It goes into financial conversation handler.
    """
    await ReplyMessage(update, 'یک گزینه را انتخاب کنید:', reply_keyboard_markup=button_keyboards['financial_keyboard'])

    if not await CheckSubs(update, context):
        return END

    return FINANCIAL


async def FinancialBuyPlanCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when خرید پلن is sent in financial conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    plans = (
        "پلن های ماهانه:\n"
        "برنز: 15 الماس + 2 سکه = 32,000 تومان\n"
        "نقره: 30 الماس + 4 سکه = 58,000 تومان\n"
        "طلایی: 60 الماس + 8 سکه = 108,000 تومان\n"
    )
    await ReplyMessage(update, text=plans, reply_keyboard_markup=inline_keyboards['financial']['buy-plan'])

    return FINANCIAL


async def FinancialBalanceCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when موجودی is sent in financial conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    text = (
        "سکه:\n"
        "الماس:\n"
        "موجودی ریالی:\n"
        "تعداد گیفت ها و یوزر ارسال کننده:\n"
        "مدت زمان باقی مانده از پلن فلان:"
    )
    await ReplyMessage(update, text=text)

    return FINANCIAL


async def FinancialChangesCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل is sent in financial conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    await ReplyMessage(update,
                       text='یک گزینه را انتخاب کنید',
                       reply_keyboard_markup=inline_keyboards['financial']['changes_keyboard'])

    return FINANCIAL_CHANGES


async def FinancialChangesGemsToCoinsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل الماس به سکه is clicked.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    text = 'تعداد الماس ها را وارد کنید:'
    await SendMessage(update, context, text=text, reply_markup=ForceReply(input_field_placeholder='مثلا 10'))

    return FINANCIAL_CHANGES_GEMS_TO_COINS


async def FinancialChangesGemsToCoinsReadGemsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل الماس به سکه has been clicked. And it reads the user input for how many gems.
    """
    if not await CheckSubs(update, context):
        return END

    gems_input = update.message.text

    await ReplyMessage(update, text=f'چک کردن موجودی الماس ها برای {gems_input} الماس...')
    await SendMessage(update, context, text='تبدیل الماس به سکه...')
    await SendMessage(update, context, text='با موفقیت انجام شد...\nموجودی:',
                      reply_markup=button_keyboards['financial_keyboard'])

    return FINANCIAL


async def FinancialChangesCoinsToGemsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل سکه به الماس is clicked.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    text = 'تعداد سکه ها را وارد کنید:'
    await SendMessage(update, context, text=text, reply_markup=ForceReply(input_field_placeholder='مثلا 10'))

    return FINANCIAL_CHANGES_COINS_TO_GEMS


async def FinancialChangesCoinsToGemsReadCoinsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل سکه به الماس has been clicked. And it reads the user input for how many coins.
    """
    if not await CheckSubs(update, context):
        return END

    coins_input = update.message.text

    await ReplyMessage(update, text=f'چک کردن موجودی سکه ها برای {coins_input} سکه...')
    await SendMessage(update, context, text='تبدیل سکه به الماس...')
    await SendMessage(update, context, text='با موفقیت انجام شد...\nموجودی:',
                      reply_markup=button_keyboards['financial_keyboard'])

    return FINANCIAL


async def FinancialChangesGiftsToCoinsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل گیفت به سکه is clicked.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    text = 'گیفت مورد نظر را وارد کنید:'
    await SendMessage(update, context, text=text, reply_markup=ForceReply())

    return FINANCIAL_CHANGES_GIFTS_TO_COINS


async def FinancialChangesGiftsToCoinsReadGiftsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل گیفت به سکه has been clicked. And it reads the user input for the inputted gift.
    """
    if not await CheckSubs(update, context):
        return END

    gift_input = update.message.text

    await ReplyMessage(update, text=f'چک کردن موجودی گیفت ها برای گیفت {gift_input}')
    await SendMessage(update, context, text='تبدیل گیفت به سکه...')
    await SendMessage(update, context, text='با موفقیت انجام شد...\nموجودی:',
                      reply_markup=button_keyboards['financial_keyboard'])

    return FINANCIAL


async def FinancialChangesGiftsToGemsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل گیفت به الماس is clicked.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    text = 'گیفت مورد نظر را وارد کنید:'
    await SendMessage(update, context, text=text, reply_markup=ForceReply())

    return FINANCIAL_CHANGES_GIFTS_TO_GEMS


async def FinancialChangesGiftsToGemsReadGiftsCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل گیفت به الماس has been clicked. And it reads the user input for the inputted gift.
    """
    if not await CheckSubs(update, context):
        return END

    gift_input = update.message.text

    await ReplyMessage(update, text=f'چک کردن موجودی گیفت ها برای گیفت {gift_input}')
    await SendMessage(update, context, text='تبدیل گیفت به الماس...')
    await SendMessage(update, context, text='با موفقیت انجام شد...\nموجودی:',
                      reply_markup=button_keyboards['financial_keyboard'])

    return FINANCIAL


async def FinancialReceiveMoneyCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when دریافت وجه is sent in the financial conversation handler.
    """
    if not await CheckSubs(update, context):
        return END

    await ReplyMessage(update, text='نمایش تعداد موجودی گیفت ها و هزینه ریالی...',
                       reply_keyboard_markup=inline_keyboards['financial']['receive-money_keyboard'])

    return FINANCIAL_RECEIVE_MONEY


async def FinancialReceiveMoneyCallbackQuery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when برداشت وجه is clicked and it wants the user's card info.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    text = 'شماره کارت خود را همراه مشخصات وارد کنید:'
    await SendMessage(update, context, text=text, reply_markup=ForceReply())

    return FINANCIAL_RECEIVE_MONEY_ENTER_CARD


async def FinancialReceiveMoneyEnterCardCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when برداشت وجه has been clicked and it reads the user's card info.
    """
    if not await CheckSubs(update, context):
        return END

    card = update.message.text

    await ReplyMessage(update, text='لطفا تا اطلاع ثانویه صبر کنید..')
    await ReplyMessage(update, text=f'واریزی ... برای کارت\n{card}\nموفقیت آمیز بود.')
    await SendMessage(update, context, text='موجودی:',
                      reply_markup=button_keyboards['financial_keyboard'])

    return FINANCIAL


async def FinancialChargeCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when شارژ سکه و الماس has been clicked and the user went to the web app for this button.
    The bot reads the gems and coins from web app and ask the user to pay.
    """
    if not await CheckSubs(update, context):
        return END

    data = json.loads(update.effective_message.web_app_data.data)

    text = (
        "شما "
        f"{data['Gems']} "
        "الماس و "
        f"{data['Coins']} "
        "سکه انتخاب کردید. برای پرداخت روی گزینه پرداخت کلیک کنید."
    )
    await ReplyMessage(update, text=text, reply_keyboard_markup=inline_keyboards['financial']['charge'])

    return FINANCIAL


async def DownLineCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when زیر مجموعه گیری is sent.
    """
    if not await CheckSubs(update, context):
        return END

    await ReplyMessage(update, text='توضیحات زیر مجموعه های گرفته شده..')

    return MAIN_MENU_STATE


async def SupportEntryCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when پشتیبانی is sent.
    """
    if not await CheckSubs(update, context):
        return END

    text = (
        "توضیحات:\n"
        "لطفا پیام خود را ارسال کنید:"
    )
    await ReplyMessage(update, text=text, reply_keyboard_markup=ForceReply())

    return SUPPORT


async def SupportEnterTicketCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback function to read the user ticket
    """
    if not await CheckSubs(update, context):
        return END

    ticket = update.message.text
    user_id = update.effective_user.id

    message_to_support_group = (
        f"user {user_id}\n"
        "تیکت:\n"
        f"{ticket}\n\n"
        "وضعیت پاسخگویی: پاسخ داده نشده ❌"
    )
    await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=message_to_support_group,
                                   reply_markup=inline_keyboards['support']['not_answered'])

    message_to_user = (
        "تیکت شما دریافت شد. ✅\n"
        "منتظر پاسخ بمانید."
    )
    await ReplyMessage(update, text=message_to_user,
                       reply_keyboard_markup=button_keyboards['default_keyboard'])

    return MAIN_MENU_STATE


async def SupportAnswerTicketCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Callback function to answer the user's ticket in the SUPPORT_GROUP_ID chat.
    """
    message = update.message.reply_to_message

    if message.reply_markup.inline_keyboard[0][0].callback_data == 'ticket_answered':
        await ReplyMessage(update, text='پاسخ این تیکت از قبل فرستاده شده!')
        return

    ticket = message.text[message.text.find('تیکت:') + 6: message.text.rfind('وضعیت') - 1]
    ticket_answer = update.message.text

    user_id = message.text.split()[1]

    edited_message_to_group = message.text[:-6] + "شده ✅"
    await context.bot.edit_message_text(chat_id=SUPPORT_GROUP_ID,
                                        message_id=message.message_id,
                                        text=edited_message_to_group,
                                        reply_markup=inline_keyboards['support']['answered'])

    message_to_user = (
        "تیکت:\n"
        f"{ticket}\n"
        "پاسخ داده شد ✅\n"
        "پاسخ:\n"
        f"{ticket_answer}"
    )
    await context.bot.send_message(chat_id=user_id,
                                   text=message_to_user)
