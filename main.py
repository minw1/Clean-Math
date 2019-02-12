import pygame
import pygame.freetype
import math
import numpy as np
import json
 
# Initialize the game engine
pygame.init()

FONT = pygame.freetype.Font("Futura.ttf", 24)

digits = ["0","1","2","3","4","5","6","7","8","9"]

 
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
SELECTED_CELL_COLOR = (37,122,253)

width = 400
height = 300

boxSideLength = 20
boxStrokeWidth = 1


celldimensions = [math.ceil(float(width)/20),math.ceil(float(height)/20)]#the current dimensions of the cell grid




selectedcell = {'x':0,"y":0}#dictionary representing the currently selected cell




#dictionary for storing what symbols have text in them
#the key is actually the string representation of a dictionary which holds the cell coordinates (in the format of selectedcell)
#(you can't use pure dictionaries as keys)
# i use json's dumps() function to turn dicts to strings, which is nice because i can use json's loads() function to turn the strings right back into dicts
#the value is a string representing the digit in the cell represented by the key.
symbolcontainer = {}


# Set the height and width of the screen
size = [width, height]
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

pygame.display.set_caption("Math Grid")
 
 
#Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
 
while not done:
 
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)

    celldimensions = [math.ceil(float(width)/20),math.ceil(float(height)/20)]
     
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)
            width = event.w
            height = event.h
        if event.type == pygame.KEYDOWN:

            #on keyboard arrow inputs, adjust the coordinates of the selected cell as needed

            if event.key == pygame.K_LEFT:
                if (selectedcell['x'] > 0):
                    selectedcell['x']-=1
            if event.key == pygame.K_RIGHT:
                selectedcell['x']+=1
            if event.key == pygame.K_UP:
                if (selectedcell['y'] > 0):
                    selectedcell['y']-=1
            if event.key == pygame.K_DOWN:
                selectedcell['y']+=1

            else:#if a key is entered
                if pygame.key.name(event.key) in digits:# which is one of the digits
                    symbolcontainer[json.dumps(selectedcell)] = pygame.key.name(event.key) #put it in the symbolcontainer
                    selectedcell['x']+=1 #so that the selected cell moves right with each data entry
            #it's going to get hairy with plus symbols etc. because they use key modifiers (shift and equals, for example)


                
 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the screen and set the screen background
    screen.fill(WHITE)

    #color in the selected cell
    selRect = pygame.Rect(boxSideLength*selectedcell['x'],boxSideLength*selectedcell['y'],boxSideLength,boxSideLength)
    screen.fill(SELECTED_CELL_COLOR,selRect)


    #draw vertical lines
    vertLineOrigin = 0

    
    while(vertLineOrigin < width):
          pygame.draw.line(screen, BLACK, [vertLineOrigin, 0], [vertLineOrigin,height],boxStrokeWidth)
          vertLineOrigin += boxSideLength

    #use same process to draw horizontal lines
    horLineOrigin = 0
    while(horLineOrigin < height):
          pygame.draw.line(screen, BLACK, [0, horLineOrigin], [width,horLineOrigin],boxStrokeWidth)
          horLineOrigin += boxSideLength


    #draw the dimensions
    #the render function returns a surface(basically an image) into the text variable, and a rectange object for that into rect
    #the rect variable is not used
 
    text,rect = FONT.render("CELL DIMENSIONS: ({},{})".format(celldimensions[0],celldimensions[1]),WHITE,BLACK)

    #for some reason, you can't set the alpha on a surface created with pygame freetype, 
    #so I have to copy it to a buffer and then set the alpha 
    buffersurface = pygame.Surface([rect.width,rect.height])
    buffersurface.blit(text,(0,0)) #blit copies from text to buffersurface
    buffersurface.set_alpha(50)
    screen.blit(buffersurface,(0,0))#and blit then copies from buffersurface to the real screen


    for key, value in symbolcontainer.items():  #here, we look through each entry in our symbol containser
        keydict = json.loads(key)  
        text, rect = FONT.render(value,BLACK)   #create a surface
        scaled = pygame.transform.scale(text,(boxSideLength,boxSideLength))# stretch it into our box size
        screen.blit(text,(keydict['x']*boxSideLength,keydict['y']*boxSideLength)) #then blit it onto the screen (it is important this comes) before we paint the cell SELECTED_CELL_COLOR, other wise, it would paint over the number


    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
