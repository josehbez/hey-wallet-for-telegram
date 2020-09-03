import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
from  handler.sign import SignHandler
from  handler.hey_wallet import HeyWalletHandler
from utils import Session, Log
from datasource.odoo import OdooSignHandler, OdooHeyWalletHandler, Odoo                          


logger = logging.getLogger(__name__)

class BaseHandler:

    STATE_START, BACK, SIGNIN, SIGNUP, OWNSERVER, TYPING, STATE_HEY_WALLET, STATE_LOGOUT = range(8)

    CALLBACK_SIGNIN, CALLBACK_AUTH , CALLBACK_CONNECT, STATE_WORKFLOW_CONNECTOR, \
    CALLBACK_ODOO_CONNECTOR, STATE_WORKFLOW_ODOO_CONNECTOR, CALLBACK_TRY_CONNECTOR = range(100, 107)

    END = ConversationHandler.END

    # SignHandler
    CALLBACK_USERNAME, CALLBACK_PASSWORD, SIGNIN_ASK_FOR,\
    STATE_SIGNIN, STATE_TYPING_SIGNIN, SIGN_HANDLER_MSG,\
    SH_STATE_ASK_FOR = map(chr, range(100, 107))

    # HeyWalletHandler - prefix HWH_{name}
    HWH_ASK_FOR, HWH_STATE_TYPING, HWH_INCOME, HWH_EXPENSE, HWH_AMOUNT, HWH_OPERATION, \
    HWH_PRODUCT_ID, HWH_PRODUCT_NAME, HWH_ACCOUNT_ID, HWH_ACCOUNT_NAME, HWH_DESCRIPTION= range(3000, 3011)

    def __init__(self):
        self.sign_handler = SignHandler(self)
        self.hey_wallet_handler = HeyWalletHandler(self)
        self.provider = False
        #self.session = Session()

    def handler(self):
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.STATE_WORKFLOW_CONNECTOR: [
                    CallbackQueryHandler(
                        self.workflow_connector,
                        pattern='^('+str(self.CALLBACK_ODOO_CONNECTOR)+')$'
                    ),
                    CallbackQueryHandler(
                        self.workflow_connector,
                        pattern='^('+str(self.CALLBACK_TRY_CONNECTOR)+')$'
                    )
                ],
                self.STATE_TYPING_SIGNIN: [
                    MessageHandler(
                        Filters.text & ~Filters.command, 
                        self.save_typing
                    )
                ],
                self.SH_STATE_ASK_FOR: [
                    CallbackQueryHandler(
                        self.sign_handler.ask_for,
                        pattern='^sign_ask_for_'
                    ),
                    CallbackQueryHandler(
                        self.auth,
                        pattern='^('+str(self.CALLBACK_AUTH)+')$'
                    )
                ],
                self.STATE_HEY_WALLET: self.hey_wallet_handler.handler(),
                self.STATE_LOGOUT: [CommandHandler('start', self.start)], 
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel)
            ],
        )
        return conv_handler
    
    @Log.new_user
    def start(self, update, context):
        buttons = [[
            InlineKeyboardButton(text='Try',callback_data=self.CALLBACK_TRY_CONNECTOR),
            InlineKeyboardButton(text='Odoo' , callback_data=self.CALLBACK_ODOO_CONNECTOR),
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        text = 'Hi! I\'m HeyWalletBot \n\n'\
        'I\'m your personal finance planner and I will help you:\n' \
        '📝 Track spending,🧾 Plan  budget and 💰 Save money. \n\n'\
        'Are you ready? ... or send /cancel to stop talking to me.'
        
        self.reply_text(update, context, text=text, reply_markup=keyboard)

        return self.STATE_WORKFLOW_CONNECTOR

    def workflow_connector(self, update, context):
        connector = update.callback_query.data
        Session.del_from(context.user_data)
        session = Session.get_from(context.user_data)
        if connector == str(self.CALLBACK_ODOO_CONNECTOR):
            session.sign_handler = OdooSignHandler(self) 
            session.hey_wallet_handler = OdooHeyWalletHandler(self)
            session.datasource = Odoo()
        else:
            session.sign_handler = None
            session.hey_wallet_handler = None
            session.datasource = None
        
        Session.set_from(context.user_data, session)
        
        if session.sign_handler:
            return session.sign_handler.workflow_connector(update, context)
        
        return self.sign_handler.workflow_connector(update, context)

    def save_typing(self, update, context):
        session = Session.get_from(context.user_data)
        if session.sign_handler:
            return session.sign_handler.save_typing(update, context)
        return self.sign_handler.save_typing(update, context)
    
    def auth(self, update, context):
        session = Session.get_from(context.user_data)
        if session.sign_handler:
            return session.sign_handler.auth(update, context)
        return self.sign_handler.auth(update, context)

    def cancel(self, update, context):        
        text = '🙋‍♂️ Bye! I hope we can talk again someday ... or /start'
        Session.del_from(context.user_data)
        self.reply_text(update, context, text=text, reply_markup=ReplyKeyboardRemove())
        return self.END

    def button_connect(self, update, context):
        Session.get_from(context.user_data)
        return self.sign_handler.workflow_connect(update, context)

    #def button_signin( self, update, context): 
    #    Session.get_from(context.user_data)
    #    return self.sign_handler.workflow_signin(update, context)

    def reply_text(self, update, context,  **args):
        if getattr(update.message, 'reply_text',False):
            update.message.reply_text(**args)
        elif getattr(update.callback_query, 'edit_message_text',False):
            update.callback_query.answer()
            update.callback_query.edit_message_text(**args)

    pprint = lambda self, val: print(json.dumps(val,  indent=4)) if isinstance(val, dict) or isinstance(val, list) else print(val)

    def del_data(self, update, context, index):               
        try:
            context.user_data[index]
            del context.user_data[index]
        except Exception as e:
            logger.error(str(e))
        
    def set_data(self, update, context, index, value=None ):               
        if not value: 
            value = update.message.text
        context.user_data[index] = value
        logger.info("User data save:  Key: {} Value: {} ".format(str(index), str(value)))

    def get_data(self, update, context, index, value=None):
        return context.user_data.get(index, value)
    
    def from_user(self, udpate, context):
        if getattr(udpate, 'message')  and getattr(udpate.message, 'from_user'):
            return getattr(udpate.message, 'from_user')
        elif getattr(udpate, 'callback_query')  and getattr(udpate.callback_query, 'from_user'):
            return getattr(udpate.callback_query, 'from_user')
        return None