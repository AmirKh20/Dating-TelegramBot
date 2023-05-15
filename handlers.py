# TODO: Add Concurrency to some handlers or their callback functions

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler
)

from callbacks import *

not_edited_messages_filter = ~filters.UpdateType.EDITED_MESSAGE

# Command Handlers that runs the callback function when ever /command is sent
commands = {
    'Main-Menu': CommandHandler('main_menu', MainMenuCallback, filters=not_edited_messages_filter & ~chatting_filter),

    'Help': CommandHandler('help', HelpCallback, filters=not_edited_messages_filter),

    'Start': CommandHandler('start', StartCallback, filters=not_edited_messages_filter),

    'End-Chat': CommandHandler('end_chat', ChattingEndChatCallback, filters=chatting_filter)
}

# Message handlers that run the callback function when ever the message contains the filters
messages = {
    'Main-Menu': MessageHandler(filters.Regex('^بازگشت به منوی اصلی$'), MainMenuCallback),

    'Consultation': {
        'Menu': MessageHandler(filters.Regex('^مشاوره$'), ConsultationEntryCallback),
        'Therapist': MessageHandler(filters.Regex('^روانشناس$'), ConsultationTherapistCallback),
        'QA': {
            'Menu': MessageHandler(filters.Regex('^پرسش و پاسخ$'), ConsultationQACallback),

            # Every text message that is replied to the bots' message in the bot.
            'Enter-Question': MessageHandler(filters.TEXT & filters.REPLY & ~filters.COMMAND,
                                             ConsultationQAEnterQuestionCallback),
        }
    },

    'Hamsan-Gozini': MessageHandler(filters.Regex('^همسان گزینی$'), HamsanGoziniEntryCallback),

    'Profile': MessageHandler(filters.Regex('^پروفایل$'), ProfileEntryCallback),

    'Financial': {
        'Menu': MessageHandler(filters.Regex('^مالی$'), FinancialEntryCallback),
        'Buy-Plan': MessageHandler(filters.Regex('^خرید پلن$'), FinancialBuyPlanCallback),
        'Balance': MessageHandler(filters.Regex('^موجودی$'), FinancialBalanceCallback),
        'Changes': {
            'Menu': MessageHandler(filters.Regex('^تبدیل$'), FinancialChangesCallback),
            'Gems-To-Coins': MessageHandler(filters.Regex('^\d+$') & filters.REPLY & ~filters.COMMAND,
                                            FinancialChangesGemsToCoinsReadGemsCallback),
            'Coins-To-Gems': MessageHandler(filters.Regex('^\d+$') & filters.REPLY & ~filters.COMMAND,
                                            FinancialChangesCoinsToGemsReadCoinsCallback),
            'Gifts-To-Coins': MessageHandler(filters.Regex('^\d+$') & filters.REPLY & ~filters.COMMAND,
                                             FinancialChangesGiftsToCoinsReadGiftsCallback),
            'Gifts-To-Gems': MessageHandler(filters.Regex('^\d+$') & filters.REPLY & ~filters.COMMAND,
                                            FinancialChangesGiftsToGemsReadGiftsCallback)
        },
        'Receive-Money': {
            'Menu': MessageHandler(filters.Regex('^دریافت وجه$'), FinancialReceiveMoneyCallback),

            # Every text message that is replied to the bots' message in the bot.
            'Enter-Card': MessageHandler(filters.TEXT & filters.REPLY & ~filters.COMMAND,
                                         FinancialReceiveMoneyEnterCardCallback)
        },
        # Web app handler for charging coins and gems
        'Charge': MessageHandler(filters.StatusUpdate.WEB_APP_DATA,
                                 FinancialChargeCallback),
    },

    'Down-Line': MessageHandler(filters.Regex('^زیر مجموعه گیری$'), DownLineCallback),

    'Support': {
        'Main': MessageHandler(filters.Regex('^پشتیبانی$'), SupportEntryCallback),

        # Every text message that is replied to the bots' message in the bot.
        'Enter-Ticket': MessageHandler(filters.TEXT & filters.REPLY & ~filters.COMMAND,
                                       SupportEnterTicketCallback),

        # Every text message that is replied to the bots' message in the Support Group.
        'Answer-Ticket': MessageHandler(filters.TEXT & filters.REPLY
                                        & ~filters.COMMAND & filters.Chat(chat_id=SUPPORT_GROUP_ID),
                                        SupportAnswerTicketCallback)
    },

    'User-Profile': {
        'Chat-Requests': {
            'Given': MessageHandler(filters.ViaBot(username=BOT_USERNAME) & filters.Regex('^درخواست داده به:'),
                                    callback=ChatRequestsGivenMenuCallback),
            'Gotten': MessageHandler(filters.ViaBot(username=BOT_USERNAME) & filters.Regex('^درخواست گرفته از:'),
                                     callback=ChatRequestsGottenMenuCallback)
        }
    },

    'Chatting': {
        'Entry-Text': MessageHandler(filters.TEXT & chatting_filter &
                                     filters.ChatType.PRIVATE & ~filters.Regex('^/end_chat$'),
                                     callback=ChattingCallback),

        'Entry-Document': MessageHandler(filters.Document.ALL & chatting_filter &
                                         filters.ChatType.PRIVATE,
                                         callback=ChattingDocumentCallback),

        'Entry-Audio': MessageHandler(filters.AUDIO & chatting_filter &
                                      filters.ChatType.PRIVATE,
                                      callback=ChattingAudioCallback),

        'Entry-Sticker': MessageHandler(filters.Sticker.ALL & chatting_filter &
                                        filters.ChatType.PRIVATE,
                                        callback=ChattingStickerCallback),

        'Text': MessageHandler(filters.TEXT & ~filters.Regex('^/end_chat$|^/main_menu$'),
                               callback=ChattingCallback),

        'Document': MessageHandler(filters.Document.ALL,
                                   callback=ChattingDocumentCallback),

        'Audio': MessageHandler(filters.AUDIO,
                                callback=ChattingAudioCallback),

        'Sticker': MessageHandler(filters.Sticker.ALL,
                                  callback=ChattingStickerCallback)
    }
}

