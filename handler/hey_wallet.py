import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, 
                        InlineKeyboardButton, InlineKeyboardMarkup)
                        
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          )
logger = logging.getLogger(__name__)
from utils import Session, Emoji, Log


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
                        
                        CallbackQueryHandler(self.selected_category,pattern='^product_(\d+)$'),
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
    
    
    @Log.new_user_authenticated
    def welcome(self, update, context):
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.welcome(update, context)
        
        user = self.base_handler.from_user(update, context)
        user_first_name = user and user.first_name        
        text = '✨ Welcome *%s*  /help' % user_first_name or ''
        self.base_handler.reply_text(update, context, text=text, parse_mode="MarkdownV2")
        return self.base_handler.STATE_HEY_WALLET
    
    def help(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.help(update, context)
        
        text = 'Track income and expenses\n\n'\
            '1️) Type operation /income or /expense\n'\
            '2️) Select /category\n'\
            '3️) Write /description\n'\
            '4) Select /account \n'\
            '5) /confirm operation \n\n'\
            'Try /state /reset /logout \n'

        self.base_handler.reply_text(update, context, text=text)
        return self.WELCOME

    
    def state_text(self, update, context):
        session = Session.get_from(context.user_data)

        text = '🗄️ Data Source: {}\n'\
            '🖊️ Operation: {}\n'\
            '💲 Amount: {}\n'\
            '🏦 Account: {} \n'\
            '🏷️ Description: {} \n'\
            '🗃️ Category: {} \n'\
            ''.format(
                session.datasource.name() if session.datasource else 'Try',
                self.operation(update, context).title(),
                str(self.base_handler.get_data(update, context, 
                    self.base_handler.HWH_AMOUNT, 0
                )).replace('.','\.'), 
                "{} \- {}".format(
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
                "{} \- {}".format(
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_PRODUCT_ID, ''
                    ),
                    self.base_handler.get_data(update, context, 
                        self.base_handler.HWH_PRODUCT_NAME, ''
                    )
                )
            )
        return text

    def state(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.state(update, context)

        text = self.state_text(update, context)
        self.base_handler.reply_text(update, context, text=text, parse_mode='MarkdownV2')

        return self.WELCOME
    
    @Log.command
    def logout(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.logout(update, context)
        
        Session.del_from(context.user_data)
        self.base_handler.reply_text(update, context, text="Okay, bye. /start")
        return  self.base_handler.STATE_LOGOUT
    
    def description(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.description(update, context)
        
        oper = self.operation(update, context)
        oper = '' if oper == 'undefined' else oper

        self.base_handler.reply_text(update, context, text="write the %s description" % oper)
        self.base_handler.set_data(update, context, 
            self.base_handler.HWH_ASK_FOR,
            self.base_handler.HWH_DESCRIPTION
        )
        return self.base_handler.HWH_STATE_TYPING

    def expense(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.expense(update, context)                 
        self.base_handler.reply_text(update, context, text="🙁Enter the amount of expense")
        context.user_data[self.base_handler.HWH_OPERATION] = self.base_handler.HWH_EXPENSE
        self.base_handler.set_data(update, context, 
            self.base_handler.HWH_ASK_FOR,
            self.base_handler.HWH_EXPENSE
        )
        return self.base_handler.HWH_STATE_TYPING

    def income(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.income(update, context)
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

    def _reset(self, update, context):
        for i in [self.base_handler.HWH_PRODUCT_ID, self.base_handler.HWH_PRODUCT_NAME, 
            self.base_handler.HWH_ACCOUNT_NAME, self.base_handler.HWH_ACCOUNT_ID, 
            self.base_handler.HWH_DESCRIPTION, self.base_handler.HWH_AMOUNT, self.base_handler.HWH_OPERATION, 
            self.base_handler.HWH_ASK_FOR]:
            self.base_handler.del_data(update, context, i)

    def reset(self, update, context):
        #session = Session.get_from(context.user_data)
        #if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
        #    return session.hey_wallet_handler.reset(update, context)
        self._reset(update, context)
        text ="Operation has been restarted, try /income ,  /expense or /help"
        self.base_handler.reply_text(update, context, text=text)
        return self.WELCOME
     
    def confirm(self, update, context):
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.confirm(update, context)

        oper = self.operation(update, context)
          
        msg = "The {} has been recorded\n\n"\
                "{}\n"\
                "Record other /income or /expense or get /help".format(
                    oper, self.state_text(update, context),                        
                )
        self._reset(update, context)  
        self.base_handler.reply_text(update, context, text=msg, parse_mode='MarkdownV2')

        return self.WELCOME

    def selected_account(self, update, context):
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.selected_account(update, context)
        
        callback_id = update.callback_query.data
        self.base_handler.reply_text(update, context, text="%s" % callback_id)
        return self.WELCOME

    def account(self, update, context):
        
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.account(update, context)
        
        msg = 'Select the account'
        keyboard =  [
            [
                InlineKeyboardButton('Bank',  callback_data='account_1'),
                InlineKeyboardButton('Cash',  callback_data='account_2'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.base_handler.reply_text(update, context, text=msg, reply_markup=reply_markup)
        return self.WELCOME
    
    def selected_category(self, update, context):
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.selected_category(update, context)
        
        callback_id = update.callback_query.data
        self.base_handler.reply_text(update, context, text="%s" % callback_id)
        return self.WELCOME

    def category(self, update, context):
        session = Session.get_from(context.user_data)
        if session.hey_wallet_handler and self.__class__.__name__ == 'HeyWalletHandler':
            return session.hey_wallet_handler.category(update, context)

        oper = self.operation(update, context)

        msg = "Not is running commad /income or /expense for get category list"
        reply_markup = None
        msg_oper = 'Select the {} category.'.format( oper if oper else  '')

        if oper == 'income':
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    Emoji.add_label_category('Income'), callback_data= 'product_2'
                )
            ]])
        elif oper == 'expense':
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    Emoji.add_label_category('Shop'), callback_data= 'product_1'
                )
            ]])
        msg = msg_oper if reply_markup else msg
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
