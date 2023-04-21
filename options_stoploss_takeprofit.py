import random
from ib_insync import *
import time
import math
import pprint
import pandas_market_calendars as mcal
import datetime as dt
import pytz
import sys

n = len(sys.argv)

if(n > 1):
    print()
else:
    print("No direction has been specified, exiting...")
    quit()


if(str(sys.argv[1]) == "CALL"):
    direction = "C"
else:
    if(str(sys.argv[1]) == "PUT"):
        direction = "P"
    else:
        print("P lease specify if you want to buy CALL or PUT.")
        quit()
    
print(f"Yous selected to buy {direction} contracts.")

# define parameters
ticker = 'TSLA'
dollar_amount = 1000
stop_price = 0.9  # 10% below purchase price
limit_price = 1.2  # 20% above purchase price

# Initialize Pretty Print
pp = pprint.PrettyPrinter(indent=4, compact=True)

#####################################################################
# define functions
#####################################################################

# this function checks if we are within a given timerange, if we are not we exit the program
def is_time_in_range(start_time_str, end_time_str):
    # Create timezone object for New York
    ny_tz = pytz.timezone('America/New_York')

    # Parse start and end times
    start_time = dt.datetime.strptime(start_time_str, '%H:%M').time()
    end_time = dt.datetime.strptime(end_time_str, '%H:%M').time()

    # Get current time in New York timezone
    now = dt.datetime.now(ny_tz).time()

    # Check if current time is within the range
    if start_time <= now <= end_time:
        return True
    else:
        return False

# checks if the market calendar shows today as a day where the market is open
def can_we_trade():
    nyse = mcal.get_calendar('NYSE')
    today = dt.date.today()
    schedule = nyse.schedule(start_date=today, end_date=today)

    if len(schedule) == 0:
        print('Market is closed')
        return False
    else:
        market_open = schedule.iloc[0]['market_open'].strftime('%Y-%m-%d %H:%M:%S')
        print(f'Market is open. Market opens at {market_open}.')
        if is_time_in_range('09:30', '15:00'):
            print('Current time is within range')
            return True
        else:
            print('Current time is not within range')
            return False
        return True


# Define the handler function for errors
def error_handler(reqId, errorCode, errorString, contract):
    if errorCode == 200 and 'No security definition' in errorString:
        print('Error: Could not find contract for current strike')

def order_status(trade):
    if trade.orderStatus.status == 'Filled':
        fill = trade.fills[-1]        
        print(f'{fill.time} - {fill.execution.side} {fill.contract.symbol} {fill.execution.shares} @ {fill.execution.avgPrice}')

#############################################################################à

# add a new funcion and callback to handle last available price
# https://www.elitetrader.com/et/threads/not-possible-to-request-bid-ask-of-an-option-spread-using-ib-api.341968/

# if we are within a time window and today is a market day, then we continue, otherwise, we quit()
if can_we_trade():
    print("We can continue")
else:
    print("We cannot continue")
    quit()

# Establish connection to IB API
ib = IB()

# Sometimes connection is lost not reusable, so we make it pseudo random
RandomId = random.randint(1,10)

ib.connect('127.0.0.1', 7497, RandomId)

# Add the error handler callback to the app
ib.errorEvent += error_handler


# Request market data for AAPL
contract = Stock('TSLA', 'SMART', 'USD')

# set markt data to LIVE
#ib.marketDataType(1)
#print(ib.marketDataType(1))

ticker = ib.reqMktData(contract, '', True, False)
details = ib.reqContractDetails(contract)[0]

# Determine the price so we can calculate the correct strike price for the call option
underlying_current_price = ticker.marketPrice()

print("Security ID (conId):", details.contract.conId)
print("Ticker:", details.contract.symbol) 
print("Price:", underlying_current_price)

# Get the option chain for the underlying stock
chain = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, details.contract.conId)

available_strikes = ""
available_strikes_list = []

if (direction == "C"):
    print("Looking for suitable CALLs")
    for i in range(len(chain)):
        if chain[i].exchange == "SMART":
            SMART_chain_index = i
            for j in range(len(chain[i].strikes)):
                if chain[i].strikes[j] > underlying_current_price and chain[i].strikes[j] < underlying_current_price * 1.03:
                    available_strikes = available_strikes + ", " + str(chain[i].strikes[j])
                    available_strikes_list.append(chain[i].strikes[j])
    print(f"Available strikes (above current trading price): {available_strikes[2:]}.")

if (direction == "P"):
    print("Looking for suitable PUTs")
    for i in range(len(chain)):
        if chain[i].exchange == "SMART":
            SMART_chain_index = i
            for j in range(len(chain[i].strikes)):
                if underlying_current_price * 0.97 < chain[i].strikes[j] < underlying_current_price:
                    available_strikes = available_strikes + ", " + str(chain[i].strikes[j])
                    available_strikes_list.append(chain[i].strikes[j])
    available_strikes_list.reverse()
    print(f"Available strikes (below current trading price): {available_strikes[2:]}.")

nearest_expiry_date = sorted(exp for exp in chain[SMART_chain_index].expirations)[0]
print("Nearest expiry date:", nearest_expiry_date)

# we use this to check if we are already trading with a given strike price or not
we_are_in_a_trade = False

for strike in available_strikes_list:
    print ("Elaboro strike:", strike)
    option_contract=Option('TSLA', nearest_expiry_date, strike, direction, 'SMART')
    try:
        oc = ib.qualifyContracts(option_contract)
    except:
        oc = []
        
    if (oc):
        break

tickers = ib.reqTickers(oc[0])


midpoint = round((tickers[0].bid + tickers[0].ask)/2, 2)
print(f"Bid: {tickers[0].bid} Ask: {tickers[0].ask} Midpoint: {midpoint}")

option_contract_price = midpoint

options_quantity = math.floor(dollar_amount / (option_contract_price * 100))
take_profit_price = round(option_contract_price * limit_price,2)
stop_loss_price = round(option_contract_price * stop_price,2)

bracket_order = ib.bracketOrder('BUY', options_quantity, limitPrice=option_contract_price, takeProfitPrice=take_profit_price, stopLossPrice=stop_loss_price)

for ord in bracket_order:
    trade = ib.placeOrder(option_contract, ord)
    ord.usePriceMgmtAlgo = True
    ib.sleep(1)
    trade.filledEvent+= order_status

# Print information about the new trade
print(f"New trade entered:")
print(f" * Price: {option_contract_price}")
print(f" * Strike: {strike}")
print(f" * Contracts: {options_quantity}")
print(f" * Direction: {direction}")

we_are_in_a_trade = True
        
# Disconnect from the IB API
ib.disconnect()
