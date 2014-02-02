# Vircurex.py
# This is a modified class based on https://github.com/alexroat/python-vircurex/blob/master/vircurex.py to support the shotgun bot.
#
# Hunterbunter
# Dec 2013

import time
import json
import urllib, urllib2
import hashlib
import random
import sys

class Vircurex:
		domain="https://api.vircurex.com"#domain
		@staticmethod
		def simpleRequest(command,**params):
				global domain
				url="%s/api/%s.json?%s"%(Vircurex.domain,command,urllib.urlencode(params.items()))#url
				request = urllib2.Request(url, headers={'User-Agent':"Magic Browser"})
				con = urllib2.urlopen(request)
				return json.load(con)
		@staticmethod
		def secureRequest(user,secret,command,tokenparams,**params):
				global domain
				t = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime())#UTC time
				txid=hashlib.sha256("%s-%f"%(t,random.randint(0,1<<31))).hexdigest();#unique trasmission ID using random hash
                #token computation
				vp=[command]+map(lambda x:params[x],tokenparams)
				token_input="%s;%s;%s;%s;%s"%(secret,user,t,txid,';'.join(map(str,vp)))
				token=hashlib.sha256(token_input).hexdigest()
				#cbuilding request
				reqp=[("account",user),("id",txid),("token",token),("timestamp",t)]+params.items()
				url="%s/api/%s.json?%s"%(Vircurex.domain,command,urllib.urlencode(reqp))#url
				request = urllib2.Request(url, headers={'User-Agent':"MagicBrowser"})
				con = urllib2.urlopen(request)
				return json.load(con)				
		#insert user and a dict with secrets set in your account settings (e.g. : create_order=>q12we34r5t)
		def __init__(self,user=None,secrets={}):
				self.user=user
				self.secrets=secrets
		#trade API
		def get_balance(self,currency):
				return Vircurex.secureRequest(self.user,self.secrets["get_balance"],"get_balance",["currency"],currency=currency)
		def get_balances(self):
				return Vircurex.secureRequest(self.user,self.secrets["get_balance"],"get_balances",[])['balances']
		def create_order(self,ordertype,amount,currency1,unitprice,currency2):
				return Vircurex.secureRequest(self.user,self.secrets["create_order"],"create_order",["ordertype","amount","currency1","unitprice","currency2"],ordertype=ordertype,amount=amount,currency1=currency1,unitprice=unitprice,currency2=currency2)
		def release_order(self,orderid):
				return Vircurex.secureRequest(self.user,self.secrets["release_order"],"release_order",["orderid"],orderid=orderid)                
		def delete_order(self,orderid,otype):
				return Vircurex.secureRequest(self.user,self.secrets["delete_order"],"delete_order",["orderid","otype"],orderid=orderid,otype=otype)
		def read_order(self,orderid,otype):
				return Vircurex.secureRequest(self.user,self.secrets["read_order"],"read_order",["orderid"],orderid=orderid,otype=otype)
		def read_orders(self,otype):
				return Vircurex.secureRequest(self.user,self.secrets["read_orders"],"read_orders",[],otype=otype)
		def read_orderexecutions(self,orderid):
				return Vircurex.secureRequest(self.user,self.secrets["read_orderexecutions"],"read_orderexecutions",["orderid"],orderid=orderid)
		def create_coupon(self,amount,currency):
				return Vircurex.secureRequest(self.user,self.secrets["create_coupon"],"create_coupon",["amount","currency"],amount=amount,currency=currency)
		def redeem_coupon(self,coupon):
				return Vircurex.secureRequest(self.user,self.secrets["redeem_coupon"],"redeem_coupon",["coupon"],coupon=coupon)
		##info API
		def get_lowest_ask(self,base,alt):
				return Vircurex.simpleRequest("get_lowest_ask",base=base,alt=alt)
		def get_highest_bid(self,base,alt):
				return Vircurex.simpleRequest("get_highest_bid",base=base,alt=alt)
		def get_last_trade(self,base,alt):
				return Vircurex.simpleRequest("get_last_trade",base=base,alt=alt)
		def get_volume(self,base,alt):
				return Vircurex.simpleRequest("get_volume",base=base,alt=alt)
		def get_info_for_currency(self):
				return Vircurex.simpleRequest("get_info_for_currency")
		def get_info_for_1_currency(self,base,alt):
				return Vircurex.simpleRequest("get_info_for_1_currency",base=base,alt=alt)
		def orderbook(self,base,alt):
				return Vircurex.simpleRequest("orderbook",base=base,alt=alt)
		def orderbook_alt(self,alt):
				return Vircurex.simpleRequest("orderbook_alt",alt=alt)
		def trades(self,base,alt,since):
				return Vircurex.simpleRequest("trades",base=base,alt=alt,since=since)
		def get_currency_info(self):
				return Vircurex.simpleRequest("get_currency_info")

def ShotgunSecrets(secret):
	secrets = {}
	secrets['get_balance'] = secret
	secrets['create_order'] = secret
	secrets['release_order'] = secret
	secrets['delete_order'] = secret
	secrets['read_order'] = secret
	secrets['read_orders'] = secret
	secrets['read_orderexecution'] = secret
	secrets['create_coupon'] = secret
	secrets['redeem_coupon'] = secret
	return secrets

def PlaceOrders(exchange, type, currency, segments, price, satoshis, increments):
	if type == "buy":
		print("\nPlacing %d Buy Orders:" % satoshis)
	else:
		print("\nPlacing %d Sell Orders:" % satoshis)
	count = 0
	total_qty = 0.00
	average_price = 0.00
	for i in range(satoshis):
		if type == "buy":
			qty = segments / price				
		else:
			qty = segments
		str = "\nOrder: %s %.8f %s @ %.8f btc..." % (type.capitalize(), qty, currency, price)
		total_qty += qty
		average_price += price
		sys.stdout.write(str)
		response = exchange.create_order(type, qty, currency, price, "btc")
		if response['status'] == 0:
			response = exchange.release_order(response['orderid'])
			if response['status'] == 0:
				sys.stdout.write("Order Released")
				count += 1
			else:
				print "Order failed to release: %s" % response['statustext']
		else:
			print "Order failed to open: %s" % response['statustext']
		if type == "buy":
			price += float(increments/100000000.0)
		else:
			price -= float(increments/100000000.0)
	print("\n%s Orders Complete: %d orders placed." % (type.capitalize(), count))
	if count != 0:
		if type == "buy":
			print("%.8f %s requested @ %.8f average btc" % (total_qty, currency, average_price/count))
		else:
			print("%.8f %s submitted @ %.8f average btc (%.8f btc total)" % (total_qty, currency, average_price/count, total_qty*average_price/count))
			