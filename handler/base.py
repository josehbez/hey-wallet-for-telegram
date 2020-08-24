import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
from  .sign import SignHandler
from  .hey_wallet import HeyWalletHandler

logger = logging.getLogger(__name__)

class BaseHandler:

    START, BACK, SIGNIN, SIGNUP, OWNSERVER, TYPING, HEY_WALLET = range(7)

    START_OVER_SIGNIN, BUTTON_SIGNIN = range(100, 102)

    END = ConversationHandler.END

    # SignHandler
    EMAIL, PASSWORD, UPDATE_EMAIL_PASSWORD, ADD_EMAIL_PASSWORD, TYPING_EMAIL_PASSWORD = map(chr, range(100, 105))

    def __init__(self):
        self.sign_handler = SignHandler(self)
        self.hey_wallet_handler = HeyWalletHandler(self)
        self.provider = False


    def handler(self):
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.START:[
                    CallbackQueryHandler(
                        self.action_start, 
                        pattern='^('+str(self.START_OVER_SIGNIN)+'|'+str(self.SIGNUP)+'|'+str(self.OWNSERVER)+')$'
                    )
                ],
                self.ADD_EMAIL_PASSWORD: [
                    CallbackQueryHandler(
                        self.sign_handler.ask_for_add_email_password,
                        pattern='^('+str(self.EMAIL)+'|'+str(self.PASSWORD)+')$'
                    ),
                    CallbackQueryHandler(
                        self.sign_handler.auth,
                        pattern='^('+str(self.BUTTON_SIGNIN)+')$'
                    )
                ],
                self.TYPING_EMAIL_PASSWORD: [
                    MessageHandler(
                        Filters.text & ~Filters.command, 
                        self.sign_handler.save_email_password
                    )
                ],
                self.HEY_WALLET: self.hey_wallet_handler.handler()
            },
            fallbacks=[
                #CallbackQueryHandler(self.action_back, pattern='^' + str(self.BACK) + '$'),
                CommandHandler('cancel', self.cancel)
            ],
        )
        return conv_handler

    def start(self, update, context):
        buttons = [[
            InlineKeyboardButton(text='Sign In',callback_data=str(self.START_OVER_SIGNIN)),
            #InlineKeyboardButton(text='Sing Up', callback_data=str(self.SIGNUP)),
            #InlineKeyboardButton(text='Own Server', callback_data=str(self.OWNSERVER))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        text = 'Hi! My name Hey Wallet Bot. \n\n' \
                'I am your personal finance planner, I will help you save money, ' \
                'plan your budget and track spending. You will become your own finance manager. \n\n' \
                'Are you ready? ... or Send /cancel to stop talking to me \n\n '
        
        if getattr(update.message, 'reply_text',False):
            update.message.reply_text(text=text,reply_markup=keyboard)
        elif getattr(update.callback_query, 'edit_message_text',False):
            update.callback_query.answer()        
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        return self.START

    def cancel(self, update, context):        
        update.message.reply_text(
            'Bye! I hope we can talk again someday ... or /start',
            reply_markup=ReplyKeyboardRemove())

        return self.END

    def action_start(self, update, context):
        action = update.callback_query.data
        go_state = self.END

        if action == str(self.START_OVER_SIGNIN):
            go_state = self.sign_handler.select_to_add_email_password(update, context)
        elif action == str(self.SIGNUP):
            pass#return self.SIGNUP
        elif action == str(self.OWNSERVER):
            pass#return self.OWNSERVER
        
        #update.callback_query.answer()
        #update.callback_query.edit_message_text(text='Please /start over')

        return go_state

    def action_back(self, update, context):
        """End gathering of features and return to parent conversation."""
        #ud = context.user_data
        #level = ud[CURRENT_LEVEL]
        #if not ud.get(level):
        #    ud[level] = []
        #ud[level].append(ud[FEATURES])
#
        ## Print upper level menu
        #if level == SELF:
        #    ud[START_OVER] = True
        #self.start(update, context)
        #else:
        #    select_level(update, context)

        return self.END


    def msg_post(self, update, context,  **args):
        if getattr(update.message, 'reply_text',False):
            update.message.reply_text(**args)
        elif getattr(update.callback_query, 'edit_message_text',False):
            update.callback_query.answer()
            update.callback_query.edit_message_text(**args)