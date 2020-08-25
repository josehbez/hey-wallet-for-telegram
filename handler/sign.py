import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
logger = logging.getLogger(__name__)
from utils.session import Session

class SignHandler:

    def __init__(self, base_handler):
        self.base_handler = base_handler

    def workflow_signin(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Add username' , callback_data=str(self.base_handler.CALLBACK_USERNAME)),
                InlineKeyboardButton(text='Add password', callback_data=str(self.base_handler.CALLBACK_PASSWORD))
            ], 
            [
                InlineKeyboardButton(text='Sign In ', callback_data=str(self.base_handler.CALLBACK_AUTH))
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)        
        text = self.base_handler.get_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG,
            'Please choose')  + ' ... or /cancel'
        
        self.base_handler.del_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG
        )
        self.base_handler.reply_text(update, context, text=text, reply_markup=keyboard)
        return self.base_handler.STATE_SIGNIN

    def ask_for_username(self,update, context):
        self.base_handler.set_data(update, context,
            self.base_handler.SIGNIN_ASK_FOR,
            self.base_handler.CALLBACK_USERNAME
        )
        text = '👾 Okay, tell me your  username'
        self.base_handler.reply_text(update, context, text=text)
        return self.base_handler.STATE_TYPING_SIGNIN

    def ask_for_password(self, update, context):
        self.base_handler.set_data(update, context,
            self.base_handler.SIGNIN_ASK_FOR,
            self.base_handler.CALLBACK_PASSWORD
        )
        text = '🔑 Okay, tell me your  password'
        self.base_handler.reply_text(update, context, text=text)
        return self.base_handler.STATE_TYPING_SIGNIN
    
    def auth(self, update, context):     
        session = Session.get_from(context.user_data)      
        text = 'First  add  your  username and password '
        if session.get_auth_args('password',  False) and session.get_auth_args('username', False):
            session.datasource.auth(**session.auth_args)
            if session.datasource.is_auth():                
                self.base_handler.hey_wallet_handler.welcome(update, context)
                return self.base_handler.STATE_HEY_WALLET
            else:
                text = 'Fail auth, update your username or password'

        self.base_handler.set_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG,
            value=text
        )
        return self.workflow_signin(update, context)

    def save_typing_signin(self, update, context):
        sign_ask_for = self.base_handler.get_data(update, context, self.base_handler.SIGNIN_ASK_FOR, None)
        session = Session.get_from(context.user_data)
        session_update = False
        if sign_ask_for and sign_ask_for == self.base_handler.CALLBACK_USERNAME:
            session.set_auth_args(username= update.message.text)
            session_update = True
        elif sign_ask_for and sign_ask_for == self.base_handler.CALLBACK_PASSWORD:
            session.set_auth_args(password = update.message.text)
            session_update = True
        Session.set_from(context.user_data, session)
        self.base_handler.set_data(update, context, 
            self.base_handler.SIGN_HANDLER_MSG,
            'Got it! Please select to update.'
        )
        return self.workflow_signin(update, context)
    