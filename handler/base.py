import logging
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
from  .sign import SignHandler
from  .hey_wallet import HeyWalletHandler
from utils.session import Session

logger = logging.getLogger(__name__)

class BaseHandler:

    STATE_START, BACK, SIGNIN, SIGNUP, OWNSERVER, TYPING, STATE_HEY_WALLET = range(7)

    CALLBACK_SIGNIN, CALLBACK_AUTH = range(100, 102)

    END = ConversationHandler.END

    # SignHandler
    CALLBACK_USERNAME, CALLBACK_PASSWORD, SIGNIN_ASK_FOR, STATE_SIGNIN, STATE_TYPING_SIGNIN, SIGN_HANDLER_MSG = map(chr, range(100, 106))

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
                self.STATE_START: [
                    CallbackQueryHandler(
                        self.button_signin,
                        pattern='^('+str(self.CALLBACK_SIGNIN)+')$'
                    )
                ],
                self.STATE_SIGNIN: [
                    CallbackQueryHandler(
                        self.sign_handler.ask_for_password,
                        pattern='^('+str(self.CALLBACK_PASSWORD)+')$'
                    ),
                     CallbackQueryHandler(
                        self.sign_handler.ask_for_username,
                        pattern='^('+str(self.CALLBACK_USERNAME)+')$'
                    ),
                    CallbackQueryHandler(
                        self.sign_handler.auth,
                        pattern='^('+str(self.CALLBACK_AUTH)+')$'
                    )
                ],
                self.STATE_TYPING_SIGNIN: [
                    MessageHandler(
                        Filters.text & ~Filters.command, 
                        self.sign_handler.save_typing_signin
                    )
                ],
                self.STATE_HEY_WALLET: self.hey_wallet_handler.handler()
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel)
            ],
        )
        return conv_handler

    def start(self, update, context):
        buttons = [[
            InlineKeyboardButton(text='Sign In',callback_data=str(self.CALLBACK_SIGNIN)),
            #InlineKeyboardButton(text='Sing Up', callback_data=str(self.SIGNUP)),
            #InlineKeyboardButton(text='Own Server', callback_data=str(self.OWNSERVER))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        text = 'Hi! My name HeyWalletBot \n\n'\
        'I\'m your personal finance planner, I will help you:\n' \
        '💰 Save money, 🧾 Plan  budget and 📝 Track spending. \n'\
        'You will become your own finance manager.\n\n' \
        'Are you ready? ... or send /cancel to stop talking to me.'
        
        self.reply_text(update, context, text=text, reply_markup=keyboard)

        return self.STATE_START

    def cancel(self, update, context):        
        text = '🙋‍♂️ Bye! I hope we can talk again someday ... or /start'
        self.reply_text(update, context, text=text, reply_markup=ReplyKeyboardRemove())
        return self.END

    def button_signin( self, update, context): 
        Session.get_from(context.user_data)
        return self.sign_handler.workflow_signin(update, context)

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