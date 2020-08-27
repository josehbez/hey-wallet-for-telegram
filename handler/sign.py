import logging
import re
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
    
    def workflow_connect(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Odoo' , callback_data=self.base_handler.CALLBACK_ODOO_CONNECTOR),
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)        
        text = self.base_handler.get_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG,
            'Connect with')  + ' ... or /cancel'
        
        self.base_handler.del_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG
        )
        self.base_handler.reply_text(update, context, text=text, reply_markup=keyboard)
        return self.base_handler.STATE_WORKFLOW_CONNECTOR

    def workflow_odoo_connector(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='URL' , callback_data='sign_ask_for_odoo_connector_url'),
                InlineKeyboardButton(text='DB' , callback_data='sign_ask_for_odoo_connector_db'),
            ],[
                InlineKeyboardButton(text='Sign In',callback_data=self.base_handler.CALLBACK_SIGNIN),
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        self.base_handler.reply_text(update, context, text="Please choose", reply_markup=keyboard)
        return self.base_handler.SH_STATE_ASK_FOR
    
    def ask_for(self,update, context):
        data = update.callback_query.data
        self.base_handler.set_data(update, context,
            self.base_handler.SIGNIN_ASK_FOR,
            data
        )        
        if data == 'sign_ask_for_odoo_connector_url':
            data = 'Odoo URL'
        elif data == 'sign_ask_for_odoo_connector_db':
            data = 'Odoo database'
        elif data == 'sign_ask_for_username':
            data = 'username 👾'
        elif data == 'sign_ask_for_password':
            data = 'password 🔑'
        
        text = 'Okay, tell me your {}'.format( data)
        self.base_handler.reply_text(update, context, text=text)

        return self.base_handler.STATE_TYPING_SIGNIN



    def workflow_signin(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Add username' , callback_data='sign_ask_for_username'),
                InlineKeyboardButton(text='Add password', callback_data='sign_ask_for_password')
            ], 
            [
                InlineKeyboardButton(text='Sign In ', callback_data=self.base_handler.CALLBACK_AUTH)
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

        return self.base_handler.SH_STATE_ASK_FOR
    
    def auth(self, update, context):     
        session = Session.get_from(context.user_data)      
        text = 'First  add  your  username and password '
        if session.get_auth_args('password', True) and session.get_auth_args('username', True):
            try:
                session.datasource.auth(**session.auth_args)
                if session.datasource.is_auth():                
                    self.base_handler.hey_wallet_handler.welcome(update, context)
                    return self.base_handler.STATE_HEY_WALLET
                else:
                    text = 'Fail auth, update your username or password'
            except Exception as e:
                text = 'Fail auth, update your username or password'
                if getattr(session.datasource, 'auth_exception'):
                    text= session.datasource.auth_exception(e) or text
                logger.error(str(e))

        self.base_handler.set_data(
            update, context,
            self.base_handler.SIGN_HANDLER_MSG,
            value=text
        )
        return self.workflow_signin(update, context)

    def save_typing(self, update, context):
        sign_ask_for = self.base_handler.get_data(update, context, self.base_handler.SIGNIN_ASK_FOR, None)
        if not sign_ask_for:
            return
        
        session = Session.get_from(context.user_data)

        go_to = None
        if re.search('odoo_connector_url$', sign_ask_for):
            session.set_auth_args(url= update.message.text)
            go_to = self.workflow_odoo_connector(update, context)
        elif re.search('odoo_connector_db$', sign_ask_for):
            session.set_auth_args(database= update.message.text)
            go_to = self.workflow_odoo_connector(update, context)
        elif re.search('username$', sign_ask_for):
            session.set_auth_args(username= update.message.text)
        
    
        elif re.search('password$', sign_ask_for):
            session.set_auth_args(password = update.message.text)
        
        Session.set_from(context.user_data, session)

        #self.base_handler.set_data(update, context, 
        #    self.base_handler.SIGN_HANDLER_MSG,
        #    'Got it! Please select to update.'
        #)

        return go_to or self.workflow_signin(update, context)
    