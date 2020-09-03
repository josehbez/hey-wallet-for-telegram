import logging
import re
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )

logger = logging.getLogger(__name__)
from utils import Session

class SignHandler:

    def __init__(self, base_handler):
        self.base_handler = base_handler
    
    def workflow_connector(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Sign In' , callback_data=self.base_handler.CALLBACK_AUTH),
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)       

        text = "Try bot workflow"
        self.base_handler.reply_text(update, context, text=text, reply_markup=keyboard)
        return self.base_handler.SH_STATE_ASK_FOR
    
    def auth(self, update, context):     
        session = Session.get_from(context.user_data)
        if session.sign_handler and self.__class__.__name__ == 'SignHandler':
            return session.sign_handler.auth(update, context)
            
        return self.base_handler.hey_wallet_handler.welcome(update, context)

    def ask_for(self,update, context):
        session = Session.get_from(context.user_data)
        if session.sign_handler and self.__class__.__name__ == 'SignHandler':
            return session.sign_handler.ask_for(update, context)
        else:
            data = update.callback_query.data
            self.base_handler.set_data(update, context,
                self.base_handler.SIGNIN_ASK_FOR,
                data
            )
            text = 'Okay, tell me your {}'.format( data)
            self.base_handler.reply_text(update, context, text=text)
        return self.base_handler.STATE_TYPING_SIGNIN
    
    def save_typing(self, update, context):
        session = Session.get_from(context.user_data)
        if session.sign_handler and self.__class__.__name__ == 'SignHandler':
            return session.sign_handler.save_typing(update, context)
        else:
            sign_ask_for = self.base_handler.get_data(update, context, self.base_handler.SIGNIN_ASK_FOR, None)
            self.base_handler.set_data(update, context,
                sign_ask_for,
                update.message.text
            )
        return self.workflow_connector(update, context)
    