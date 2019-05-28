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
import ui
import psutil

pygame.init()


width = 800
height = 600
size = [width, height]
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("Clean Math")
clock = pygame.time.Clock()
currentTime = time.clock()

'''
uiEq1 = ui.uiExpression((100,100))
uiEq1.is_active = True

uiList = [uiEq1]
'''

SHOW_HITBOXES = True

ui.uiMaster.init()

while st.programIsRunning:
    clock.tick(20)
    st.lock.acquire()



    keys = pygame.key.get_pressed() #returns dict with keys, pygame keys and values as bools if pressed
    mousePos = pygame.mouse.get_pos()
    (button1,button2,button3) = pygame.mouse.get_pressed()
    events = pygame.event.get()

    for event in events: # User did something
        ##SYSTEM EVENTS##

        if event.type == pygame.QUIT: # If user clicked close
            pygame.quit()
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h
    '''
    for ui in uiList:
        ui.handle_events(events,mousePos)
    '''
    ui.uiMaster.handle_events(events,mousePos)

    screen.fill((255,255,255))
    

    '''
    for ui in uiList:
        ui.update()
        ui.draw(screen)
        if SHOW_HITBOXES:
            for x in ui.surf.hitboxes:
                [irect,orect], hbExp, op_depth = x
                print(hbExp,irect)
                transrect = irect.move(ui.rect.topleft)
                pygame.draw.rect(screen,(255,0,0),transrect,1)
    '''
    ui.uiMaster.draw(screen)


    st.lock.release()
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
