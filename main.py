
import logging
from telegram.ext import Updater

from handler.base import BaseHandler
from providers.maxsbiz import MSBHeyWallet

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

import sys
sys.path.append(".")


def main():
    updater = Updater("1292507662:AAEKz6xPYp-hbdkaT7rx7bnUxMBhTzMtkRg", use_context=True)
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

if __name__ == '__main__':
    main()