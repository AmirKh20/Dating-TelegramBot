# TODO: Add Concurrency to some handlers or their callback functions

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from callbacks import *

not_edited_messages_filter = ~filters.UpdateType.EDITED_MESSAGE

# Command Handlers that runs the callback function when ever /command is sent
commands = {
    'Main-Menu': CommandHandler('main_menu', MainMenuCallback, filters=not_edited_messages_filter),

    'Help': CommandHandler('help', HelpCallback, filters=not_edited_messages_filter),

    'Start': CommandHandler('start', StartCallback, filters=not_edited_messages_filter),
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
    }
}

# Conversation handlers that modify the workflow of the bot
conversations = {
    # This handler starts when همسان گزینی is sent in the parent conversation handler.
    # The user clicks on a province after it.
    'Hamsan-Gozini': ConversationHandler(
        entry_points=[messages['Hamsan-Gozini']],
        states={
            PROVINCES: [CallbackQueryHandler(HamsanGoziniProvincesCallback,
                                             pattern=lambda data: data in GetProvinceNames())],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start']],
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