# Conversation handlers that modify the workflow of the bot
conversations = {
    # This handler starts when همسان گزینی is sent in the parent conversation handler.
    # The user clicks on a province after it.
    'Hamsan-Gozini': ConversationHandler(
        entry_points=[messages['Hamsan-Gozini']],
        states={
            HAMSAN_GOZINI_MENU: [CallbackQueryHandler(pattern='^chat_requests_list$',
                                                      callback=HamsanGoziniChatRequestsListCallback)],
            HAMSAN_GOZINI_CHAT_REQUESTS: [CallbackQueryHandler(pattern='^back$',
                                                               callback=HamsanGoziniGoBackMenu)]
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start'],
                   messages['Hamsan-Gozini']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        },
        persistent=True,
        name='hamsan-gozini_conversation'
    ),

    # Conversation handler for پروفایل button
    'Profile': ConversationHandler(
        entry_points=[messages['Profile']],
        states={
            PROFILE: [
                CallbackQueryHandler(ProfileEditCallback, pattern='^profile_edit$'),
                CallbackQueryHandler(ProfileContactsCallback, pattern='^contacts$'),
                CallbackQueryHandler(ProfileLikersCallback, pattern='^likers$'),
                CallbackQueryHandler(ProfileBlocksCallback, pattern='^blocks$'),
                CallbackQueryHandler(ProfileNumberOfLikesOnOff, pattern='^on_off_number_likes$')
            ],
            PROFILE_CONTACTS: [
                CallbackQueryHandler(BackToProfileCallback, pattern='^back_to_profile$'),
            ],
            PROFILE_LIKERS: [
                CallbackQueryHandler(BackToProfileCallback, pattern='^back_to_profile$'),
            ],
            PROFILE_BLOCKS: [
                CallbackQueryHandler(BackToProfileCallback, pattern='^back_to_profile$'),
            ],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start'],
                   messages['Profile']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        },
        persistent=True,
        name='profile_conversation'
    ),

    # Conversation handler for مالی button
    'Financial': ConversationHandler(
        entry_points=[messages['Financial']['Menu']],
        states={
            FINANCIAL: [messages['Financial']['Buy-Plan'],
                        messages['Financial']['Balance'],
                        messages['Financial']['Changes']['Menu'],
                        messages['Financial']['Receive-Money']['Menu'],
                        messages['Financial']['Charge']],

            FINANCIAL_CHANGES: [CallbackQueryHandler(pattern='^gems_to_coins$',
                                                     callback=FinancialChangesGemsToCoinsCallback),
                                CallbackQueryHandler(pattern='^coins_to_gems$',
                                                     callback=FinancialChangesCoinsToGemsCallback),
                                CallbackQueryHandler(pattern='^gifts_to_coins$',
                                                     callback=FinancialChangesGiftsToCoinsCallback),
                                CallbackQueryHandler(pattern='^gifts_to_gems$',
                                                     callback=FinancialChangesGiftsToGemsCallback)],

            FINANCIAL_CHANGES_GEMS_TO_COINS: [messages['Financial']['Changes']['Gems-To-Coins']],
            FINANCIAL_CHANGES_COINS_TO_GEMS: [messages['Financial']['Changes']['Coins-To-Gems']],
            FINANCIAL_CHANGES_GIFTS_TO_COINS: [messages['Financial']['Changes']['Gifts-To-Coins']],
            FINANCIAL_CHANGES_GIFTS_TO_GEMS: [messages['Financial']['Changes']['Gifts-To-Gems']],

            FINANCIAL_RECEIVE_MONEY: [CallbackQueryHandler(pattern='^receive-money$',
                                                           callback=FinancialReceiveMoneyCallbackQuery)],

            FINANCIAL_RECEIVE_MONEY_ENTER_CARD: [messages['Financial']['Receive-Money']['Enter-Card']],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start'],
                   messages['Main-Menu'],
                   messages['Financial']['Menu'],
                   messages['Financial']['Buy-Plan'],
                   messages['Financial']['Balance'],
                   messages['Financial']['Changes']['Menu'],
                   messages['Financial']['Receive-Money']['Menu'],
                   messages['Financial']['Charge']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        },
        persistent=True,
        name='financial_conversation'
    ),

    # Conversation handler for مشاوره button.
    'Consultation': ConversationHandler(
        entry_points=[messages['Consultation']['Menu']],
        states={
            CONSULTATION: [messages['Consultation']['Therapist'],
                           messages['Consultation']['QA']['Menu']],

            CONSULTATION_QA: [messages['Consultation']['QA']['Enter-Question']],

            CONSULTATION_QA_ENTER_QUESTION: [CallbackQueryHandler(pattern='^send_question$',
                                                                  callback=ConsultationQASendQuestionCallback),
                                             CallbackQueryHandler(pattern='^dont_send_question$',
                                                                  callback=ConsultationQADontSendQuestionCallback)],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start'],
                   messages['Main-Menu'],
                   ],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        },
        persistent=True,
        name='consultation_conversation'
    ),

    # Conversation handler for پشتیبانی button.
    'Support': ConversationHandler(
        entry_points=[messages['Support']['Main']],
        states={
            SUPPORT: [messages['Support']['Enter-Ticket']],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        },
        persistent=True,
        name='support_conversation'
    ),

    'Chat-Requests': {
        'Given': ConversationHandler(
            entry_points=[messages['User-Profile']['Chat-Requests']['Given']],
            states={
                CHAT_REQUESTS_GIVEN: [
                    CallbackQueryHandler(pattern='^show_given_user_profile$',
                                         callback=ChatRequestsGivenShowProfileCallback)
                ],

                CHAT_REQUESTS_GIVEN_PROFILE: [
                    CallbackQueryHandler(pattern='^back_to_given_menu$',
                                         callback=ChatRequestsGivenProfileGoBackCallback)
                ],
            },
            fallbacks=[commands['Main-Menu'],
                       messages['User-Profile']['Chat-Requests']['Given']],
            persistent=True,
            name='chat_requests_given_conversation'
        ),

        'Gotten': ConversationHandler(
            entry_points=[messages['User-Profile']['Chat-Requests']['Gotten']],
            states={
                CHAT_REQUESTS_GOTTEN: [
                    CallbackQueryHandler(pattern='^accept_chat_request$',
                                         callback=ChatRequestsGottenAcceptRequestCallback),
                    CallbackQueryHandler(pattern='^reject_chat_request$',
                                         callback=ChatRequestsGottenRejectRequestCallback),
                    CallbackQueryHandler(pattern='^show_gotten_user_profile$',
                                         callback=ChatRequestsGottenShowProfileCallback)
                ],

                CHAT_REQUESTS_GOTTEN_PROFILE: [
                    CallbackQueryHandler(pattern='^back_to_gotten_menu$',
                                         callback=ChatRequestsGottenProfileGoBackCallback)
                ]
            },
            fallbacks=[commands['Main-Menu'],
                       messages['User-Profile']['Chat-Requests']['Gotten']],
            persistent=True,
            name='chat_requests_gotten_conversation'
        ),
    },

    'Chatting': ConversationHandler(
        entry_points=[messages['Chatting']['Entry-Text'],
                      messages['Chatting']['Entry-Document'],
                      messages['Chatting']['Entry-Audio'],
                      messages['Chatting']['Entry-Sticker'],
                      commands['End-Chat']],
        states={
            CHATTING: [messages['Chatting']['Text'],
                       messages['Chatting']['Document'],
                       messages['Chatting']['Audio'],
                       messages['Chatting']['Sticker']]
        },
        fallbacks=[commands['End-Chat'],
                   commands['Main-Menu']],
    )
}

