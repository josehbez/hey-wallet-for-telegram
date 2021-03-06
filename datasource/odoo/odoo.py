import xmlrpc.client
import json
import re 
from urllib.parse import urlparse
import os 

class Odoo:

    def __init__(self):        
        pass

    common = lambda self: xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))

    def models(self, model, method, domain, options=False):
        if not self.uid:
            print("is not auth")
            return False
        x = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        return x.execute_kw(self.database, self.uid, self.password, model, method, domain, options)
     
    def is_auth(self):
        return self.uid

    def demo_creadentials(self):
        if str(os.getenv('ENVIRONMENT')) == 'DEV':
            return {
                'url':os.getenv('ODOO_URL'),
                'database':os.getenv('ODOO_DATABASE'),
                'username':os.getenv('ODOO_USERNAME'),
                'password':os.getenv('ODOO_PASSWORD'),
            }
        return None
        
        

    def auth(self, **args):
        args = self.demo_creadentials() or args    
        print(args)
        up = urlparse(args.get(
            'url',
            'https://wallet.maxs.biz'
        ))

        url = '{}://{}'.format(
            up.scheme or 'https', up.netloc
        )

        self.username = args.get('username')
        self.password = args.get('password')
        self.database = args.get('database', 'wallet.maxs.biz')
        self.url = url
        self.uid = self.common().authenticate(self.database, self.username, self.password, {})
        return self.uid

    def auth_exception(self, e):
        msg = str(e)
        text = ''
        if re.search(r"(database).*(does not exist)", msg):            
            for g in re.search(r"(database).*(does not exist)", msg).groups():
                text += ' '+ g        
        elif re.search(r"unsupported XML-RPC protocol", msg):
            text += 'URL unsupported XML-RPC protocol'
        elif re.search(r"common: 404 NOT FOUND", msg):
            text += 'URL XML-RPC not found'
        return len(text) and text or None


    def category_income(self):
        return self.models(
                'hey.wallet',
                'hey_wallet_product_category',
                [{
                    'kind':'income',
                }],
            )

    def category_expense(self):
        return self.models(
                'hey.wallet',
                'hey_wallet_product_category',
                [{
                    'kind':'expense',
                }],
            )

    def product(self, category_id):
        return self.models(
                'hey.wallet',
                'hey_wallet_product',
                [{
                    'category_id':category_id,
                }],
            )
    
    def account(self):
        return self.models('hey.wallet','hey_wallet_account',[{}], )

    def income(self, product_id, description, amount, account_journal_id=False):
        res = self.models(
                'hey.wallet',
                'hey_wallet_tracking',
                [{
                    'kind':'income',
                    'product_id': product_id, 
                    'description': description, 
                    'amount': amount,
                    'account_journal_id': account_journal_id,
                }],
            )
        return res

    def expense(self, product_id, description, amount, account_journal_id=False):
        res = self.models(
                'hey.wallet',
                'hey_wallet_tracking',
                [{
                    'kind':'expense',
                    'product_id': product_id, 
                    'description': description, 
                    'amount': amount,
                    'account_journal_id': account_journal_id
                }],
            )
        return res

    def payment(self, account_account_id,account_move_id ):
        res = self.models(
                'hey.wallet',
                'hey_wallet_payment',
                [{
                    'account_journal_id': account_account_id,
                    'account_move_id': account_move_id,
                }],
            )
        return res

    name = lambda self: 'Odoo'

    def white_list(self, url):
        pass