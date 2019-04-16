import pygame
import pygame.freetype
import settings as st
import math
import numpy as np
import json
import string
import panel as pnl
import os
import random
import gridOps as go
import time
from copy import deepcopy
from settings import selectedcell
#import expression as xp

# Initialize the game engine
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)

FONT = st.FONT
iFONT = st.iFONT
KEYPRESS_TOLERANCE = 0.25


sounds = []
for i in range(1,st.numSounds + 1):
    sounds += [pygame.mixer.Sound(st.audio_locator(str(i) + ".ogg"))]


exitmsg, rexitmsg = FONT.render("Please use the console to exit.", st.RED,st.WHITE)
showmExitMsg = False

allowed_symbols = ["0","1","2","3","4","5","6","7","8","9","+","-","=","*","/","^","(",")","."]+list(string.ascii_lowercase)

width = 400
height = 300



currentcell = {'x':0,"y":0}#dictionary representing the cell the cursor is currently in

currentlyScrolling = False

scrollLocation = [0,0]
pixelsToGrid = [width,height] #keeps track of the farthest pixel locations that need to be loaded
#in the loop, this will be calculated with
#[width+scrollLocation[0], height + scrollLocation[1]]


# Set the height and width of the screen
size = [width, height]

clipboard = {}
copyOrigin = {}


screen = pygame.display.set_mode(size, pygame.RESIZABLE)

pygame.display.set_caption("Clean Math")
 

clock = pygame.time.Clock()
currentTime = time.clock()
timeLeft = 0
timeRight = 0
timeUp = 0
timeDown = 0

#this is starting the thread that controls the command line controls
panelthread = pnl.PanelThread("panel 1")
panelthread.start()


