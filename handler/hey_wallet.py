import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
                        
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
logger = logging.getLogger(__name__)

class HeyWalletHandler:

    WELCOME, INCOME, EXPENSE, CATEGORY, DESCRIPTION, PRODUCT, ACCOUNT = range(3000, 3007)

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
                    CommandHandler('expense', self.expense),
                    CommandHandler('category', self.category),
                    CommandHandler('done', self.account)
                ],
                states={
                    self.WELCOME: [
                        CommandHandler('income', self.income),
                        CommandHandler('expense', self.expense),
                        CommandHandler('done', self.account),
                        CommandHandler('category', self.category),
                        CallbackQueryHandler(self.product,pattern='^product_(\d+)$'),
                        CallbackQueryHandler(self.category,pattern='^category_(\d+)$'),
                        CallbackQueryHandler(self.done,pattern='^account_(\d+)$')
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
            #CallbackQueryHandler(self.welcome, pattern='^' + str(self.base_handler.CALLBACK_AUTH) + '$'),
            #CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
            #CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
        ]
    
    def welcome(self, update, context):
        text = 'Welcome. /income /expense /category /account'
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
   
    def expense(self, update, context):         
        self.base_handler.reply_text(update, context, text="Expense ... ")
        context.user_data[self.CATEGORY] = self.EXPENSE
        return self.WELCOME

    def income(self, update, context):
        self.base_handler.reply_text(update, context, text="Income ...")
        context.user_data[self.CATEGORY] = self.INCOME
        return self.WELCOME
    

    def operation(self, update, context):
        oper = str(self.base_handler.get_data(update, context, self.CATEGORY))
        to = 'undefined'
        if oper == str(self.INCOME):
            to = 'income'
        elif oper == str(self.EXPENSE):
            to = 'expense'
        return to

    def done(self, update, context):
        try:
            oper = self.operation(update, context)
            if oper == 'unidefined':
                raise Exception("First define what operation you want to do /income or /expense")
            amount = 100 #self.base_handler.get_data(update, context, self.AMOUNT)
            if not amount:
                raise Exception("Please run the command /income or /expense and capture the amount")
            product_id = self.base_handler.get_data(update, context, self.PRODUCT, None)
            description = self.base_handler.get_data(update, context, self.DESCRIPTION, oper)
            account_id = getattr(update, 'callback_query') and getattr(update.callback_query, 'data') or ''
            account_journal_id = ''.join( filter( str.isdigit, account_id))
            req = None
            if oper == 'income':
                req = self.base_handler.provider.income(product_id, description, amount, account_journal_id=account_journal_id)
            elif oper == 'expense':
                req = self.base_handler.provider.expense(product_id, description, amount, account_journal_id=account_journal_id)
            if req and isinstance(req, dict) and req.get('Success'):
                msg = "The {} has been recorded\n"\
                    "* Category -  {}\n"\
                    "* Account  -  {}\n"\
                    "* Amount   - ${}\n"\
                    "* State    - {}\n\n"\
                    "Record other /income or /expense or get /help".format(
                        oper, 
                        "{} ] {} ".format( product_id  or '', description),
                        account_journal_id,
                        amount, 
                        'Posted' if account_journal_id else 'Draft'
                    )
            else:
                logger.error(req)
                msg ="Failed to register the %s,  try later /done" % oper
        except Exception as e:
            msg = str(e)
        self.base_handler.reply_text(update, context, text=msg)
        return self.WELCOME

    def account(self, update, context):        
        accounts = self.base_handler.provider.account()
        reply_markup= None
        if isinstance(accounts, dict) and accounts.get('Success') and len(accounts.get('Data', [])):
            msg = 'Select the account'
            keyboard =  []
            keyboardline = []                    
            for row in accounts.get('Data', []):
                if len(keyboardline) <= 1:
                    keyboardline.append(
                        InlineKeyboardButton(
                            row.get('name'), 
                            callback_data= 'account_{}'.format(row.get('id'))
                        )
                    )                
                if len(keyboardline)== 2:
                    keyboard.append(keyboardline)
                    keyboardline= []

            if len(keyboardline):
                keyboard.append(keyboardline)
            if len(keyboard):
                reply_markup = InlineKeyboardMarkup(keyboard)
        else: 
            msg = "Could not get accounts, try later /done"

        self.base_handler.reply_text(update, context, text=msg, reply_markup=reply_markup)
        return self.WELCOME

    def product(self, update, context):
        product_id = update.callback_query.data
        logger.info("Product id: %s " % product_id)
        product_id =''.join( filter( str.isdigit, product_id) ) 
        self.base_handler.set_data(update, context, index=self.PRODUCT, value=product_id)
        self.base_handler.reply_text(update, context, text="Product selected: %s" % product_id)
        return self.WELCOME

    def category(self, update, context):
        
        kind_category = context.user_data.get(self.CATEGORY,"")
        categories = None
        kind_category_label = None
        category_id_callback = getattr(update, 'callback_query') and getattr(update.callback_query, 'data') or None
        logger.info("Execute command /category ")
        if kind_category == self.INCOME and not category_id_callback:
            categories = self.base_handler.provider.category_income()
            kind_category_label  = 'income'
        elif kind_category == self.EXPENSE and not category_id_callback:
            kind_category_label  = 'expense' 
            categories = self.base_handler.provider.category_expense()
        elif category_id_callback:
            logger.info("from callback")
            categories = {
                'Success': True, 
                'Data': [{'id': ''.join( filter( str.isdigit, category_id_callback))}]
            }
        else:
            msg = "Not is running commad /income or /expense for get category list"
        reply_markup = None
        if categories and  isinstance(categories, dict) and categories.get('Success'):
            msg = 'Select the {} category.'.format( kind_category_label if kind_category_label else  '')
            categories_data = categories.get('Data')
            category_product = None
            req = {}
            if len(categories_data) == 1:
                category_product = 'product_'                
                req = self.base_handler.provider.product(categories_data[0].get('id'))
            elif len(categories_data) > 1:
                category_product = 'category_'
                req = categories
            if category_product:                
                if isinstance(req, dict) and req.get('Success', False) and len(req.get('Data',[])):
                    keyboard =  []
                    keyboardline = []                    
                    for l in req.get('Data'):
                        if len(keyboardline) <= 1:
                            keyboardline.append(
                                InlineKeyboardButton(
                                    l.get('name'), 
                                    callback_data= '{}{}'.format(category_product, l.get('id'))
                                )
                            )
                        
                        if len(keyboardline)== 2:
                            keyboard.append(keyboardline)
                            keyboardline= []

                    if len(keyboardline):
                        keyboard.append(keyboardline)
                    if len(keyboard):
                        reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    msg="Could not get use categories use command /description"
            else:
                msg="Could not get use categories use command /description"
        self.base_handler.reply_text(update, context, text=msg, reply_markup=reply_markup)
        return self.WELCOME