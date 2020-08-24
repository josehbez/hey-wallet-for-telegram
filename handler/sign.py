import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
from providers.maxsbiz import MSBHeyWallet

logger = logging.getLogger(__name__)

class SignHandler:

    def __init__(self, base_handler):
        self.base_handler = base_handler

    def select_to_add_email_password(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Add email' , callback_data=str(self.base_handler.EMAIL)),
                InlineKeyboardButton(text='Add password', callback_data=str(self.base_handler.PASSWORD))
            ], 
            [
                InlineKeyboardButton(text='Sign In ', callback_data=str(self.base_handler.BUTTON_SIGNIN))
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        if getattr(update.callback_query, 'edit_message_text',False):
            update.callback_query.answer()
            text = 'Please choose, ... or /cancel'
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        elif getattr(update.message, 'reply_text',False):
            text = 'Got it! Please select to update.'
            update.message.reply_text(text=text, reply_markup=keyboard)
        return self.base_handler.ADD_EMAIL_PASSWORD

    def ask_for_add_email_password(self, update, context):        
        ep = str(update.callback_query.data)        
        context.user_data[self.base_handler.UPDATE_EMAIL_PASSWORD] = ep            
        if ep == str(self.base_handler.EMAIL):
            ep_kind = "email"
        else:
            ep_kind = "password"
        text = 'Okay, tell me your {}'.format(ep_kind)
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.base_handler.TYPING_EMAIL_PASSWORD
        
        
    
    def auth(self, update, context):        
        ep = str(update.callback_query.data)
        ud = context.user_data
        ud[self.base_handler.EMAIL] = 'admin' # TODO: Comment
        ud[self.base_handler.PASSWORD] = 'admin' # TODO: Comment
        if ud.get(self.base_handler.EMAIL) and ud.get(self.base_handler.PASSWORD):
            provider = MSBHeyWallet()
            provider.auth(
                ud.get(self.base_handler.EMAIL),
                ud.get(self.base_handler.PASSWORD),
                '013c-jh',
                'http://localhost:8068'
            )
            if provider.is_auth():
                self.base_handler.provider = provider                    
                logger.info(" To return  HEY_WALLET")
                #update.callback_query.edit_message_text(text="Welcome")
                self.base_handler.hey_wallet_handler.welcome(update, context)
                return self.base_handler.HEY_WALLET
            else:
                text = 'Fail auth, update your email or password'
                update.callback_query.edit_message_text(text=text)
                return self.select_to_add_email_password(update, context)    
        
        text = 'First  add  your  email and password '
        update.callback_query.edit_message_text(text=text)
        return self.select_to_add_email_password(update, context)

        


    def save_email_password(self, update, context):
        ud = context.user_data
        if ud[self.base_handler.UPDATE_EMAIL_PASSWORD] == str(self.base_handler.EMAIL):
            ud[self.base_handler.EMAIL] = update.message.text
        elif ud[self.base_handler.UPDATE_EMAIL_PASSWORD]== str(self.base_handler.PASSWORD):
            ud[self.base_handler.PASSWORD] = update.message.text
        return self.select_to_add_email_password(update, context)
    