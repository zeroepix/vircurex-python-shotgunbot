#!/usr/bin/env python
# Vircurex Shotgun Bot
# User inputs the currency to buy/sell against btc, the range of prices they wish to aim at, and how much of each currency to spend. 
# The bot then creates an order for every satoshi in the range, creating buys below market price, and asks above. 
# The API password in Vircurex settings must be the same for get_balance, create_order and release_order for this to work properly.
# If TheCleaner option eventually gets added, the API password for read_orders and delete_order must also be the same as those prior.
#
# Hunterbunter
# Dec 2013

from vircurex import Vircurex
from vircurex import ShotgunSecrets
from vircurex import PlaceOrders

import sys, os, re

def Verification():
	"""Get username and password from either user or user.ini"""
	while (1):
			try:
				with open ("user.ini") as f: 	# check if user.ini file exists, if so, use it
					data = f.read()
					data = data.split("\n")					
					username = data[0]
					password = data[1]
			except IOError:						# if it doesn't exist, or couldn't be read, delete it
				if os.path.exists("user.ini"):
					os.remove("user.ini")
				username = raw_input("\nEnter Vircurex Username: ")	# get user input for username and password
				password = raw_input("Enter API password: ")
			
			secrets = ShotgunSecrets(password)	# create secrets dictionary
			try:
				exchange = Vircurex(username, secrets)	# create exchange object
				response = exchange.get_balance("btc")	# get btc balance to verify username/password
				if response['status'] != 0:				# if it fails, tell the user why
					print "\n"+response['statustext']
					if response['status'] == 8003 and os.path.exists("user.ini"): # and if it fails because of incorrect username/password, delete the user.ini file if it exists and go back to start
						 os.remove("user.ini")
				else:
					btc_balance = float(response['availablebalance'])	# store btc balance					
					if not os.path.exists("user.ini"):	# ask user if they want to store their username/password so they don't have to enter it again to run this script
						answer = raw_input("\nDo you wish to store your username/password for future use? Y/N: ")
						if answer == "Y" or answer == "y": 
							try:
								f = open("user.ini", 'w')
								f.write(username+"\n"+password)	
								print "\nWARNING: This file is not encrypted; store at your own risk.\nUsername and Password saved in user.ini. Delete this file if you wish to remove it."
							except IOError:
								print "Could not write file user.ini"
					return exchange, btc_balance
			except:
				raise

def TheCleaner():
	"""Get a full list of all released orders, and cancel all of them"""
	print "Yet to be implemented. For now, you can delete all easily enough from the vircurex order page."

