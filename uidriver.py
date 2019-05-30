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
import saver

pygame.init()


width = 800
height = 600
size = [width, height]
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
scrollblock = pygame.Surface((10000,10000))


pygame.display.set_caption("Clean Math")
clock = pygame.time.Clock()
currentTime = time.clock()



xscroll = 0
yscroll = 0
scrollspeed = 5

getting_input_flag = 0
filename = ""
prompt = None



DEFAULT_FONT = pygame.freetype.Font(None,24)


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
    contOrCommand = (pygame.key.get_pressed()[310] or pygame.key.get_mods() & pygame.KMOD_LCTRL)

    for event in events: # User did something
        ##SYSTEM EVENTS##

        if event.type == pygame.QUIT: # If user clicked close
            pygame.quit()
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            width = event.w
            height = event.h

        if event.type == pygame.KEYDOWN:
            if getting_input_flag == 0:
                if contOrCommand:
                    if event.unicode == "s":
                        getting_input_flag = 1
                    if event.unicode == "o":
                        getting_input_flag = 2

            elif getting_input_flag>0:
                if event.key == pygame.K_BACKSPACE:
                    if not filename == "":
                        filename = filename [:-1]
                elif event.key == pygame.K_RETURN:
                    if getting_input_flag == 1:
                        saver.saveCM(filename,ui.uiMaster,ui.uiEquation)
                    if getting_input_flag == 2:
                        saver.openCM(filename,ui.uiMaster,ui.uiEquation)
                    getting_input_flag = 0
                else:
                    filename += event.unicode






    if mousePos[0] > (width-20):
        xscroll += scrollspeed
    if mousePos[0] < (20):
        xscroll -= scrollspeed
    if mousePos[1] > (height-20):
        yscroll += scrollspeed
    if mousePos[1] < (20):
        yscroll -= scrollspeed




    '''
    for ui in uiList:
        ui.handle_events(events,mousePos)
    '''
    if not getting_input_flag:
        ui.uiMaster.handle_events(events,(mousePos[0]+xscroll,mousePos[1]+yscroll))

    screen.fill((255,255,255))
    scrollblock.fill((255,255,255))


    

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
    if not getting_input_flag:
        ui.uiMaster.draw(scrollblock)
        screen.blit(scrollblock, (-xscroll,-yscroll))


    if getting_input_flag ==1:
        prompt = DEFAULT_FONT.render("What would you like to save your file as?",(0,0,255))[0]

    if getting_input_flag == 2:
        prompt = DEFAULT_FONT.render("What is the name of the file you would like to open?",(0,0,255))[0]

    if getting_input_flag>0:
        textf = DEFAULT_FONT.render(filename,(0,0,255))[0]

        screen.blit(prompt,(100,100))
        screen.blit(textf,(100,150))
 


    


    st.lock.release()
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
