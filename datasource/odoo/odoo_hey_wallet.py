from handler.hey_wallet import HeyWalletHandler
from utils.session import Session
from utils.log import Log
from . import Odoo
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
from utils.emoji import Emoji

class OdooHeyWalletHandler(HeyWalletHandler):
    def __init__(self, base_handler):
        super(OdooHeyWalletHandler, self).__init__(base_handler)

    def confirm(self, update, context):
        session = Session.get_from(context.user_data)
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
            
            
            req = None
            if oper == 'income':
                req = session.datasource.income(product_id, description, amount, account_journal_id=account_id)
            elif oper == 'expense':
                req = session.datasource.expense(product_id, description, amount, account_journal_id=account_id)
    
            if req and isinstance(req, dict) and req.get('Success'):
                msg = "The {} has been recorded\n\n"\
                    "{}\n"\
                    "Record other /income or /expense or get /help".format(
                        oper, self.state_text(update, context),                        
                    )
                self._reset(update, context)
            else:
                Log.error(req)
                raise Exception("Failed to register the %s,  try later /done" % oper)
        except Exception as e:
            Log.error(e)
            msg = str(e)
        self.base_handler.reply_text(update, context, text=msg, parse_mode='MarkdownV2')
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

    def selected_category(self, update, context):
        cb_data, cb_text = self.selected_inline_keybord(update, context, keyboard_from='product')
        return self.WELCOME
    
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
                                    Emoji.add_label_category( l.get('name')), 
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