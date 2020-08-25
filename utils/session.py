
import logging
from datasource.maxsbiz import MSBHeyWallet
logger = logging.getLogger(__name__)

class Session:

    def __init__(self ):
        self.datasource = None
        self.auth_args = {}

    def set_auth_args(self, **args):
        for key in args.keys():
            self.auth_args[key] = args.get(key)

    def get_auth_args(self, key, value=None):
        return self.auth_args.get(key, value)


    @staticmethod
    def get_from(user_data):
        if "session" not in user_data:
            s = Session()
            s.datasource = MSBHeyWallet()
            user_data["session"] = s

        return user_data["session"]
    
    @staticmethod
    def set_from(user_data, session):
        logger.info(session.__dict__)
        user_data["session"] = session
        return user_data["session"]
    
    @staticmethod
    def del_from(user_data):
        try:
            del user_data["session"]
        except Exception as e:
            logger.error(e)
        
        
        