import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
from  sign_handler import SignHandler

logger = logging.getLogger(__name__)

class HeyWallet:

    START, SIGNIN, SIGNUP, OWNSERVER, TYPING = range(5)

    END = ConversationHandler.END

    # SignHandler
    EMAIL, PASSWORD, UPDATE_EMAIL_PASSWORD, ADD_EMAIL_PASSWORD, TYPING_EMAIL_PASSWORD = map(chr, range(100, 105))

    def __init__(self):
        self.sign_handler = SignHandler(self)


    def handler(self):
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.START:[
                    CallbackQueryHandler(
                        self.action_start, 
                        pattern='^('+str(self.SIGNIN)+'|'+str(self.SIGNUP)+'|'+str(self.OWNSERVER)+')$'
                    )
                ],
                self.ADD_EMAIL_PASSWORD: [
                    CallbackQueryHandler(
                        self.sign_handler.ask_for_add_email_password,
                        pattern='^('+str(self.EMAIL)+'|'+str(self.PASSWORD)+')$'
                    )
                ],
                self.TYPING_EMAIL_PASSWORD: [
                    MessageHandler(
                        Filters.text & ~Filters.command, 
                        self.sign_handler.save_email_password)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        return conv_handler

    def start(self, update, context):
        buttons = [[
            InlineKeyboardButton(text='Sign In',callback_data=str(self.SIGNIN)),
            InlineKeyboardButton(text='Sing Up', callback_data=str(self.SIGNUP)),
            InlineKeyboardButton(text='Own Server', callback_data=str(self.OWNSERVER))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        update.message.reply_text(
            'Hi! My name Hey Wallet Bot. \n\n'
            'I am your personal finance planner, I will help you save money, '
            'plan your budget and track spending. You will become your own finance manager. \n\n'
            'Are you ready? ... or Send /cancel to stop talking to me \n\n ',
            reply_markup=keyboard)
        return self.START

    def cancel(self, update, context):        
        update.message.reply_text(
            'Bye! I hope we can talk again someday.',
            reply_markup=ReplyKeyboardRemove())

        return self.END

    def action_start(self, update, context):
        action = update.callback_query.data

        logger.info("Action: {}  ".format(action))
        go_state = self.END
        if action == str(self.SIGNIN):
            go_state = self.sign_handler.select_to_add_email_password(update, context)
        elif action == str(self.SIGNUP):
            pass#return self.SIGNUP
        elif action == str(self.OWNSERVER):
            pass#return self.OWNSERVER
        
        #update.callback_query.answer()
        #update.callback_query.edit_message_text(text='Please /start over')

        return go_state