isHighlighting = False
#[[minX, minY],[maxX,maxY]]
highlightedRegion = [[None,None],[None,None]]

 
while st.programIsRunning:
    FONT = st.FONT
    iFONT = st.iFONT

    currentlyScrolling = False
 
    st.lock.acquire()

    # This limits the while loop to a max of 20 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(20)
    currentTime = time.clock()
    keys = pygame.key.get_pressed();#returns dict with keys, pygame keys and values as bools if pressed


    pixelsToGrid[0]= width+scrollLocation[0]
    pixelsToGrid[1]= height+scrollLocation[1]


    intermediate_scrollblock = pygame.Surface((pixelsToGrid[0],pixelsToGrid[1]))
    #this surface is what everything is painted on. Then, we paint it onto the screen so that it shows a location relative to the  scrolllocation

    (x,y) = pygame.mouse.get_pos()
    currentcell['x']= math.floor((x + scrollLocation[0])/st.boxSideLength)
    currentcell['y']= math.floor((y + scrollLocation[1])/st.boxSideLength)
    
    for event in pygame.event.get(): # User did something


        contOrCommand = (keys[310] or pygame.key.get_mods() & pygame.KMOD_LCTRL)

        if event.type == pygame.QUIT: # If user clicked close
        	showmExitMsg = True
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h
        if event.type == pygame.KEYDOWN:#if a key is entered        
            if event.key == pygame.K_BACKSPACE:

                if not isHighlighting:
                    if (selectedcell['x'] > 0 and json.dumps(selectedcell) not in st.symbolcontainer):
                        selectedcell['x']-=1
                    st.symbolcontainer.pop(json.dumps(selectedcell),None)
                else:
                    j = list(st.symbolcontainer.keys())#don't want to delete from the dict as we're accessing from it, so lets take the keys
                    for key in j:
                        unpack = json.loads(key)
                        if unpack['x'] >= highlightedRegion[0][0] and unpack['x'] <= highlightedRegion[0][1] and unpack['y'] >= highlightedRegion[1][0] and unpack['y'] <= highlightedRegion[1][1]:
                            st.symbolcontainer.pop(key)


            elif event.key == pygame.K_SPACE:
                selectedcell['x']+=1

            elif event.key == pygame.K_c and contOrCommand:#command or control keys
                clipboard = {}
                if isHighlighting:
                    copyOrigin = {'x':highlightedRegion[0][0],'y':highlightedRegion[1][0]}
                    for x in range(highlightedRegion[0][0],highlightedRegion[0][1]+1):
                        for y in range(highlightedRegion[1][0],highlightedRegion[1][1]+1):
                            key=json.dumps({"x":x,"y":y})
                            if key in st.symbolcontainer:
                                clipboard[key]=st.symbolcontainer[key]
                            else:
                                clipboard[key]=None
                else:
                    copyOrigin=deepcopy(currentcell)
                    key=json.dumps(currentcell)
                    if key in st.symbolcontainer:
                        clipboard[key]=st.symbolcontainer[key]
                    else:
                        clipboard[key]=None



            elif event.key == pygame.K_x and contOrCommand:#command or control keys
                clipboard = {}
                if isHighlighting:
                    copyOrigin = {'x':highlightedRegion[0][0],'y':highlightedRegion[1][0]}
                    for x in range(highlightedRegion[0][0],highlightedRegion[0][1]+1):
                        for y in range(highlightedRegion[1][0],highlightedRegion[1][1]+1):
                            key=json.dumps({"x":x,"y":y})
                            if key in st.symbolcontainer:
                                clipboard[key]=st.symbolcontainer[key]
                            else:
                                clipboard[key]=None
                    j = list(st.symbolcontainer.keys())#don't want to delete from the dict as we're accessing from it, so lets take the keys
                    for key in j:
                        unpack = json.loads(key)
                        if unpack['x'] >= highlightedRegion[0][0] and unpack['x'] <= highlightedRegion[0][1] and unpack['y'] >= highlightedRegion[1][0] and unpack['y'] <= highlightedRegion[1][1]:
                            st.symbolcontainer.pop(key)
                else:
                    copyOrigin=deepcopy(currentcell)
                    key=json.dumps(currentcell)
                    if key in st.symbolcontainer:
                        clipboard[key]=st.symbolcontainer[key]
                        st.symbolcontainer.pop(key)
                    else:
                        clipboard[key]=None


            elif event.key == pygame.K_v and (keys[310] or pygame.key.get_mods() & pygame.KMOD_LCTRL):#command or control keys
                for key,value in clipboard.items():
                    toReplace = json.loads(key)
                    toReplace['x'] += selectedcell['x'] - copyOrigin['x']
                    toReplace['y'] += selectedcell['y'] - copyOrigin['y']
                    formattedPlace = json.dumps(toReplace)
                    if value is not None:
                        st.symbolcontainer[formattedPlace] = value
                    elif formattedPlace in st.symbolcontainer:
                        st.symbolcontainer.pop(formattedPlace)




            elif event.unicode in allowed_symbols:# which is one of the digits
                isHighlighting = False
                st.symbolcontainer[json.dumps(selectedcell)] = event.unicode #put it in the symbolcontainer
                selectedcell['x']+=1 #so that the selected cell moves right with each data entry
                if st.calmingMode:
                    sounds[event.key % st.numSounds].play()
                if event.unicode == "=" and contOrCommand:
                    try:
                        go.printExpression(xp.simpleWAQuery(go.getString(go.goToExpressionStart(json.dumps(selectedcell)))), json.dumps(selectedcell))
                    except:
                        go.printExpression("error",json.dumps(selectedcell))
            elif event.key == pygame.K_LEFT:
                timeLeft = currentTime
                if (selectedcell['x'] > 0):
                    selectedcell['x']-=1
                    isHighlighting = False
            elif event.key == pygame.K_RIGHT:
                timeRight = currentTime
                selectedcell['x']+=1
                isHighlighting = False
            elif event.key == pygame.K_UP:
                timeUp = currentTime
                if (selectedcell['y'] > 0):
                    selectedcell['y']-=1
                    isHighlighting = False
            elif event.key == pygame.K_DOWN:
                timeDown = currentTime
                selectedcell['y']+=1
                isHighlighting = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            selectedcell['x'] = currentcell['x']
            selectedcell['y'] = currentcell['y']
            isHighlighting = False
            highlightedRegion=[[None,None],[None,None]]

            if event.button==4:
                scrollLocation[1] = max(scrollLocation[1]-7,0)
            if event.button==5:
                scrollLocation[1] += 7


    #use keys to navigate selected cell
    #the reason these aren't in the event loop is that we want them to be able to be held, and for the function to be able to be copied each frame
    #in the event loop, for example, the space bar must be tapped twice to get two spaces.
    if keys[pygame.K_LEFT] and (currentTime-timeLeft>KEYPRESS_TOLERANCE):
        if (selectedcell['x'] > 0):
            selectedcell['x']-=1
            isHighlighting = False
    if keys[pygame.K_RIGHT] and (currentTime-timeRight>KEYPRESS_TOLERANCE):
        selectedcell['x']+=1
        isHighlighting = False
    if keys[pygame.K_UP] and (currentTime-timeUp>KEYPRESS_TOLERANCE):
        if (selectedcell['y'] > 0):
            selectedcell['y']-=1
            isHighlighting = False
    if keys[pygame.K_DOWN] and (currentTime-timeDown>KEYPRESS_TOLERANCE):
        selectedcell['y']+=1
        isHighlighting = False

    
    (mousePX, mousePY) = pygame.mouse.get_pos()

    #adjusting the scroll corner depeneding on user's mouse location.
    if mousePX < 30 and mousePX > 0:
        scrollLocation[0] = max(scrollLocation[0]-7,0)
        currentlyScrolling = not scrollLocation[0] == 0
    if mousePX > width-30 and mousePX  < width-1:
        scrollLocation[0] += 7
        currentlyScrolling = True
    if mousePY < 30 and mousePY > 0:
        currentlyScrolling = not scrollLocation[1] == 0
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


    if selectedcell['x']*st.boxSideLength < scrollLocation[0] + 3*st.boxSideLength:
        if currentlyScrolling:
            selectedcell['x']+=1
        else:
            if scrollLocation[0]<st.boxSideLength:
                scrollLocation[0] = 0
            else:
                scrollLocation[0] -= st.boxSideLength

    if selectedcell['y']*st.boxSideLength < scrollLocation[1] + 3*st.boxSideLength:
        if currentlyScrolling:
            selectedcell['y']+=1
        else:
            if scrollLocation[1]<st.boxSideLength:
                scrollLocation[1]=0
            else:
                scrollLocation[1] -= st.boxSideLength


 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the scrollblock and set the background
    intermediate_scrollblock.fill(st.backgroundColor)

    #color in the selected cell

    selRect = pygame.Rect(st.boxSideLength*selectedcell['x'],st.boxSideLength*selectedcell['y'],st.boxSideLength,st.boxSideLength)
    if (selectedcell != currentcell and pygame.mouse.get_pressed()[0]):
        isHighlighting = True
        minCellX = min(selectedcell['x'],currentcell['x'])
        minCellY = min(selectedcell['y'],currentcell['y'])
        maxCellX = max(selectedcell['x'],currentcell['x'])
        maxCellY = max(selectedcell['y'],currentcell['y'])
        highlightedRegion = [[minCellX,maxCellX],[minCellY,maxCellY]]

    if isHighlighting:
        minCellX,maxCellX=highlightedRegion[0]
        minCellY,maxCellY=highlightedRegion[1]
        highlightRect = pygame.Rect(st.boxSideLength*minCellX,st.boxSideLength*minCellY,st.boxSideLength*(maxCellX-minCellX+1),st.boxSideLength*(maxCellY-minCellY+1))
        intermediate_scrollblock.fill(st.HIGHLIGHTED_CELL_COLOR,highlightRect)
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
