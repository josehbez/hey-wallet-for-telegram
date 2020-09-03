import logging
logger = logging.getLogger(__name__)

class Log:
    
    @classmethod
    def new_user(cls, func):
        def inner(*args, **kwargs):
            user = args[0].from_user(args[1], args[2])

            return func(*args, **kwargs)
        return inner
    
    @classmethod
    def new_user_authenticated(cls, func):
        def inner(*args, **kwargs):
            #user = args[0].from_user(args[1], args[2])
            #cls.info("New user authenticated: %s ", user.first_name)
            return func(*args, **kwargs)
        return inner
    
    @classmethod
    def command(cls, func):
        def inner(*args, **kwargs):
            cls.info("Launch command: %s", func.__name__)
            return func(*args, **kwargs)
        return inner

    @classmethod
    def info(cls, msg, *args, **kwargs):        
        logger.info(msg, *args, **kwargs)
    
    @classmethod
    def error(cls, msg, *args, **kwargs):        
        logger.error(msg, *args, **kwargs)