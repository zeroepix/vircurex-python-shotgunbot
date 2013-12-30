vircurex-python-shotgunbot
==========================

Python Bot for Vircurex Cryptocurrency Exchange, which creates a range of buy/sell orders based on input.

User inputs the currency to buy/sell against btc, the range of prices they wish to aim at, and how much of each currency to spend. The bot then creates an order for every santoshi in the range, creating buys below market price, and asks above. The API password in Vircurex settings must be the same for get_balance, create_order and release_order for this to work properly.

If TheCleaner option eventually gets added, the API password for read_orders and delete_order must also be the same as those prior.

To use the bot:

- copy/clone the files from github
- use either 'python shotgunbot.py' or '.\shotgun.py' to run it (to those who don't already have it, you need python installed for it to work)
- enter vircurex username/API password (not login password, check settings to set these, make them the same for all)
- save username/password to file, or not (to save you having to type it in every time)
- enter the currency you want to trade 
- enter minimum price *in santoshis* (eg entering 65 would be 0.00000065 btc)
- enter maximum price in santoshis
- enter how much BTC you want to put up (it'll show you how much you have available), just enter if you want to use it all
- enter how much alt-currency you want to put up
- read report, y to confirm
- watch your orders either get released or fail.
