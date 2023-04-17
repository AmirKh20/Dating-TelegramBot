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
        'Menu': MessageHandler(filters.Regex('^مشاوره$'), ConsultationCallback),
        'Therapist': MessageHandler(filters.Regex('^روانشناس$'), TherapistCallback),
    },
    'Hamsan-Gozini': MessageHandler(filters.Regex('^همسان گزینی$'), HamsanGoziniEntryCallback),
    'Profile': MessageHandler(filters.Regex('^پروفایل$'), ProfileEntryCallback),
}

# Conversation handlers that modify the workflow of the bot
conversations = {
    # This handler starts when همسان گزینی is sent in the parent conversation handler.
    # The user clicks on a province after it.
    'Hamsan-Gozini': ConversationHandler(
        entry_points=[messages['Hamsan-Gozini']],
        states={
            PROVINCES: [CallbackQueryHandler(HamsanGoziniProvincesCallback)],
        },
        fallbacks=[commands['Main-Menu'],
                   commands['Start']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        }
    ),

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
                   commands['Start']],
        map_to_parent={
            MAIN_MENU_STATE: MAIN_MENU_STATE,
            END: END,
        }
    )
}

# This handler starts when `Start` or `Main-Manu` handlers is run, and it goes to different states
conversations['Starting'] = ConversationHandler(
    entry_points=[commands['Start'],
                  commands['Main-Menu']],
    states={
        MAIN_MENU_STATE: [messages['Consultation']['Menu'],
                          conversations['Hamsan-Gozini'],
                          conversations['Profile']],
        CONSULTATION_STATE: [messages['Consultation']['Therapist']],
    },
    fallbacks=[messages['Main-Menu'],
               commands['Main-Menu']]
)
