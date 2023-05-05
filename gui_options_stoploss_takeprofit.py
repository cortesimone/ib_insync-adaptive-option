import random
from ib_insync import *
import time
import math
import pandas_market_calendars as mcal
import datetime as dt
import pytz
import sys
import tkinter as tk

#####################################
#
# SETTINGS

settings = {
    "stocks": ["TSLA", "GOOGL"],
    "selected_stock": "TSLA",
    "entry_money_value": 1000,
    "entry_loss_value": 0.90,
    "entry_gain_value": 1.20,
    "in_trade_put": False,
    "in_trade_call": False,
    }

######################################
#
# FUNCTIONS

def update_var(name,value):
    # aggiorna i settings in base alla pressione dei pulsanti
    global settings
    
    settings[name] = value
    entry_money.delete(0,tk.END)
    entry_money.insert(0, settings["entry_money_value"])
    entry_loss.delete(0,tk.END)
    entry_loss.insert(0, settings["entry_loss_value"])
    entry_gain.delete(0,tk.END)
    entry_gain.insert(0, settings["entry_gain_value"])
  
 

def insert_txt_info(message, color="black"):
    #insert a message in the txt_info widget
    global txt_info
    
    txt_info.config(state='normal')
    begin = txt_info.index(tk.INSERT)
    txt_info.insert(tk.END,message)
    end = txt_info.index(tk.INSERT)
        
    if color=="red":
        txt_info.tag_add("red", begin, end)
        
    if color=="green":
        txt_info.tag_add("green", begin, end)
      
    txt_info.insert(tk.END, "\n")
    txt_info.config(state='disabled')
 
 
 
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
        insert_txt_info('Market is closed','red')
        return False
    else:
        market_open = schedule.iloc[0]['market_open'].strftime('%Y-%m-%d %H:%M:%S')
        insert_txt_info(f'Market is open. Market opens at {market_open}.')
        if is_time_in_range('09:30', '15:00'):
            insert_txt_info('Current time is within range')
            return True
        else:
            insert_txt_info('Current time is not within range')
            return False
        return True

 
 
# Define the handler function for errors
def error_handler(reqId, errorCode, errorString, contract):
    if errorCode == 200 and 'No security definition' in errorString:
        insert_txt_info('Error: Could not find contract for current strike')

 
def order_status(trade):
    if trade.orderStatus.status == 'Filled':
        fill = trade.fills[-1]        
        insert_txt_info(f'{fill.time} - {fill.execution.side} {fill.contract.symbol} {fill.execution.shares} @ {fill.execution.avgPrice}')


ib = IB()
 
def connect_api():
    # Establish connection to IB API
    global ib, btn_title, btn_call, btn_put
    
    # Sometimes connection is lost not reusable, so we make it pseudo random
    RandomId = random.randint(1,10)

    ib.connect('127.0.0.1', 7497, RandomId)

    # Add the error handler callback to the app
    ib.errorEvent += error_handler
    

    #connection OK
    btn_conn.configure(text="connected", bg="OrangeRed3", fg= "white")
    insert_txt_info('OK: Connected to API', "green")
            
    

    global displ_market_status
    # verify if we can trade
    displ_market_status.config(state='normal')
    if can_we_trade():
        #set indicator "Market OPEN"
        displ_market_status.config(text="OPEN")
        displ_market_status.config(bg="dark green")
        btn_put.config( bg='#ED8787')
        btn_put.config( state='active', command=lambda *args: callback_button_put_call('P'))
        btn_call.config(bg='#83CC89')
        btn_call.config( state='active', command=lambda *args: callback_button_put_call('C'))
        
    else:
        # set indicator "Market CLOSE"
        displ_market_status.config(text="CLOSED")
        displ_market_status.config(bg="dark red")
        #disable buttons PUT and CALL
        btn_put.config(state='disabled')
        btn_call.config(state='disabled')
        
    displ_market_status.config(state='disabled')    
    
    
    
    #check ordini precedenti
    ib.client.reqAllOpenOrders()
    dummy = ib.reqOpenOrders()  # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
      
    trades_iniziali = ib.openTrades()
    if trades_iniziali:
        print("Ci sono trades:")
        for t in trades_iniziali:
            if t.contract.right == 'C': # disabilita CALL
                btn_call.config(state='disabled')
                insert_txt_info("C'è già una CALL che gira", "green")
                
            if t.contract.right == 'P': # disabilita PUT    
                btn_put.config(state='disabled')
                insert_txt_info("C'è già una PUT che gira", "green")
              
    
    
 
 
 
 
def disconnect_api():
    # Disconnect from the IB API
    global ib
    ib.disconnect()




def callback_dropdown(*args):
    # chiamato dal dropdown menu 
    global settings, displ_selected_stock
    
    settings["selected_stock"] = drop_menu_value.get()
    displ_selected_stock.config(state='normal')
    displ_selected_stock.config(text=settings["selected_stock"], state='disabled')
    insert_txt_info(f"Codice stock cambiato in  '{drop_menu_value.get()}'")



