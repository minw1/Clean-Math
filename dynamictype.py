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
import expression as xp
import expToSurface as xts
import plyParser as pprs
import expToStr as xtstr
import re

def process_string(input_str):
    output_str = input_str
    #Remove illegal characters
    illegal_chars = ['!', '@', '#', '$', '%', '&', '_', '\\', ':', ';', '\"', '\'', '?', '>', '<', ',', '=']
    idx = 0
    while idx < len(output_str):
        if output_str[idx] in illegal_chars:
            output_str = output_str[:idx] + output_str[idx+1:]
        else:
            idx += 1

    #Replace multiplication operators with unicode version
    output_str = output_str.replace('*', '\u00B7')

    #Insert implicit multiplication
    output_str = re.sub('(?<=\w|\))(?=\|?\()|(?<=\))(?=\|?\w)|(?<=\d|[a-zA-Z])(?=\|?[a-zA-Z])|(?<=[a-zA-Z])(?=\|?\d)', '*', output_str)
	
   #Close unclosed parentheses (with shadow parens)
    extr_lprns = 0
    extr_rprns = 0
    for i in range(0, len(output_str)):
        if output_str[i] == "(":
            extr_rprns += 1
        elif output_str[i] == ")":
            if extr_rprns > 0:
                extr_rprns -= 1
            else:
                extr_lprns += 1
    output_str = extr_lprns*"\u2985" + output_str + "\u2986"*extr_rprns
	
    #Add brackets for division operands
	
    return output_str


# Initialize the game engine
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)

FONT = st.FONT
iFONT = st.iFONT
KEYPRESS_TOLERANCE = 0.25

expression = None


exitmsg, rexitmsg = FONT.render("Please use the console to exit.", st.RED,st.WHITE)
showmExitMsg = False

allowed_symbols = ["0","1","2","3","4","5","6","7","8","9","+","-","=","*","/","^","(",")","."]+list(string.ascii_lowercase)+list(string.ascii_uppercase)

width = 400
height = 300



# Set the height and width of the screen
size = [width, height]


selectedRectangle = pygame.Rect(0,0,0,0)
firstTap = (-1,-1)
secondTap = (-1,-1)


screen = pygame.display.set_mode(size, pygame.RESIZABLE)

pygame.display.set_caption("Clean Math")
 
rselect = None

clock = pygame.time.Clock()
currentTime = time.clock()
timeLeft = 0
timeRight = 0
timeUp = 0
timeDown = 0

text=''
index=0

import psutil

Surface=None

def sandwich(A,B):#is A inclusively between (B1,B2)?
    maxi = max(B[0],B[1])
    mini = min(B[0],B[1])
    return A>=mini and A<=maxi



def distPointRect(point,rect): #squared distance of point and rectangle. We don't need the real distance to compare distance sizes.
    (X,Y) = point
    (A,B) = rect.topleft
    (W,Z) = rect.bottomright

    xoffset = 0
    yoffset = 0

    if not sandwich(X,(A,W)):
        xoffset = min(abs(X-A),abs(X-W))
    if not sandwich(Y,(B,Z)):
        xoffset = min(abs(Y-B),abs(Y-Z))

    return (xoffset**2 + yoffset**2)




 
while st.programIsRunning:
    clock.tick(20)
    st.lock.acquire()



    keys = pygame.key.get_pressed();#returns dict with keys, pygame keys and values as bools if pressed
    (mousePX, mousePY) = pygame.mouse.get_pos()
    (button1,button2,button3) = pygame.mouse.get_pressed()

    for event in pygame.event.get(): # User did something
        ##SYSTEM EVENTS##
        if event.type == pygame.QUIT: # If user clicked close
            pygame.quit()
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h
        ##MOUSE EVENTS##
        if event.type == pygame.MOUSEBUTTONDOWN:
            firstTap = (mousePX, mousePY)
            secondTap = (mousePX,mousePY)
        if event.type == pygame.MOUSEMOTION and button1:
            secondTap = (mousePX, mousePY)
        if event.type == pygame.MOUSEBUTTONUP:
            if(selectedRectangle.size == (0,0)):
                #a click to move the cursor
                xtstr.clearCursor(expression)
                smallestDist = 99999999999999999
                smallestExp = None
                xcoorCenter = -1


                for hb in Surface.hitboxes:
                    [irect,orect], expression, op_depth = hb
                    if type(expression) == xp.NoOpExpression:
                        dpr = distPointRect((mousePX-100,mousePY-100),irect)
                        if dpr < smallestDist:
                            smallestDist = dpr
                            smallestExp = expression
                            xcoorCenter = irect.centerx

                if not smallestExp == None:
                    smallestExp.cursor = True
                    if mousePX-100 < xcoorCenter:
                        smallestExp.cursor_idx = 0
                    else:
                        smallestExp.cursor_idx = 1

                text = xtstr.expToStr(expression)
                index = text.index("|")
                text = text.replace("|","")




                rselect = None

            firstTap = (-1,-1)
            secondTap = (-1,-1)

        ##KEY EVENTS
        if event.type == pygame.KEYDOWN:#if a key is entered        
            if event.key == pygame.K_BACKSPACE and index>0:
                text=text[:index-1]+text[index:]
                index-=1
            elif event.key == pygame.K_SPACE:
                text=text[:index]+' '+text[index:]
                index+=1
            elif event.unicode in allowed_symbols:# which is one of the digits
                text=text[:index]+event.unicode+text[index:]
                index+=1
            elif event.key == pygame.K_LEFT:
                index=max(index-1,0)
            elif event.key == pygame.K_RIGHT:
                index=min(index+1,len(text))
        if event.type == pygame.MOUSEBUTTONDOWN and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            x,y=mousePX-100,mousePY-100
            if Surface is not None:
                expres = Surface.get_at_position((x,y))
                print('exp high is', expres)

            




    string = text[:index]+'|'+text[index:]
    string = process_string(string)

    expression = pprs.get_exp(string)
    expression.assign_parents()
    Surface = xts.smartSurface(expression)
    screen.fill((255,255,255))
    #pygame.draw.rect(screen,st.ORANGE,selectedRectangle)


    selectedRectangle.x = min(firstTap[0],secondTap[0])
    selectedRectangle.y = min(firstTap[1],secondTap[1])
    selectedRectangle.w = abs(firstTap[0]-secondTap[0])
    selectedRectangle.h = abs(firstTap[1]-secondTap[1])


    if(selectedRectangle.size == (0,0)):
        selectedRectangle.x = -1
        selectedRectangle.y = -1


    if (not firstTap == (-1,-1)) and (not secondTap == (-1,-1)):
        selRectInEQSpace = selectedRectangle.move(-100,-100)
        rselect = Surface.selectFromRect(selRectInEQSpace)


    for hb in Surface.hitboxes:
        [irect,orect], expression, op_depth = hb
        if xp.compare_exp(expression,rselect):
            pygame.draw.rect(screen,st.ORANGE,orect.move(100,100))

    screen.blit(Surface.surface,(100,100))
    print(string)

    
    st.lock.release()

 

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.

    

    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