def ShotgunBot():
	"""Get User details, check each is valid, 
	then spam vircurex with orders.
	"""
	# First get user's username and API password - User must use the same password for all of the functions for this to work.
	print "\nVircurex Shotgun Bot."
	try:
		secrets = {}
		username = ""
		password = ""
		currency = ""
		min_price = 0.0
		max_price = 0.0
		btc_at_risk = 0.0
		currency_at_risk = 0.0
		btc_balance = 0.0
		currency_balance = 0.0
		avg_market_price = 0
		
		# access and verify username/password
		exchange, btc_balance = Verification()
		print "\nAvailable BTC balance: %.8f btc" % btc_balance
		
		# Get currency details, check that they are valid
		while (1):
			currency = raw_input("\nEnter Currency Code you wish to trade against BTC: ")
			try:
				response = exchange.get_balance(currency)	# verify currency code by getting available balance of it
				if response['status'] != 0:
					print "\n"+response['statustext']
				else:
					currency_balance = float(response['availablebalance'])
					print "\nAvailable %s balance: %.8f %s" % (currency.upper(), currency_balance, currency.lower())
					break
			except:
				raise
		
		# Get minimum and maximum prices
		while (1):
			try:
				market_bid = exchange.get_highest_bid(currency, "btc")
				market_ask = exchange.get_lowest_ask(currency, "btc")
				if market_bid['value'] != None and market_ask['value'] != None:
					avg_market_price = (int(float(market_bid['value'])*100000000) + int(float(market_ask['value'])*100000000)) / 2
					print "\nAverage market price: %d satoshis" % avg_market_price
				else:
					print "\nCould not get market prices. Connection or Vircurex may be down."
					raise Exception
			except:
				raise
			print "0.00000001 btc = 1 Satoshi"
			try:
				min_price = int(raw_input("Enter Minimum price in Satoshis: "))
				max_price = int(raw_input("Enter Maximum price in Satoshis: "))
				if max_price > min_price:
					answer = raw_input("\nEnter increment between orders in Satoshis (eg 1, 10, 100 etc),\nor 'o' then the max number of orders you wish to place (eg o20 = 20 orders)\nInput: ")
					if "o" in answer:
						answer = int(re.sub(r'o', "", answer))
						increments = (max_price - min_price) / (answer)
						if increments == 0:
							increments = 1
					else:
						increments = int(answer)						
					break
				else:
					print "\nThe maximum price must be greater than the minimum price."
			except ValueError:
				print "\nPrices must be whole integers. If you want 0.00010000 as the price, you need to enter 10000."
			except:
				raise
		# Get BTC and DVC to put up for buy and sell orders
		while (1):
			try:
				str1 = "\nEnter amount of BTC to put up (%.8f available, leave blank to use all of it): " % btc_balance
				str2 = "Enter amount of %s to put up (%.8f available, leave blank to use all of it): " % (currency.upper(), currency_balance)
				answer = raw_input(str1)
				if answer == "":
					btc_at_risk = btc_balance
				else:
					btc_at_risk = float(answer)
				if btc_at_risk > btc_balance:
					raise					
				answer = raw_input(str2)
				if answer == "":
					currency_at_risk = currency_balance
				else:
					currency_at_risk = float(answer)
				if currency_at_risk > currency_balance:
					raise
				break
			except KeyboardInterrupt:
				raise
			except:
				print "\nThe amounts must be floating point numbers (or whole numbers), and equal to or below the amount available."
		
		# Get current marking bid and ask
		try:			
			# find upper and lower range
			if avg_market_price > min_price:
				if max_price < avg_market_price: # all of our orders are going to be bids
					lower_range = int((max_price - min_price + 1)/increments)					
				else:
					lower_range = int((avg_market_price - min_price)/increments) 	# how many satoshis are going to be buy orders (not all of them)
				btc_segments = btc_at_risk / lower_range	# the btc value of each segment
			else:
				lower_range = 0
				btc_segments = 0
			if avg_market_price < max_price:
				if min_price > avg_market_price:
					upper_range = int((max_price - min_price + 1)/increments)					
				else:
					upper_range = int((max_price - avg_market_price)/increments)				# how many santoshis are going to be sell orders
				currency_segments = currency_at_risk / upper_range	# the currency value of each segment
			else:
				upper_range = 0
				currency_segments = 0
			
			print "\nReport:\nThe average market price is: %d satoshis(btc) per 1 %s" % (avg_market_price, currency)
			print "There will be %.0f buy orders worth %.8f btc each - MUST be above 0.0001 btc to be accepted by vircurex" % (lower_range, btc_segments)
			print "There will be %.0f sell orders worth %.8f %s each - MUST be above %.4f %s to be accepted by vircurex" % (upper_range, currency_segments, currency, 10000.0/avg_market_price, currency)
			answer = raw_input("\nProceed? Y/N: ")
			if answer == "Y" or answer == "y":
				PlaceOrders(exchange, "buy", currency, btc_segments, min_price/100000000.0, int(lower_range), increments)
				PlaceOrders(exchange, "sell", currency, currency_segments, max_price/100000000.0, int(upper_range), increments)
			
		except:
			raise
	except KeyboardInterrupt:
		exit(1)
	except Exception as e:
		print e

def Entry():
	"""Ask user whether they want to close all open and released orders, or create more orders"""
	print "\nVircurex ShotgunBot and Cleaner.\nWhat would you like to do?\n1) Create a batch of orders.\n2) Close all open and released orders."
	answer = raw_input("Command: ")
	if answer == "1":
		ShotgunBot()
	elif answer == "2":
		TheCleaner()	
		
if __name__ == "__main__":
	#Entry()
	ShotgunBot()

