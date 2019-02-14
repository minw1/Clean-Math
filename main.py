import pygame
import pygame.freetype
import settings as st
import math
import numpy as np
import json
import string
import panel as pnl
 
# Initialize the game engine
pygame.init()

#load the fonts
FONT = pygame.freetype.Font("tnr.ttf", 24)
iFONT = pygame.freetype.Font("tnri.ttf",24)

exitmsg, rexitmsg = FONT.render("Please use the console to exit.", st.RED,st.WHITE)
showmExitMsg = False


allowed_symbols = ["0","1","2","3","4","5","6","7","8","9","+","-","=","*","/","^","(",")","."]+list(string.ascii_lowercase)

width = 400
height = 300


selectedcell = {'x':0,"y":0}#dictionary representing the currently selected cell

currentlyScrolling = False

scrollLocation = [0,0]
pixelsToGrid = [400,300] #keeps track of the farthest pixel locations that need to be loaded
#in the loop, this will be calculated with
#[width+scrollLocation[0], height + scrollLocation[1]]


# Set the height and width of the screen
size = [width, height]


screen = pygame.display.set_mode(size, pygame.RESIZABLE)

pygame.display.set_caption("Clean Math")
 

clock = pygame.time.Clock()


#this is starting the thread that controls the command line controls
panelthread = pnl.PanelThread("panel 1")
panelthread.start()


 
while st.programIsRunning:

    currentlyScrolling = False
 
    st.lock.acquire()

    # This limits the while loop to a max of 20 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(20)
    keys = pygame.key.get_pressed();#returns dict with keys, pygame keys and values as bools if pressed


    pixelsToGrid[0]= width+scrollLocation[0]
    pixelsToGrid[1]= height+scrollLocation[1]


    intermediate_scrollblock = pygame.Surface((pixelsToGrid[0],pixelsToGrid[1]))
    #this surface is what everything is painted on. Then, we paint it onto the screen so that it shows a location relative to the  scrolllocation


    
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
        	showmExitMsg = True
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h
        if event.type == pygame.KEYDOWN:#if a key is entered
            if event.unicode in allowed_symbols:# which is one of the digits
                st.symbolcontainer[json.dumps(selectedcell)] = event.unicode #put it in the symbolcontainer
                selectedcell['x']+=1 #so that the selected cell moves right with each data entry
            if event.key == pygame.K_BACKSPACE:
                if (selectedcell['x'] > 0 and json.dumps(selectedcell) not in st.symbolcontainer):
                    selectedcell['x']-=1
                st.symbolcontainer.pop(json.dumps(selectedcell),None)


            if event.key == pygame.K_SPACE:
                selectedcell['x']+=1
        if event.type == pygame.MOUSEBUTTONDOWN:
            (x,y) = pygame.mouse.get_pos()

          

            selectedcell['x']= math.floor((x + scrollLocation[0])/st.boxSideLength)
            selectedcell['y']= math.floor((y + scrollLocation[1])/st.boxSideLength)



    #use keys to navigate selected cell
    #the reason these aren't in the event loop is that we want them to be able to be held, and for the function to be able to be copied each frame
    #in the event loop, for example, the space bar must be tapped twice to get two spaces. 

    if keys[pygame.K_LEFT]:
        if (selectedcell['x'] > 0):
            selectedcell['x']-=1
    if keys[pygame.K_RIGHT]:
        selectedcell['x']+=1
    if keys[pygame.K_UP]:
        if (selectedcell['y'] > 0):
            selectedcell['y']-=1
    if keys[pygame.K_DOWN]:
        selectedcell['y']+=1


    
    (mousePX, mousePY) = pygame.mouse.get_pos()

    #adjusting the scroll corner depeneding on user's mouse location.
    if mousePX < 30 and mousePX > 0:
        scrollLocation[0] = max(scrollLocation[0]-7,0)
        currentlyScrolling = True
    if mousePX > width-30 and mousePX  < width-1:
        scrollLocation[0] += 7
        currentlyScrolling = True
    if mousePY < 30 and mousePY > 0:
        currentlyScrolling = True
        scrollLocation[1] = max(scrollLocation[1]-7,0)
    if mousePY > height - 30 and mousePY < height-1:
        scrollLocation[1] += 7
        currentlyScrolling = True



    if selectedcell['x']*st.boxSideLength > pixelsToGrid[0] - 3*st.boxSideLength:
        if currentlyScrolling:
            selectedcell['x']-=1
        else:
            scrollLocation[0] += st.boxSideLength

    if selectedcell['y']*st.boxSideLength > pixelsToGrid[1] - 3*st.boxSideLength:
        if currentlyScrolling:
            selectedcell['y']-=1
        else:
            scrollLocation[1] += st.boxSideLength


 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the scrollblock and set the background
    intermediate_scrollblock.fill(st.backgroundColor)

    #color in the selected cell

    selRect = pygame.Rect(st.boxSideLength*selectedcell['x'],st.boxSideLength*selectedcell['y'],st.boxSideLength,st.boxSideLength)
    intermediate_scrollblock.fill(st.SELECTED_CELL_COLOR,selRect)


 
    if st.show_grid:
        #draw vertical lines
        vertLineOrigin = 0
        while(vertLineOrigin < pixelsToGrid[0]):
            pygame.draw.line(intermediate_scrollblock, st.boxStrokeColor, [vertLineOrigin, 0], [vertLineOrigin,pixelsToGrid[1]],st.boxStrokeWidth)
            vertLineOrigin += st.boxSideLength

        #use same process to draw horizontal lines
        horLineOrigin = 0
        while(horLineOrigin < pixelsToGrid[1]):
            pygame.draw.line(intermediate_scrollblock, st.boxStrokeColor, [0, horLineOrigin], [pixelsToGrid[0],horLineOrigin],st.boxStrokeWidth)
            horLineOrigin += st.boxSideLength



    for key, value in st.symbolcontainer.items():  #here, we look through each entry in our symbol container
        keydict = json.loads(key)
        if value in list(string.ascii_lowercase):
        	text, rect = iFONT.render(value,st.fontColor)   #create a surface with the character in italic font
        else:
        	text, rect = FONT.render(value,st.fontColor)   #create a surface with the character in normal font
        intermediate_scrollblock.blit(text,((keydict['x']+0.5)*st.boxSideLength - rect.width/2
            ,(keydict['y']+0.5)*st.boxSideLength - rect.height/2)) 

        #then blit it onto the scrollblock (it is important this comes) after we paint the cell SELECTED_CELL_COLOR, other wise, it would paint over the number
        #The reason I do all this stuff with adding a half a cell and then subtracting the rectangle width
        #is so that the center of the symbol is aligned with the center of the cell

    


    screen.blit(intermediate_scrollblock,(-scrollLocation[0],-scrollLocation[1]))#bop the scrollbox somewhere to the up-left of the actual screen

    if(showmExitMsg):
        screen.blit(exitmsg,(0,0)) #lets leave this message unscrollable

    st.lock.release()


    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
