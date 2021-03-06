import sys
sys.path.append(".")
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, PicklePersistence
from handler.base import BaseHandler
from datasource.odoo import Odoo

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



def main():
    
    token = os.getenv('TELEGRAM_TOKEN', None)
    if not token:
        load_dotenv()
        token = os.getenv('TELEGRAM_TOKEN', None)
    
    pp = None 
    if os.getenv('ENVIRONMENT', '') == 'DEV':
        pp = PicklePersistence(filename='storage/telegram/heywallet')

    if not token:
        logger.error("Is required TELEGRAM_TOKEN  is generate from BotFather.")  
        exit()
    
    updater = Updater(
        token, 
        persistence=pp, 
        use_context=True
    )
    # Get the dispatcher to register handlers
    dp = updater.dispatcher    
    # set Workflow /start
    dp.add_handler(BaseHandler().handler())
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def main2():
    
    from datasource.odoo import OdooHeyWalletHandler
    o = OdooHeyWalletHandler(False)
    o.dummy()
    #pass

    
if __name__ == '__main__':
    main()
    #main2()