# Define the colors we will use in RGB format
import threading

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
SELECTED_CELL_COLOR = (37,122,253)

boxSideLength = 20
boxStrokeWidth = 1
boxStrokeColor = BLACK
fontColor = BLACK
show_dimensions = False
show_grid = False

lock = threading.RLock()
programIsRunning = True