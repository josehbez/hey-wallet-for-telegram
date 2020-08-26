import xmlrpc.client
import json

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
        
    def auth(self, **args):
        self.username = 'jose@heywallet.com'#args.get('username')
        self.password = 'jose@heywallet.com'#args.get('password')
        self.database = 'heywallet' #args.get('database', 'wallet.maxs.biz')
        self.url = 'http://localhost:8068'#args.get('url','https://wallet.maxs.biz')
        self.uid = self.common().authenticate(self.database, self.username, self.password, {})
        return self.uid

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

    #def welcome(self):
    #    return ' \- _[{}]({})_'.format(
    #            self.name,
    #            self.url, 
    #        )

    def name(self):
        return 'Odoo / %s' % self.url