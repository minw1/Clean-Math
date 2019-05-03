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

allowed_symbols = ["0","1","2","3","4","5","6","7","8","9","+","-","=","*","/","^","(",")","."]+list(string.ascii_lowercase)+list(string.ascii_uppercase)


class uiExpression:
	def __init__(self,topleft):
		self.text = ""
		self.index = 0
		self.exp = xp.NoOpExpression("")
		self.surf = xts.smartSurface(self.exp)
		self.rect = pygame.Rect(topleft,(self.surf.get_rect().w, self.surf.get_rect().h))
		self.is_active = False

	def update(self):
		if self.is_active:
			curstring = self.text[:self.index]+'|'+self.text[self.index:]
		else:
			curstring = self.text

		finalstring = process_string(curstring)
		self.exp = pprs.get_exp(finalstring)
		self.exp.assign_parents()
		self.surf = xts.smartSurface(self.exp)
		self.rect.size = self.surf.get_rect().size

	def draw(self,screen):
		screen.blit(self.surf.surface,self.rect.topleft)

	def feed_mousedown(self,mouse_absolute):
		mouse_rel = (mouse_absolute[0]-self.rect.topleft[0],mouse_absolute[1]-self.rect.topleft[1])
		if not self.rect.collidepoint(mouse_absolute):
			return False
		xtstr.clearCursor(self.exp)
		smallestDist = 99999999999999999
		smallestExp = None
		xcoorCenter = -1
		for hb in self.surf.hitboxes:
			[irect,orect], hbExp, op_depth = hb
			if type(hbExp) == xp.NoOpExpression:
				dpr = distPointRect(mouse_rel,irect)
				if dpr < smallestDist:
					smallestDist = dpr
					smallestExp = hbExp
					xcoorCenter = irect.centerx
		if not smallestExp == None:
			smallestExp.cursor = True
			if mouse_rel[0] < xcoorCenter:
				smallestExp.cursor_idx = 0
			else:
				smallestExp.cursor_idx = 1 #this needs to become more sophisticated later
		self.text = xtstr.expToStr(self.exp)
		self.index = self.text.index("|")
		self.text = self.text.replace("|","")
		self.is_active = True


	def feed_mouseup(self, mouse_absolute):
		mouse_rel = (mouse_absolute[0]-self.rect.topleft[0],mouse_absolute[1]-self.rect.topleft[1])

	def feed_keydown(self, keydown):
		if keydown == pygame.K_BACKSPACE and self.index>0:
			self.text = self.text[:self.index-1] + self.text[self.index:]
			self.index-=1
		elif keydown == pygame.K_SPACE:
			self.text = self.text[:self.index]+" "+self.text[self.index:]
			self.index+=1
		elif keydown == pygame.K_LEFT or keydown==pygame.K_UP:
			self.index=max(self.index-1,0)
		elif keydown == pygame.K_RIGHT or keydown==pygame.K_DOWN:
			self.index=min(self.index+1,len(self.text))
		else:
			return False #some other symbol

	def feedAllowedSymbol(self, symbol):
		self.text=self.text[:self.index]+symbol+self.text[self.index:]
		self.index+=1

	def handle_events(self, events, mouse_absolute):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.feed_mousedown(mouse_absolute)
			if event.type == pygame.KEYDOWN and self.is_active:
				if event.unicode in allowed_symbols:
					self.feedAllowedSymbol(event.unicode)
				else:
					self.feed_keydown(event.key)


