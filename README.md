vircurex-python-shotgunbot
==========================

Python Bot for Vircurex Cryptocurrency Exchange, which creates a range of buy/sell orders based on input.

User inputs the currency to buy/sell against btc, the range of prices they wish to aim at, and how much of each currency to spend. The bot then creates an order for every santoshi in the range, creating buys below market price, and asks above. The API password in Vircurex settings must be the same for get_balance, create_order and release_order for this to work properly.

If TheCleaner option eventually gets added, the API password for read_orders and delete_order must also be the same as those prior.

To run it put shotgunbot.py and vircurex.py in the same folder, then assuming you have python installed:

.\shotgunbot.py

or

python shotgunbot.py
