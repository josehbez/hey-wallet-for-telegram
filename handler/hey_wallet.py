import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
                        
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
logger = logging.getLogger(__name__)
from utils.session import Session


class HeyWalletHandler:

    WELCOME, INCOME, EXPENSE, CATEGORY, DESCRIPTION, PRODUCT, ACCOUNT = range(4000, 4007)

    def __init__(self, base_handler):
        self.base_handler = base_handler

    

    def handler(self):
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler('income', self.income),
                    CommandHandler('expense', self.expense),
                    
                    CommandHandler('category', self.category),
                    CommandHandler('account', self.account),
                    CommandHandler('description', self.description),
                    CommandHandler('confirm', self.confirm),
                    
                    CommandHandler('help', self.help), 
                    CommandHandler('state', self.state),
                    CommandHandler('reset', self.reset),                     

                ],
                states={
                    self.WELCOME: [
                        
                        CommandHandler('income', self.income),
                        CommandHandler('expense', self.expense),

                        CommandHandler('account', self.account),
                        CommandHandler('category', self.category),
                        CommandHandler('description', self.description),
                        CommandHandler('confirm', self.confirm),

                        CommandHandler('help', self.help), 
                        CommandHandler('state', self.state), 
                        CommandHandler('reset', self.reset), 
                        
                        CallbackQueryHandler(self.selected_product,pattern='^product_(\d+)$'),
                        CallbackQueryHandler(self.category,pattern='^category_(\d+)$'),
                        CallbackQueryHandler(self.selected_account,pattern='^account_(\d+)$')
                    ],
                    self.base_handler.HWH_STATE_TYPING: [
                        MessageHandler(
                            Filters.text & ~Filters.command, 
                            self.save_typing
                        )
                    ],
                },

                fallbacks=[
                    CommandHandler('logout', self.logout)
                ],

                map_to_parent={                
                    self.base_handler.STATE_LOGOUT: self.base_handler.STATE_LOGOUT,
                }
            ),
        ]
    
    

    def welcome(self, update, context):
        user = self.base_handler.from_user(update, context)
        user_first_name = user and user.first_name
        session = Session.get_from(context.user_data)
        text = '✨ Welcome *%s* ' % user_first_name or ''
        #if getattr( session.datasource, 'welcome'):
        #    text += session.datasource.welcome()
        text += '\n\nTry the command  /help'

        self.base_handler.reply_text(update, context, text=text, parse_mode="MarkdownV2")
        return self.WELCOME
    
    def help(self, update, context):
        text = 'Track income and expenses\n\n'\
            '1️⃣ Type operation /income or /expense\n'\
            '2️⃣ Write amount\n'\
            '3️⃣ Select the /category\n'\
            '4️⃣ Write /description\n'\
            '5️⃣ Select /account \n'\
            '6️⃣ /confirm operation \n\n'\
            '📌 Workflow /state\n'\
            '📌 Workflow /reset\n'\
            '📌 Close session /logout\n'

        self.base_handler.reply_text(update, context, text=text)
        return self.WELCOME

    def state(self, update, context, label=False):
        session = Session.get_from(context.user_data)
        text = '🗄️ Data Source: {}\n'\
            '🖊️ Operation: {}\n'\
            '💲 Amount: {}\n'\
            '🏦 Account: {} \n'\
            '🏷️ Description: {} \n'\
            '🗃️ Category: {} \n'\
            ''.format(
                session.datasource.name(), 
                self.operation(update, context).title(),
                self.base_handler.get_data(update, context, 
                    self.base_handler.HWH_AMOUNT, 0
                ), 
                "{} - {}".format(
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_ACCOUNT_ID, ''
                    ),
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_ACCOUNT_NAME, ''
                    )
                ),                
                self.base_handler.get_data(update, context, 
                    self.base_handler.HWH_DESCRIPTION, ''
                ) ,
                "{} - {}".format(
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_PRODUCT_ID, ''
                    ),
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_PRODUCT_NAME, ''
                    )
                )
            )
        
        if label:
            return text
        self.base_handler.reply_text(update, context, text=text)
        return self.WELCOME
    
    def logout(self, update, context):
        Session.del_from(context.user_data)
        self.base_handler.reply_text(update, context, text="Okay, bye. /start")
        return  self.base_handler.STATE_LOGOUT
    
    def description(self, update, context):
        oper = self.operation(update, context)
        oper = '' if oper == 'undefined' else oper

        self.base_handler.reply_text(update, context, text="write the %s description" % oper)
        self.base_handler.set_data(update, context, 
            self.base_handler.HWH_ASK_FOR,
            self.base_handler.HWH_DESCRIPTION
        )
        return self.base_handler.HWH_STATE_TYPING

    def expense(self, update, context):         
        self.base_handler.reply_text(update, context, text="🙁Enter the amount of expense")
        context.user_data[self.base_handler.HWH_OPERATION] = self.base_handler.HWH_EXPENSE
        self.base_handler.set_data(update, context, 
            self.base_handler.HWH_ASK_FOR,
            self.base_handler.HWH_EXPENSE
        )
        return self.base_handler.HWH_STATE_TYPING

    def income(self, update, context):
        self.base_handler.reply_text(update, context, text="🙂Enter the amount of income")
        context.user_data[self.base_handler.HWH_OPERATION] = self.base_handler.HWH_INCOME
        self.base_handler.set_data(update, context, 
            self.base_handler.HWH_ASK_FOR,
            self.base_handler.HWH_INCOME
        )
        return self.base_handler.HWH_STATE_TYPING
    
    def operation(self, update, context):
        oper = self.base_handler.get_data(update, context, self.base_handler.HWH_OPERATION)
        to = 'undefined'
        if oper == self.base_handler.HWH_INCOME:
            to = 'income'
        elif oper == self.base_handler.HWH_EXPENSE:
            to = 'expense'
        return to

    def reset(self, update, context, onlyreset=False):
        for i in [self.base_handler.HWH_PRODUCT_ID, self.base_handler.HWH_PRODUCT_NAME, 
            self.base_handler.HWH_ACCOUNT_NAME, self.base_handler.HWH_ACCOUNT_ID, 
            self.base_handler.HWH_DESCRIPTION, self.base_handler.HWH_AMOUNT, self.base_handler.HWH_OPERATION, 
            self.base_handler.HWH_ASK_FOR]:
            self.base_handler.del_data(update, context, i)
        if onlyreset:
            return 
        text ="Operation has been restarted, try /income ,  /expense or /help"
        self.base_handler.reply_text(update, context, text=text)
        return self.WELCOME
        

    def confirm(self, update, context):
        try:
            oper = self.operation(update, context)
            if oper == 'unidefined':
                raise Exception("First define what operation you want to do /income or /expense")

            amount = self.base_handler.get_data(update, context, self.base_handler.HWH_AMOUNT, 0)
            if not amount:
                raise Exception("Please run the command /income or /expense and capture the amount")
            
            product_id = self.base_handler.get_data(update, context, self.base_handler.HWH_PRODUCT_ID, False)
            description = self.base_handler.get_data(update, context, self.base_handler.HWH_DESCRIPTION, False)
            account_id =  self.base_handler.get_data(update, context, self.base_handler.HWH_ACCOUNT_ID, False)
            session = Session.get_from(context.user_data)

            req = None
            if oper == 'income':
                req = session.datasource.income(product_id, description, amount, account_journal_id=account_id)
            elif oper == 'expense':
                req = session.datasource.expense(product_id, description, amount, account_journal_id=account_id)

            if req and isinstance(req, dict) and req.get('Success'):
                msg = "The {} has been recorded\n\n"\
                    "{}\n"\
                    "Record other /income or /expense or get /help".format(
                        oper, self.state(update, context, label=True),                        
                    )
                self.reset(update, context, onlyreset=True)
            else:
                logger.error(req)
                raise Exception("Failed to register the %s,  try later /done" % oper)
        except Exception as e:
            msg = str(e)
        self.base_handler.reply_text(update, context, text=msg)
        return self.WELCOME

    def selected_account(self, update, context):
        cb_data, cb_text = self.selected_inline_keybord(update, context, keyboard_from='account')
        return self.WELCOME

    def account(self, update, context):
        session = Session.get_from(context.user_data)
        accounts = session.datasource.account()
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
    
    def selected_product(self, update, context):
        cb_data, cb_text = self.selected_inline_keybord(update, context, keyboard_from='product')
        return self.WELCOME

    def selected_inline_keybord(self, update, context, keyboard_from):
        data = update.callback_query.data
        def get_callback_name(id):
            if getattr(update.callback_query, 'message'):
                if getattr(update.callback_query.message, 'reply_markup'):
                    for ik in update.callback_query.message.reply_markup.inline_keyboard:
                        for b in ik:
                            if id == b.callback_data:
                                return b.text
            return ''
        callback_name = get_callback_name(data)        
        callback_id =''.join( filter( str.isdigit, data))
        id, name = None, None
        if keyboard_from == 'product':
            id = self.base_handler.HWH_PRODUCT_ID
            name = self.base_handler.HWH_PRODUCT_NAME 
        elif keyboard_from == 'account':
            id = self.base_handler.HWH_ACCOUNT_ID
            name = self.base_handler.HWH_ACCOUNT_NAME

        if id and name:
            self.base_handler.set_data(update, context, index=id, value=callback_id)        
            self.base_handler.set_data(update, context, index=name, value=callback_name)
            self.base_handler.reply_text(update, context, text="%s - %s" % (callback_id , callback_name))

        return callback_id, callback_name

    def category(self, update, context):
        oper = self.operation(update, context)
        categories = None        
        category_id_callback = getattr(update, 'callback_query') and getattr(update.callback_query, 'data') or None
        session = Session.get_from(context.user_data)

        if oper == 'income' and not category_id_callback:
            categories = session.datasource.category_income()
        elif oper == 'expense' and not category_id_callback:
            categories = session.datasource.category_expense()
        elif category_id_callback:
            categories = {
                'Success': True, 
                'Data': [{'id': ''.join( filter( str.isdigit, category_id_callback))}]
            }
        else:
            msg = "Not is running commad /income or /expense for get category list"
        
        reply_markup = None
        if categories and  isinstance(categories, dict) and categories.get('Success'):
            msg = 'Select the {} category.'.format( oper if oper else  '')
            categories_data = categories.get('Data')
            category_product = None
            req = {}
            if len(categories_data) == 1:
                category_product = 'product_'                
                req = session.datasource.product(categories_data[0].get('id'))
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

    def save_typing(self, update, context):
        ask_for = self.base_handler.get_data(
            update, 
            context, 
            self.base_handler.HWH_ASK_FOR, 
            None
        )
        if not ask_for: 
            return self.WELCOME

        if ask_for == self.base_handler.HWH_INCOME or ask_for == self.base_handler.HWH_EXPENSE: 
            match = Filters.regex('(\d+(\.\d+)?)').filter(update.message).get('matches',[])            
            if len(match) and match[0].group():
                self.base_handler.set_data(update, context, self.base_handler.HWH_AMOUNT,match[0].group())
            else:                
                return self.income(update, context) if ask_for == self.base_handler.HWH_INCOME else self.expense(update, context)
        else:
            self.base_handler.set_data(update, context, ask_for, update.message.text)

        return self.WELCOME
