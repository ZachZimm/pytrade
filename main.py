import chart.py
import pytrade.py
# I want to refactor the analysis out of pytrade so that I have a write-only module that listens for data and records to csv (hopefully with a shorter date and just one of them)
# and a read-write module that does analysis 
import account.py

# Do I need to implement them as objects?
# I should probably add a kill function to each 'module'

# pytrade (or whatever I name that module) should probably emit some sort of event on every new candle

if __name__ == 'main':
    chart.run() # ?
    pytrade.run() 
    account.run()

    while True: # Will having an infinte loop here wreck performance?
    keyboard_input = input("Enter Command:\n")
        if(keyboard_input == restart_chart) # How do I want to do commands? Should I just replace/duplicate the existing command interface?
            chart.kill()
            chart.run()
        if(keyboard_input == restart_pytrade)
            pytrade.kill() # Figure out how to get the scheduler to run at the right point
            pytrade.run()
        if(keyboard_input == restart_account)
            account.kill()
            account.run()