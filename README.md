<p align="center">    
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/josehbez/hey-wallet-for-telegram?style=flat-square" />
  </a>
  <a href="semv.toml">
    <img src="https://img.shields.io/badge/semv-1.0.1-green"/>
  </a>
</p>
<p align="center">
  <a href="http://t.me/HeyWalletBot">
    <img src="https://img.shields.io/badge/Telegram Bot-t.me/HeyWalletBot-blue"/>
  </a>
</p>

## Hey Wallet for Telegram Bot

It is a gateway that runs on the server to interact with the bot and connects commonly used financial software for to execute operations simply and quickly.

* Record of income and expenses
* Select a category or put a description
* Select a bank or cash account


## Connectors 

* ✅ Try (Demo)
* ✅ [Odoo](http://odoo.com/) you need to have the module installed `msb_hey_wallet`.


![](preview.gif)

## Run own server

### Docker 
```bash
export TELEGRAM_TOKEN=TOKEN && docker-compose up -d
```

### Pipenv 

```bash
pipenv shell 
pip install -r requirements.tx 
export TELEGRAM_TOKEN=TOKEN
python main.py
```