def callback_button_put_call(direction):
    #chiamato dai bottoni PUT o CALL
    
    if (direction == "P" and ('settings[settings["selected_stock"]]["in_trade_put"]' in globals()) and settings[settings["selected_stock"]]["in_trade_put"]):
        insert_txt_info("Already in a PUT. Stop!", "red")
        return 1
        
    if (direction == "C" and ('settings[settings["selected_stock"]]["in_trade_call"]' in globals()) and settings[settings["selected_stock"]]["in_trade_call"]):
        insert_txt_info("Already in a CALL. Stop!", "red")
        return 1
    
    
    
              
    # Request market data for the chosen stock
    contract = Stock(settings["selected_stock"], 'SMART', 'USD')
    
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

    for strike in available_strikes_list:
        print ("Elaboro strike:", strike)
        option_contract=Option(settings["selected_stock"], nearest_expiry_date, strike, direction, 'SMART')
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

    options_quantity = math.floor(settings["entry_money_value"] / (option_contract_price * 100))
    take_profit_price = round(option_contract_price * settings["entry_gain_value"],2)    
    stop_loss_price = round(option_contract_price * settings["entry_loss_value"],2)

    bracket_order = ib.bracketOrder('BUY', options_quantity, limitPrice=option_contract_price, takeProfitPrice=take_profit_price, stopLossPrice=stop_loss_price)

    for ord in bracket_order:
        trade = ib.placeOrder(option_contract, ord)
        ord.usePriceMgmtAlgo = True
        ib.sleep(1)
        trade.filledEvent+= order_status

    # Print information about the new trade
    print(trade)
    print("---------------------")
    print(f"New trade entered:")
    print(f" * Price: {option_contract_price}")
    print(f" * Strike: {strike}")
    print(f" * Contracts: {options_quantity}")
    print(f" * Direction: {direction}")

    # se la variabile non esiste
    if not ('settings[settings["selected_stock"]]' in vars()) and not ('settings[settings["selected_stock"]]' in globals()):
        settings[settings["selected_stock"]]={}
    
    if (direction == "P"):
        settings[settings["selected_stock"]]['in_trade_put'] = True
        settings[settings["selected_stock"]]['put_order']=trade
        btn_put.config(state='disabled')
        print(trade)

    if (direction == "C"):
        settings[settings["selected_stock"]]["in_trade_call"] = True
        settings[settings["selected_stock"]]["call_order"]=trade
        btn_call.config(state='disabled')
        print(trade)
        
##############################################################################################################

###### WINDOW CREATION

window = tk.Tk()
window.title("StopLoss - TakeProfit")

window.rowconfigure(3, minsize=100, weight=1)
window.columnconfigure(1, minsize=100, weight=1)


###########################
# frame 00   | frame 01
#--------------------------
# frame 10   | frame 11
#--------------------------
# frame 20   | frame 21
#--------------------------
# frame 30   | frame 31
#--------------------------





#frame 00, titolo 
###################################################
frm_title = tk.Frame(window, relief=tk.RAISED, bd=2)
label_title = tk.Label(frm_title, text="StopLoss - TakeProfit", font=('Arial',24))

label_title.grid(row=0, column=0, sticky="nw", padx=25, pady=5)


#frame 01, pulsante connessione
###################################################
frm_conn = tk.Frame(window, relief=tk.RAISED,bd=2)
btn_conn = tk.Button(frm_conn, height=1, width=9, text="connect", font=('Arial',18), bg='#9999cc', command=lambda *args: connect_api() ) 

btn_conn.grid(row=0, column=0, padx=5, pady=5)


#frame 10, pulsanti put e call
###################################################
frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
drop_label = tk.Label(frm_buttons, text="Codice stock:", font=('Arial',12))
drop_menu_value = tk.StringVar()
drop_menu_value.set(settings["stocks"][0])
drop_menu_value.trace("w",callback_dropdown )

drop_stock = tk.OptionMenu(frm_buttons, drop_menu_value, *settings["stocks"])
btn_put = tk.Button(frm_buttons, width=10, text="PUT", font=('Arial',32),  state='disabled') # rosso
btn_call = tk.Button(frm_buttons, width=10, text="CALL", font=('Arial',32), state='disabled') # verde

drop_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
drop_stock.grid(row=0, column=1, sticky="w", padx=5, pady=5)
btn_put.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_call.grid(row=1, column=1, sticky="ew", padx=5, pady=5)


#frame 11, vuoto
###################################################
frm_empty11 = tk.Frame(window, relief=tk.RAISED, bd=2)


#frame 20, finestra testuale x info
###################################################
frm_info = tk.Frame(window, relief=tk.RAISED, bd=2)
label_info = tk.Label(frm_info, text="Informazioni:",font=('Courier',10))
txt_info = tk.Text(frm_info)
txt_info.tag_config("green", foreground="dark green")
txt_info.tag_config("red", foreground="red")
insert_txt_info("Starting....")


label_info.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
txt_info.grid(row=1, column=1, sticky="ew", padx=5, pady=5)


#frame 21, indicatori read only
###################################################
frm_leds = tk.Frame(window, relief=tk.RAISED, bd=2)
label_leds = tk.Label(frm_leds, text="CURRENT STATUS", font=('Arial',10))

