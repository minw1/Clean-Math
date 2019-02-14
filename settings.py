# Define the colors we will use in RGB format
import threading

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
PURPLE = (138,43,226)
RED =   (255,   0,   0)
GRAY = (128,128,128)
ORANGE = (255,165,0)
SELECTED_CELL_COLOR = (37,122,253)

colorMap={"RED":RED, "BLUE":BLUE, "BLACK":BLACK, "GREEN":GREEN, "WHITE":WHITE,"PURPLE":PURPLE,"GRAY":GRAY,"GREY":GRAY,"ORANGE":ORANGE}

boxSideLength = 20
boxStrokeWidth = 1
boxStrokeColor = BLUE
backgroundColor = WHITE
fontColor = BLACK
show_grid = True

lock = threading.RLock()
programIsRunning = True


#dictionary for storing what symbols have text in them
#the key is actually the string representation of a dictionary which holds the cell coordinates (in the format of selectedcell)
#(you can't use pure dictionaries as keys)
# i use json's dumps() function to turn dicts to strings, which is nice because i can use json's loads() function to turn the strings right back into dicts
#the value is a string representing the digit in the cell represented by the key.
symbolcontainer = {}