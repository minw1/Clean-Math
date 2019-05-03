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
import re

def process_shadow_parens(input_str):
    output_str = input_str
    #Remove superfluous shadow parens and close unclosed parentheses (with shadow parens)
    # Find shadow-paren edges of string
    l_idx = 0
    l_add = True
    while l_add:
        if l_idx + 1 > len(output_str):
            l_add = False
        elif output_str[l_idx] == '\u2985':
            l_idx += 1
        else:
            l_add = False

    r_idx = len(output_str)-1
    r_add = True
    while r_add:
        if r_idx - 1 < l_idx:
            r_add = False
        elif output_str[r_idx] == '\u2986':
            r_idx -= 1
        else:
            r_add = False

    print("Left Index: " + str(l_idx) + "\nRight Index: " + str(r_idx))
    # Turn shadow parens contained within the string (and not adjacent to parens) into actual parens
    for i in range(l_idx, r_idx+1):
        if output_str[i] == '\u2985':
            replace = True
            if i != r_idx and output_str[i+1] == '(':
                replace = False
            elif i != l_idx and output_str[i-1] == '(':
                replace = False
            if replace:
                output_str = output_str[:i] + '(' + output_str[i+1:]
        elif output_str[i] == '\u2986':
            replace = True
            if i != r_idx and output_str[i+1] == ')':
                replace = False
            elif i != l_idx and output_str[i-1] == ')':
                replace = False
            if replace:
                output_str = output_str[:i] + ')' + output_str[i+1:]

    # Refresh shadow parens, maintaining cursor position
    c_dist = (None, 0)
    if '|' in output_str[:l_idx]:
        c_dist = ('L', output_str[:l_idx].index('|'))
    elif '|' in output_str[r_idx+1:]:
        c_dist = ('R', len(output_str)-1 - output_str.index('|'))
    
    output_str = output_str[l_idx:r_idx+1]
    #  Remove shadow parens
    output_str = output_str.replace('\u2985', '').replace('\u2986', '')
    #  Figure out how many new shadow parens to add
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
    # Add new shadow parens
    output_str = extr_lprns * "\u2985" + output_str + "\u2986" * extr_rprns
    # Add cursor back in
    if c_dist[0] == 'L':
        output_str = output_str[:c_dist[1]] + '|' + output_str[c_dist[1]:]
    elif c_dist[0] == 'R':
        output_str = output_str[:len(output_str)-c_dist[1]] + '|' + output_str[len(output_str)-c_dist[1]:]
    
    return output_str

def process_string(input_str):
    output_str = input_str
    #Remove illegal characters
    illegal_chars = ['!', '@', '#', '$', '%', '&', '_', '\\', ':', ';', '\"', '\'', '?', '>', '<', ',', '=']
    str_idx = 0
    while str_idx < len(output_str):
        if output_str[str_idx] in illegal_chars:
            output_str = output_str[:str_idx] + output_str[str_idx+1:]
        else:
            str_idx += 1

    #Replace multiplication operators with unicode version
    output_str = output_str.replace('*', '\u00B7')

    #Process shadow parens
    output_str = process_shadow_parens(output_str)
    #Insert implicit multiplication
    output_str = re.sub('(?<=\w|\))(?=\|?\()|(?<=\))(?=\|?\w)|(?<=\d|[a-zA-Z])(?=\|?[a-zA-Z])|(?<=[a-zA-Z])(?=\|?\d)', '*', output_str)

    #Add brackets for division operands

    #Edit cursor index
    index = output_str.index("|")
    return (output_str, index)
	

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
    print("----------")
    print(string + " -- " + text + " -- " + str(index))
    string_and_index = process_string(string)
    string = string_and_index[0]
    index = string_and_index[1]
    text = re.sub('\|', '', string)
    print(string + " -- " + text + " -- " + str(index))
    print("----------")
    expression = pprs.get_exp(string)
    expression.assign_parents()
    Surface = xts.smartSurface(expression)
    screen.fill((255,255,255))
    #pygame.draw.rect(screen,st.ORANGE,selectedRectangle)


    selRectInEQSpace = selectedRectangle.move(-100,-100)
    rselect = Surface.selectFromRect(selRectInEQSpace)

    for hb in Surface.hitboxes:
        [irect,orect], expression, op_depth = hb
        if expression == rselect:
            pygame.draw.rect(screen,st.ORANGE,orect.move(100,100))

    screen.blit(Surface.surface,(100,100))

    
    st.lock.release()


    selectedRectangle.x = min(firstTap[0],secondTap[0])
    selectedRectangle.y = min(firstTap[1],secondTap[1])
    selectedRectangle.w = abs(firstTap[0]-secondTap[0])
    selectedRectangle.h = abs(firstTap[1]-secondTap[1])


    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.

    

    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