label_market_status = tk.Label(frm_leds, text="Market status", font=('Arial',10))
displ_market_status = tk.Label(frm_leds, text="---", bg="#000", fg="#fff", width=7, font=('Courier',10), state='disabled')
label_selected_stock = tk.Label(frm_leds, text="Selected stock", font=('Arial',10))
displ_selected_stock = tk.Label(frm_leds, text=settings["selected_stock"], bg="#000", fg="#fff", width=7, font=('Courier',10), state='disabled')

label_leds.grid(row=0, column=0, sticky="e", padx=2, pady=12)
label_market_status.grid(row=2, column=0, sticky="w", padx=2, pady=2)
displ_market_status.grid(row=2, column=1, sticky="e", padx=2, pady=2)
label_selected_stock.grid(row=3, column=0, sticky="w", padx=2, pady=2)
displ_selected_stock.grid(row=3, column=1, sticky="e", padx=2, pady=2)


#frame 30, parametri di acquisto
###################################################
frm_params = tk.Frame(window, relief=tk.RAISED, bd=2)
label_money = tk.Label(frm_params, text="Investimento max per operazione $:", font=('Arial',12))# 1000 2000 5000 6000
entry_money = tk.Entry(frm_params)
entry_money.insert(0, settings["entry_money_value"])
btn_mo1000 = tk.Button(frm_params, text="1000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",1000)) 
btn_mo2000 = tk.Button(frm_params, text="2000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",2000)) 
btn_mo5000 = tk.Button(frm_params, text="5000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",5000))
btn_mo7500 = tk.Button(frm_params, text="7500", font=('Arial',14), command=lambda *args: update_var("entry_money_value",7500)) 

label_loss = tk.Label(frm_params, text="Moltiplicatore stoploss:", font=('Arial',12)) #0,90 0,95 ecc
entry_loss = tk.Entry(frm_params)
entry_loss.insert(0, settings["entry_loss_value"])
btn_lo088 = tk.Button(frm_params, text="0.88", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.88))
btn_lo090 = tk.Button(frm_params, text="0.90", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.90))
btn_lo092 = tk.Button(frm_params, text="0.92", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.92))
btn_lo095 = tk.Button(frm_params, text="0.95", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.95))

label_gain = tk.Label(frm_params, text="Moltiplicatore takeprofit:", font=('Arial',12)) # 1,05 1,10 1,15 ecc
entry_gain = tk.Entry(frm_params)
entry_gain.insert(0, settings["entry_gain_value"])
btn_ga118 = tk.Button(frm_params, text="1.18", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.18))
btn_ga120 = tk.Button(frm_params, text="1.20", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.20))
btn_ga122 = tk.Button(frm_params, text="1.22", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.22))
btn_ga125 = tk.Button(frm_params, text="1.25", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.25))

label_money.grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_money.grid(row=0, column=1, sticky="e", padx=5, pady=5)
btn_mo1000.grid(row=0, column=2, sticky="ew", padx=10, pady=5)
btn_mo2000.grid(row=0, column=3, sticky="ew", padx=10, pady=5)
btn_mo5000.grid(row=0, column=4, sticky="ew", padx=10, pady=5)
btn_mo7500.grid(row=0, column=5, sticky="ew", padx=10, pady=5)

label_loss.grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_loss.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
btn_lo088.grid(row=1, column=2, sticky="ew", padx=10, pady=5)
btn_lo090.grid(row=1, column=3, sticky="ew", padx=10, pady=5)
btn_lo092.grid(row=1, column=4, sticky="ew", padx=10, pady=5)
btn_lo095.grid(row=1, column=5, sticky="ew", padx=10, pady=5)

label_gain.grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_gain.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
btn_ga118.grid(row=2, column=2, sticky="ew", padx=10, pady=5)
btn_ga120.grid(row=2, column=3, sticky="ew", padx=10, pady=5)
btn_ga122.grid(row=2, column=4, sticky="ew", padx=10, pady=5)
btn_ga125.grid(row=2, column=5, sticky="ew", padx=10, pady=5)


#frame 31, vuoto
###################################################
frm_empty31 = tk.Frame(window, relief=tk.RAISED, bd=2)


#inserimento frame nella finestra
##############################################
frm_title.grid(row=0, column=0, sticky="nsew")
frm_conn.grid(row=0, column=1, sticky="ew")
frm_buttons.grid(row=1, column=0, sticky="")
frm_empty11.grid(row=1, column=1, sticky="nsew")
frm_info.grid(row=2, column=0, sticky="nsew")
frm_leds.grid(row=2, column=1, sticky="nsew")
frm_params.grid(row=3, column=0, sticky="nsew")
frm_empty31.grid(row=3, column=1, sticky="nsew")

################  LOOP PRINCIPALE 

#window.mainloop()


while True:
    window.update()
    if ('settings[settings["selected_stock"]]' in globals()):

        ib.reqAllOpenOrders()
        print("Ci sono nuovi ordini")
        print(ib.reqAllOpenOrders())
        window.update()
        time.sleep(1)
        
        
#### controllo uscita

disconnect_api()
