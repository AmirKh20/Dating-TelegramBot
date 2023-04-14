from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from callbacks import *

# Command Handlers that runs the callback function when ever /command is sent
commands = {
    'Main-Menu': CommandHandler('main_menu', MainMenuCallback),
    'Help': CommandHandler('help', HelpCallback),
    'Start': CommandHandler('start', StartCallback),
}

# Message handlers that run the callback function when ever the message contains the filters
messages = {
    'Consultation': {
        'Menu': MessageHandler(filters.Regex('^مشاوره$'), ConsultationCallback),
        'Therapist': MessageHandler(filters.Regex('^روانشناس$'), TherapistCallback),
    },
    'Main-Menu': MessageHandler(filters.Regex('^بازگشت به منوی اصلی$'), MainMenuCallback)
}

# Conversation handlers that modify the workflow of the bot
conversations = {
    # This handler starts when `Start` or `Main-Manu` handlers is run, and it goes to different states
    'Starting': ConversationHandler(
        entry_points=[commands['Start'], commands['Main-Menu']],
        states={
            MAIN_MENU_STATE: [messages['Consultation']['Menu']],
            CONSULTATION_STATE: [messages['Consultation']['Therapist']],
        },
        fallbacks=[messages['Main-Menu'], commands['Main-Menu']]
    )
}
