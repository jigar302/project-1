# !/usr/bin/env python3

# STUDENT version for Project 1.
# TPRG2131 Fall 202x
# Updated Phil J (Fall 202x)
# 
# Louis Bertrand
# Oct 4, 2021 - initial version
# Nov 17, 2022 - Updated for Fall 2022.
# Jigar Jeet Singh Hundal
# Student id: 100891267

# PySimpleGUI recipes used:
#
# Persistent GUI example
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2a-persistent-window-multiple-reads-using-an-event-loop
#
# Asynchronous Window With Periodic Update
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#asynchronous-window-with-periodic-update


import PySimpleGUI as sg




hardware_present = False
try:
    from gpiozero import Button             #Uncomment this for working on pi.
    key1 = Button(5)
    from gpiozero import Button, Servo
    from time import sleep
    servo = Servo(17)
    servo.detach()
    
    hardware_present = True
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")

TESTING = True

def log(s):
    if TESTING:
        print(s)

class VendingMachine(object): # Class representing vending machine products and coins.
    PRODUCTS = {"Chocolate": ("Chocolate", 5),
                "Chips": ("Chips", 10),
                "Drink": ("Drink", 50),
                "Sweets": ("Sweets", 200),
                "Gum": ("Gum", 250),
                }

    COINS = {"5cents": ("Nickel", 5),
             "10cents": ("Dime", 10),
             "25cents": ("Quarter", 25),
             "$1": ("Loonie", 100),
             "$2": ("Toonie", 200),
            }

    def __init__(self): #Vending machine properties
        self.state = None
        self.states = {}
        self.event = ""
        self.amount = 0
        self.change_due = 0
        values = []
        for k in self.COINS:
            values.append(self.COINS[k][1])
        self.coin_values = sorted(values, reverse=True)
        log(str(self.coin_values))

    def add_state(self, state): #Add state define
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.on_exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.on_entry(self)

    def update(self):
        if self.state:
            self.state.update(self)

    def add_coin(self, coin): #Adding the coin.
        self.amount += self.COINS[coin][1]

    def button_action(self): #Action of button.
        self.event = 'RETURN'
        self.update()

class State(object):
    _NAME = ""
    def __init__(self):
        pass
    @property
    def name(self):
        return self._NAME
    def on_entry(self, machine):
        pass
    def on_exit(self, machine):
        pass
    def update(self, machine):
        pass

class WaitingState(State): #In this state machine waits for the first coin
    _NAME = "waiting"
    def update(self, machine):
        if machine.event in machine.COINS:
            machine.add_coin(machine.event)
            machine.go_to_state('add_coins')

class AddCoinsState(State): #In this machine adds the coin.
    _NAME = "add_coins"
    def update(self, machine):
        if machine.event == "RETURN":
            machine.change_due = machine.amount
            machine.amount = 0
            machine.go_to_state('count_change')
        elif machine.event in machine.COINS:
            machine.add_coin(machine.event)
        elif machine.event in machine.PRODUCTS:
            if machine.amount >= machine.PRODUCTS[machine.event][1]: #Servo is defined with its function.
                machine.go_to_state('deliver_product')
                servo.value = 1                #Uncomment this for working on pi.
                sleep(0.5)
                servo.value= -1
                sleep(0.5)
                servo.detach()           


        else:
            pass

class DeliverProductState(State): #Deliver products and change state.
    _NAME = "deliver_product"
    def on_entry(self, machine):
        machine.change_due = machine.amount - machine.PRODUCTS[machine.event][1]
        machine.amount = 0
        print("Buzz... Whir... Click...", machine.PRODUCTS[machine.event][0])
        if machine.change_due > 0:
            machine.go_to_state('count_change')
        else:
            machine.go_to_state('waiting')

class CountChangeState(State): #Count the change in coins.
    _NAME = "count_change"
    def on_entry(self, machine):
        print("Change due: $%0.2f" % (machine.change_due / 100))
        log("Returning change: " + str(machine.change_due))
    def update(self, machine):
        for coin_index in range(0, 5):
            while machine.change_due >= machine.coin_values[coin_index]:
                print("Returning %d" % machine.coin_values[coin_index])
                machine.change_due -= machine.coin_values[coin_index]
        if machine.change_due == 0:
            machine.go_to_state('waiting')

if __name__ == "__main__": #Main program for machine.
    sg.theme('red')

    coin_col = []
    coin_col.append([sg.Text("ENTER COINS", font=("Helvetica", 20))])  
    for item in VendingMachine.COINS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 12))
        row = [button]
        coin_col.append(row)

    select_col = []
    select_col.append([sg.Text("SELECT ITEM", font=("Helvetica", 20))])
    for item in VendingMachine.PRODUCTS:
        log(item)
        button = sg.Button(item, font=("Helvetica", 12))
        row = [button]
        select_col.append(row)

    layout = [ [sg.Column(coin_col, vertical_alignment="TOP"),
                     sg.VSeparator(),
                     sg.Column(select_col, vertical_alignment="TOP")
                    ] ]
    layout.append([sg.Button("RETURN", font=("Helvetica", 12))])
    window = sg.Window('Vending Machine', layout)

    vending = VendingMachine()

    vending.add_state(WaitingState())
    vending.add_state(AddCoinsState())
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())

    vending.go_to_state('waiting')
    
    if hardware_present:
        key1.when_pressed = vending.button_action

    while True:
        event, values = window.read(timeout=10)
        if event != '__TIMEOUT__':
            log((event, values))
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        vending.event = event
        vending.update()

    window.close()
    print("Shutting Down") #Print shutting down on close.
