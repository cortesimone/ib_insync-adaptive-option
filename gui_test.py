import tkinter as tk


#####################################
#
# SETTINGS

settings = {
    "entry_money_value": 1000,
    "entry_loss_value": 0.90,
    "entry_gain_value": 1.20
    }



######################################
#
# FUNCTIONS

def update_var(name,value):
    settings[name] = value
    entry_money.delete(0,tk.END)
    entry_money.insert(0, settings["entry_money_value"])
    entry_loss.delete(0,tk.END)
    entry_loss.insert(0, settings["entry_loss_value"])
    entry_gain.delete(0,tk.END)
    entry_gain.insert(0, settings["entry_gain_value"])
  




window = tk.Tk()
window.title("StopLoss - TakeProfit")

window.rowconfigure(3, minsize=100, weight=1)
window.columnconfigure(0, minsize=100, weight=1)

#frame 0, titolo
###################################################
frm_title = tk.Frame(window, relief=tk.RAISED, bd=2)
label_title = tk.Label(frm_title, text="StopLoss - TakeProfit", font=('Arial',24))

label_title.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)



#frame 1, pulsanti put e call
###################################################
frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
btn_open = tk.Button(frm_buttons, width=10, text="PUT", font=('Arial',32), bg='#ED8787') # rosso
btn_save = tk.Button(frm_buttons, width=10, text="CALL", font=('Arial',32), bg='#83CC89') # verde

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=0, column=1, sticky="ew", padx=5, pady=5)


#frame 2, finestra testuale x info
###################################################
frm_info = tk.Frame(window, relief=tk.RAISED, bd=2)
label_info = tk.Label(frm_info, text="Informazioni:",font=('Arial',12))
txt_info = tk.Text(frm_info)

label_info.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
txt_info.grid(row=1, column=1, sticky="ew", padx=5, pady=5)



#frame 3, parametri di acquisto
###################################################
frm_params = tk.Frame(window, relief=tk.RAISED, bd=2)
label_money = tk.Label(frm_params, text="Investimento max per operazione $:", font=('Arial',12))# 1000 2000 5000 6000
entry_money = tk.Entry(frm_params)
entry_money.insert(0, settings["entry_money_value"])
btn_mo1000 = tk.Button(frm_params, text="1000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",1000)) 
btn_mo2000 = tk.Button(frm_params, text="2000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",2000)) 
btn_mo5000 = tk.Button(frm_params, text="5000", font=('Arial',14), command=lambda *args: update_var("entry_money_value",5000))
btn_mo7500 = tk.Button(frm_params, text="7500", font=('Arial',14), command=lambda *args: update_var("entry_money_value",7500)) 

label_loss = tk.Label(frm_params, text="Percentuale stoploss %:", font=('Arial',12)) #0,90 0,95 ecc
entry_loss = tk.Entry(frm_params)
entry_loss.insert(0, settings["entry_loss_value"])
btn_lo088 = tk.Button(frm_params, text="0.88%", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.88))
btn_lo090 = tk.Button(frm_params, text="0.90%", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.90))
btn_lo092 = tk.Button(frm_params, text="0.92%", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.92))
btn_lo095 = tk.Button(frm_params, text="0.95%", font=('Arial',14), command=lambda *args: update_var("entry_loss_value",0.95))

label_gain = tk.Label(frm_params, text="Percentuale takeprofit %:", font=('Arial',12)) # 1,05 1,10 1,15 ecc
entry_gain = tk.Entry(frm_params)
entry_gain.insert(0, settings["entry_gain_value"])
btn_ga118 = tk.Button(frm_params, text="1.18%", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.18))
btn_ga120 = tk.Button(frm_params, text="1.20%", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.20))
btn_ga122 = tk.Button(frm_params, text="1.22%", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.22))
btn_ga125 = tk.Button(frm_params, text="1.25%", font=('Arial',14), command=lambda *args: update_var("entry_gain_value",1.25))

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



#inserimento frame nella finestra
##############################################
frm_title.grid(row=0, column=0, sticky="nsew")
frm_params.grid(row=3, column=0, sticky="nsew")
frm_buttons.grid(row=1, column=0, sticky="ns")
frm_info.grid(row=2, column=0, sticky="nsew")



window.mainloop()
