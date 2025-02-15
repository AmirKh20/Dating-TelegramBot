import json
import logging
import re

from telegram import (
    ForceReply,
    error,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo
)
from telegram.ext import ConversationHandler

from keyboard_buttons import button_keyboards, inline_keyboards
from utils import *

logger = logging.getLogger('__main__')

# States in the conversation handlers
(MAIN_MENU_STATE,

 HAMSAN_GOZINI_MENU,

 PROFILE,
 PROFILE_CONTACTS,
 PROFILE_LIKERS,
 PROFILE_BLOCKS,

 FINANCIAL,

 FINANCIAL_CHANGES,
 FINANCIAL_CHANGES_GEMS_TO_COINS,
 FINANCIAL_CHANGES_COINS_TO_GEMS,
 FINANCIAL_CHANGES_GIFTS_TO_COINS,
 FINANCIAL_CHANGES_GIFTS_TO_GEMS,

 FINANCIAL_RECEIVE_MONEY,

 CONSULTATION,

 CONSULTATION_QA,
 CONSULTATION_QA_ENTER_QUESTION,

 SUPPORT,

 HAMSAN_GOZINI_CHAT_REQUESTS,

 CHAT_REQUESTS_GIVEN,
 CHAT_REQUESTS_GIVEN_PROFILE,
 CHAT_REQUESTS_GOTTEN,
 CHAT_REQUESTS_GOTTEN_PROFILE,

 CHATTING
 ) = range(0, 23)

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
    Runs when روانشناس is clicked.
    """
    web_app_data = json.loads(update.effective_message.web_app_data.data)

    name = web_app_data['name']
    email = web_app_data['email']
    phone_number = web_app_data['phone_number']
    doctor = web_app_data['doctor']
    date = web_app_data['date']

    message_text = (
        "درخواست روانشناس به نام "
        f"`{name}`, "
        "با ایمیل "
        f"`{email}`, "
        "شماره تلفن: "
        f"`{phone_number}`, "
        "برای دکتر "
        f"`{doctor}`, "
        "به تاریخ: "
        f"`{date}` "
        "ثبت شد\."
    )
    await ReplyMessage(update,
                       text=message_text,
                       **{'parse_mode': 'MarkdownV2'})
    return CONSULTATION


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
    query = update.callback_query
    if query:
        await query.answer()
        await SendMessage(update, context,
                          text='منوی اصلی:', reply_markup=button_keyboards['default_keyboard'])
    else:
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
    """
    Runs when the user clicks on لیست درخواست ها in the hamsan-gozini menu
    """
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
    """
    Runs when the user wants to go back to the hamsan-gozini menu
    """
    query = update.callback_query
    await query.answer()

    message_text = (
        "یک گزینه را انتخاب کنید:"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['hamsan_gozini']['main_keyboard'])

    return HAMSAN_GOZINI_MENU


async def HamsanGoziniChatRequestsGivenListCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inline query handler for listing the users' given chat requests
    """
    if not await CheckSubs(update, context):
        return

    query = update.inline_query

    results = GetChatRequestsGivenList(update.effective_user.id)

    await query.answer(results=results, is_personal=True, cache_time=60)


async def HamsanGoziniChatRequestsGottenListCallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inline query handler for listing the users' gotten chat requests
    """
    if not await CheckSubs(update, context):
        return

    query = update.inline_query

    results = GetChatRequestsGottenList(update.effective_user.id)

    await query.answer(results=results, is_personal=True, cache_time=60)


async def ChatRequestsGivenMenuCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user clicks on one of their given chat requests.
    This function shows some options for that user.
    """
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
    """
    Runs when the user wants to see the profile of a given chat request
    """
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
    """
    Runs when the user wants to go back from the given chat request profile
    """
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
    """
    Runs when the user clicks on one of their gotten chat requests.
    This function shows some options for that user.
    """
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
    """
    Runs when the user accepts a gotten chat request
    """
    query = update.callback_query
    await query.answer()

    other_user_id = int(query.message.text.split(maxsplit=1)[0])
    this_user_id = int(update.effective_user.id)

    # Add the users id to the chatting_filter
    chatting_filter.add_chat_ids([other_user_id, this_user_id])
    # Save the chatting_filter in a pickle file
    with open('chatting_filter.pkl', 'wb') as file:
        pickle.dump(chatting_filter, file)

    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    # Save user ids in bot_data['chatting_with'] dictionary
    bot_data['chatting_with'][other_user_id] = this_user_id
    bot_data['chatting_with'][this_user_id] = other_user_id

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

    return END


async def ChatRequestsGottenRejectRequestCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user rejects a gotten chat request
    """
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
    """
    Runs when the user wants to see the profile of a gotten chat request
    """
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
    """
    Runs when the user wants to go back from the gotten chat request profile
    """
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
    """
    Callback function for sending messages in a chat between users
    """
    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    this_user_id = update.effective_user.id
    if this_user_id not in bot_data['chatting_with']:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data['chatting_with'][this_user_id]

    message = update.message
    if message.forward_date:  # If the message is forwarded, forward it
        message_bot_sent = await context.bot.forward_message(chat_id=other_user_id,
                                                             from_chat_id=this_user_id,
                                                             message_id=message.message_id,
                                                             write_timeout=30,
                                                             connect_timeout=30)
    else:
        # Get the reply message id if the message is a reply.
        reply_to_message_id = GetReplyMessageId(update, context)
        message_bot_sent = await context.bot.copy_message(chat_id=other_user_id,
                                                          from_chat_id=this_user_id,
                                                          message_id=message.message_id,
                                                          write_timeout=30,
                                                          connect_timeout=30,
                                                          reply_to_message_id=reply_to_message_id)

    # Linking messages the user sent with that message in another chat which the bot has sent
    bot_data['message_ids'][other_user_id][message_bot_sent.message_id] = message.message_id
    bot_data['message_ids'][this_user_id][message.message_id] = message_bot_sent.message_id

    return CHATTING


async def ChattingEditedTextCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback function for text-edited messages
    """
    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    this_user_id = update.effective_user.id
    if this_user_id not in bot_data['chatting_with']:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data['chatting_with'][this_user_id]

    edited_message = update.edited_message
    edited_message_id = GetEditedMessageId(update, context)

    if edited_message_id:  # If an edited message id was found in the current chat
        await context.bot.edit_message_text(chat_id=other_user_id,
                                            message_id=edited_message_id,
                                            text=edited_message.text,
                                            entities=edited_message.entities,
                                            reply_markup=inline_keyboards['chatting']['edited_keyboard'])

    return CHATTING


