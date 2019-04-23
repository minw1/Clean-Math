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

text=''
index=0

import psutil

Surface=None
 
while st.programIsRunning:
    clock.tick(20)
    st.lock.acquire()
    keys = pygame.key.get_pressed();#returns dict with keys, pygame keys and values as bools if pressed
    for event in pygame.event.get(): # User did something

        if event.type == pygame.QUIT: # If user clicked close 
            pygame.quit()
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h
        if event.type == pygame.KEYDOWN:#if a key is entered        
            if event.key == pygame.K_BACKSPACE and index>0:
                text=text[:index-1]+text[index:]
                index-=1
            elif event.key == pygame.K_SPACE:
                text=text[:index]+' '+text[index:]
                index+=1
            elif event.unicode == "(":
                text=text[:index]+'()'+text[index:]
                index+=2
            elif event.unicode != ")" and event.unicode in allowed_symbols:# which is one of the digits
                text=text[:index]+event.unicode+text[index:]
                index+=1
            elif event.key == pygame.K_LEFT:
                index=max(index-1,0)
            elif event.key == pygame.K_RIGHT:
                index=min(index+1,len(text))
        if event.type == pygame.MOUSEBUTTONDOWN and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            posx, posy = pygame.mouse.get_pos()
            x,y=posx-100,posy-100
            if Surface is not None:
                expres = Surface.get_at_position((x,y))
                print('exp high is', expres)
            
    string = text[:index]+'|'+text[index:]
    expression = pprs.get_exp(string)
    Surface = xts.smartSurface(expression)
    screen.fill((255,255,255))
    screen.blit(Surface.surface,(100,100))
    
    
    
    st.lock.release()


    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
