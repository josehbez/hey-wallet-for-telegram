import xmlrpc.client

class MSBWallet:

    def __init__(self, username, password, database, url):
        self.username = username
        self.password = password
        self.database = database
        self.url = url
        self.uid = False
        self.auth()

    common = lambda self:  xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))

    def is_auth(self):
        return self.uid
        
    def auth(self):
        self.uid = self.common().authenticate(self.database, self.username, self.password, {})
        return self.uid

o = MSBWallet(
'admin@maxs.biza',
'@dmn15tr@dor*/.',
'o13c-sarais',
'http://localhost:8068',
)

o.auth()