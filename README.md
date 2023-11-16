# project-1
# Commit 1st
Line 21 to line 44 hold the gpio and servo working.
Line 45 to 59 is defining the class of vending machine with product and coins.
Line 61 to 71 vending machine properties.
Line 73 to 93 hold all the states of action like adding coin, waiting, button action, deliver product and return state.
# Working with Rasp Pi
With one pusbutton and servo motor. In the vending machine when product is deliver the servo motor make rotation back to forth and with using the push button, when pusbutto is pressed user gets return coins.
# Working of Vending Machine
This code simulates the vending machine PysimpleGUI and implements a state machine model for its functionality. The states used in this like waiting, adding_coins, delivery products, and counting change. Each state work differently in waiting it wait for coin to add, then in add_coins coins is added, then product is selected and delivery product deliver the product with its amount, then return state. return the coins with change. When close the window it close by print message shuuting down.
