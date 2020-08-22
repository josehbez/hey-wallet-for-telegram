import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )

logger = logging.getLogger(__name__)

class SignHandler:

    def __init__(self, hey_wallet):
        self.hey_wallet = hey_wallet

    def select_to_add_email_password(self, update, context):
        buttons = [
            [
                InlineKeyboardButton(text='Email' , callback_data=str(self.hey_wallet.EMAIL)),
                InlineKeyboardButton(text='Password', callback_data=str(self.hey_wallet.PASSWORD))
            ], 
            [
                InlineKeyboardButton(text='Back', callback_data=str(self.hey_wallet.END))
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        if not context.user_data.get(self.hey_wallet.UPDATE_EMAIL_PASSWORD):
            update.callback_query.answer()
            text = 'Please add your ...'
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        else:
                text = 'Got it! Please select to update.'
                update.message.reply_text(text=text, reply_markup=keyboard)
        return self.hey_wallet.ADD_EMAIL_PASSWORD

    def ask_for_add_email_password(self, update, context):
        #context.user_data[CURRENT_FEATURE] = update.callback_query.data
        ep = str(update.callback_query.data)
        ep_kind = "password"
        if ep == str(self.hey_wallet.EMAIL):
            ep_kind = "email"

        text = 'Okay, tell me your {}'.format(ep_kind)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.hey_wallet.TYPING_EMAIL_PASSWORD
    
    def save_email_password(self, update, context):        
        ud = context.user_data
        ud[self.hey_wallet.UPDATE_EMAIL_PASSWORD] = True
        #ud[FEATURES][ud[CURRENT_FEATURE]] = update.message.text

        #ud[START_OVER] = True
        logger.info("Save " +update.message.text)
        return self.select_to_add_email_password(update, context)

    