async def ChattingEditedMediaCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback function for media-edited messages
    """
    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    this_user_id = update.effective_user.id
    if this_user_id not in bot_data['chatting_with']:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data['chatting_with'][this_user_id]

    edited_message = update.edited_message
    edited_message_id = GetEditedMessageId(update, context)
    if not edited_message_id:  # If an edited message id was not found in the current chat
        return CHATTING

    input_media = None
    if edited_message.animation:
        input_media = InputMediaAnimation(media=edited_message.animation.file_id,
                                          caption=edited_message.caption,
                                          caption_entities=edited_message.caption_entities,
                                          has_spoiler=edited_message.has_media_spoiler)
    elif edited_message.audio:
        input_media = InputMediaAudio(media=edited_message.audio.file_id,
                                      caption=edited_message.caption,
                                      caption_entities=edited_message.caption_entities)
    elif edited_message.document:
        input_media = InputMediaDocument(media=edited_message.document.file_id,
                                         caption=edited_message.caption,
                                         caption_entities=edited_message.caption_entities)
    elif edited_message.photo:
        input_media = InputMediaPhoto(media=edited_message.photo[0].file_id,
                                      caption=edited_message.caption,
                                      caption_entities=edited_message.caption_entities,
                                      has_spoiler=edited_message.has_media_spoiler)
    elif edited_message.video:
        input_media = InputMediaVideo(media=edited_message.video.file_id,
                                      caption=edited_message.caption,
                                      caption_entities=edited_message.caption_entities,
                                      has_spoiler=edited_message.has_media_spoiler)
    else:
        return CHATTING

    await context.bot.edit_message_media(media=input_media,
                                         chat_id=other_user_id,
                                         message_id=edited_message_id,
                                         reply_markup=inline_keyboards['chatting']['edited_keyboard'])

    return CHATTING


async def ChattingEditedCaptionCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback function for caption-edited messages
    """
    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    this_user_id = update.effective_user.id
    if this_user_id not in bot_data['chatting_with']:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data['chatting_with'][this_user_id]

    edited_message = update.edited_message
    edited_message_id = GetEditedMessageId(update, context)

    if edited_message_id:  # If an edited message id was found in the current chat
        await context.bot.edit_message_caption(chat_id=other_user_id,
                                               message_id=edited_message_id,
                                               caption=edited_message.caption,
                                               caption_entities=edited_message.caption_entities,
                                               reply_markup=inline_keyboards['chatting']['edited_keyboard'])

    return CHATTING


async def ChattingEditedMessageButtonCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback function for edited_keyboard.
    This function tells the user that this message is edited
    """
    query = update.callback_query
    message_text = (
        "این پیام ویرایش شده است!"
    )
    await query.answer(text=message_text)

    return CHATTING


async def ErrorHandler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Error handler which tells the user to send their message again if the error was a timeout error.
    Otherwise, it logs the exception in the log file.
    """
    if not isinstance(update, Update):
        return

    logger.exception(f"Exception in error handler for user {update.effective_user.id}:", exc_info=context.error)

    if isinstance(context.error, error.TimedOut):
        await ReplyMessage(update,
                           text='مشکلی پیش آمد. لطفا دوباره پیام خود را بفرستید',
                           **{"write_timeout": 30, "connect_timeout": 30})


async def ChattingEndChatCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when the user sends /end_chat. To end the chat between two users
    """
    bot_data = context.bot_data
    if 'chatting_with' not in bot_data:
        bot_data['chatting_with'] = {}

    this_user_id = update.effective_user.id
    if this_user_id not in bot_data['chatting_with']:
        await SendMessage(update, context, text='شما در حال چت با کسی نیستید!')
        return END

    other_user_id = bot_data['chatting_with'][this_user_id]

    # Remove the user ids from chatting_filter
    chatting_filter.remove_chat_ids([this_user_id, other_user_id])
    # Save the chatting_filter in a pickle file
    with open('chatting_filter.pkl', 'wb') as file:
        pickle.dump(chatting_filter, file)

    # delete chatting_with and message_ids of the users
    del bot_data['chatting_with'][this_user_id]
    del bot_data['chatting_with'][other_user_id]

    del bot_data['message_ids'][this_user_id]
    del bot_data['message_ids'][other_user_id]

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
    await ReplyMessage(update,
                       text='یک گزینه را انتخاب کنید:',
                       reply_keyboard_markup=inline_keyboards['financial']['main_keyboard'])

    if not await CheckSubs(update, context):
        return END

    return FINANCIAL


async def FinancialBuyPlanCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when خرید پلن is clicked in the financial menu.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    plans = (
        "پلن های ماهانه:\n"
        "برنز: 15 الماس + 2 سکه = 32,000 تومان\n"
        "نقره: 30 الماس + 4 سکه = 58,000 تومان\n"
        "طلایی: 60 الماس + 8 سکه = 108,000 تومان\n"
    )
    await query.edit_message_text(text=plans,
                                  reply_markup=inline_keyboards['financial']['buy-plan'])

    return FINANCIAL


async def FinancialChangesCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when تبدیل is clicked in the financial menu.
    """
    if not await CheckSubs(update, context):
        return END

    query = update.callback_query
    await query.answer()

    message_text = (
        "یک گزینه را انتخاب کنید:"
    )
    await query.edit_message_text(text=message_text,
                                  reply_markup=inline_keyboards['financial']['changes_keyboard'])

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
                      reply_markup=inline_keyboards['financial']['main_keyboard'])

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
                      reply_markup=inline_keyboards['financial']['main_keyboard'])

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
                      reply_markup=inline_keyboards['financial']['main_keyboard'])

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
                      reply_markup=inline_keyboards['financial']['main_keyboard'])

    return FINANCIAL


async def FinancialReceiveMoneyCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when دریافت وجه is clicked in the financial keyboard.
    """
    # Read the data from the Web App
    web_app_data = json.loads(update.effective_message.web_app_data.data)

    selected_gifts = web_app_data['gifts']
    card_number = web_app_data['card_number']

    # TODO: Check for every gifts in the users' gifts in db and add their price to amount_to_pay
    amount_to_pay = 0
    for gift in selected_gifts:
        if gift == 'coffee':
            amount_to_pay += 23000
        elif gift == 'teddy-bear':
            amount_to_pay += 67000

    message_text = (
        "مبلغ دریافتی: "
        f"`{amount_to_pay}`\n"
        "شماره کارت: "
        f"`{card_number}`"
    )
    await ReplyMessage(update,
                       text=message_text,
                       reply_keyboard_markup=inline_keyboards['financial']['receive-money_confirm'],
                       **{'parse_mode': 'MarkdownV2'})

    return FINANCIAL_RECEIVE_MONEY


async def FinancialReceiveMoneyConfirmCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs after the user has confirmed their money amount and card number.
    This function sends the amount_to_pay and card_number variables to a table in the database.
    """
    query = update.callback_query
    message = query.message
    amount_to_pay = int(re.findall('مبلغ دریافتی:.+', message.text)[0].split()[-1])
    card_number = re.findall('شماره کارت:.+', message.text)[0].split()[-1]

    # Read the data from the replied Web App message
    web_app_data = json.loads(message.reply_to_message.web_app_data.data)
    selected_gifts = web_app_data['gifts']

    # TODO: Send amount_to_pay and card_number to db
    # TODO: Remove gifts from users_gifts table for the user

    await query.answer()

    message_sent_to_user = (
        "درخواست شما برای دریافت وجه با\n"
        "مبلغ دریافتی: "
        f"`{amount_to_pay}`\n"
        "شماره کارت: "
        f"`{card_number}`\n"
        "فرستاده شد\. منتظر جواب بمانید\."
    )
    await query.edit_message_text(text=message_sent_to_user,
                                  parse_mode='MarkdownV2')

    return FINANCIAL


async def FinancialChargeCallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Runs when شارژ سکه و الماس has been clicked and the user went to the web app for this button.
    The bot reads the gems and coins from web app and asks the user to pay.
    """
    if not await CheckSubs(update, context):
        return END

    # Read the data from the Web App
    web_app_data = json.loads(update.effective_message.web_app_data.data)

    number_of_coins, price = 0, 0

    if 'coins' in web_app_data:  # If the user didn't select a plan
        number_of_coins = web_app_data['coins']
        price = COINS_PRICE * int(number_of_coins)

    elif 'plan' in web_app_data:  # If the user has selected a plan
        number_of_coins = web_app_data['plan']['coins']
        price = web_app_data['plan']['price']

    text = (
        "شما "
        f"{number_of_coins} "
        "سکه انتخاب کردید. "
        "هزینه پرداختی: "
        f"{price}\n"
        "برای پرداخت روی گزینه پرداخت کلیک کنید."
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
