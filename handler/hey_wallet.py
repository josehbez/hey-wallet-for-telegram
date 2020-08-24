import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
                        
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
logger = logging.getLogger(__name__)

class HeyWalletHandler:

    WELCOME, INCOME, EXPENSE, CATEGORY, PRODUCT, ACCOUNT = range(6)

    def __init__(self, base_handler):
        self.base_handler = base_handler

    

    def handler(self):
        logger.info("hey wallet handler")
        return [
            ConversationHandler(
                entry_points=[                    
                    #MessageHandler(
                    #    Filters.text ,
                    #    self.welcome,
                    #)
                    #CallbackQueryHandler(
                    #    self.welcome,
                    #    pattern='^' + str(self.base_handler.) + '$'
                    #),
                    #CommandHandler('welcome', self.welcome),
                    CommandHandler('income', self.income),
                    CommandHandler('account', self.account),
                    CommandHandler('category', self.category)
                ],
                states={
                    self.WELCOME: [
                        CommandHandler('income', self.income),
                        CommandHandler('account', self.account),
                        CommandHandler('category', self.category)
                        #CallbackQueryHandler(select_gender,pattern='^{}$|^{}$'.format(str(PARENTS),str(CHILDREN)))
                    ],
                    #SELECTING_GENDER: [description_conv]
                },

                fallbacks=[
                    #CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
                    #CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
                    CommandHandler('logout', self.stop_nested)
                ],

                #map_to_parent={
                #    # After showing data return to top level menu
                #    SHOWING: SHOWING,
                #    # Return to top level menu
                #    END: SELECTING_ACTION,
                #    # End conversation alltogether
                #    LOGOUT: END,
                #}
            ),
            #CallbackQueryHandler(self.welcome, pattern='^' + str(self.base_handler.BUTTON_SIGNIN) + '$'),
            #CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
            #CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
        ]
    
    def welcome(self, update, context):
        text = 'Welcome. /income /category /account'
        if getattr(update.callback_query, 'edit_message_text',False):
            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text)
        elif getattr(update.message, 'reply_text',False):
            update.message.reply_text(text=text)
        return self.WELCOME
    
    def stop_nested(self, update, context):
        """Completely end conversation from within nested conversation."""
        update.message.reply_text('Okay, bye.')
        return  ConversationHandler.END #self.LOGOUT

    def income(self, update, context):
        logger.info(" test command")
        logger.info(update.message.text)
        if getattr(update.message, 'reply_text',False):
            text = '{}'.format(update.message.text)
            update.message.reply_text(text=text)
        elif getattr(update.callback_query, 'edit_message_text',False):
            text = '{}'.format(update.message.text)
            update.callback_query.answer()        
            update.callback_query.edit_message_text(text=text)
        context.user_data[self.CATEGORY] = self.INCOME
        return self.WELCOME

    def account(self, update, context):
        try:
            accounts = self.base_handler.provider.account()
            if isinstance(accounts, dict) and accounts.get('Success'):
                text = "Accounts\n\n"
                for account in accounts.get('Data', []):
                    text += "[{}] {}\n".format(account['id'], account['name'])
                self.base_handler.msg_post(update, context, text=text)
        except Exception as e:
            logger.exception(e)
        return self.WELCOME

    def category(self, update, context):
        if context.user_data[self.CATEGORY]  == self.INCOME:
            categ_in = self.base_handler.provider.category_income()
            if isinstance(categ_in, dict) and categ_in.get('Success'):
                logger.info(str(categ_in.get('Data')))
                products = self.base_handler.provider.product(categ_in.get('Data')[0].get('id'))
                if isinstance(products, dict) and products.get('Success'):
                    logger.info(str(products.get('Data')))
                    keyboard =  []
                    keyboardline = []
                    for product in products.get('Data'):
                        if len(keyboardline) <= 1:
                            keyboardline.append(
                                InlineKeyboardButton(
                                    product.get('name'), 
                                    callback_data= 'product_{}'.format(product.get('id'))
                                )
                            )
                        elif len(keyboardline)== 2:
                            keyboard.append(keyboardline)
                            keyboardline= []
                    if len(keyboardline):
                        keyboard.append(keyboardline)
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text ="Income category"
                    self.base_handler.msg_post(update, context, text=text, reply_markup=reply_markup)
        return self.WELCOME