# This handler starts when `Start` or `Main-Manu` handlers is run, and it goes to different states
conversations['Starting'] = ConversationHandler(
    entry_points=[commands['Start'],
                  commands['Main-Menu']],
    states={
        MAIN_MENU_STATE: [conversations['Hamsan-Gozini'],
                          conversations['Profile'],
                          conversations['Financial'],
                          conversations['Consultation'],
                          messages['Down-Line'],
                          conversations['Support']],

    },
    fallbacks=[messages['Main-Menu'],
               commands['Main-Menu']],
    persistent=True,
    name='start_conversation'
)

# Accept Question handler. This handler only works in the QA Group.
accept_question_query_handler = CallbackQueryHandler(pattern='^accept_question$',
                                                     callback=ConsultationQAAcceptQuestionCallback)

# Reject Question handler. This handler only works in the QA Group.
reject_question_query_handler = CallbackQueryHandler(pattern='^reject_question$',
                                                     callback=ConsultationQARejectQuestionCallback)

given_list_inline_query_handler = InlineQueryHandler(pattern='^درخواست های داده شده:.*$',
                                                     callback=HamsanGoziniChatRequestsGivenListCallback)

gotten_list_inline_query_handler = InlineQueryHandler(pattern='^درخواست های گرفته شده:.*$',
                                                      callback=HamsanGoziniChatRequestsGottenListCallback)
