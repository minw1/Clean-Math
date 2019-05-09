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
import processString as proc


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


class uiExpression: #static methods operate on the whole list of created uiExpressions
	allUiExpressions = []

	def __init__(self,topleft):
		self.text = ""
		self.index = 0
		self.exp = xp.NoOpExpression("")
		self.surf = xts.smartSurface(self.exp)
		self.rect = pygame.Rect(topleft,(self.surf.get_rect().w, self.surf.get_rect().h))
		self.is_active = False
		uiExpression.allUiExpressions += [self]

	def update(self):
		if self.is_active:
			curstring = self.text[:self.index]+'|'+self.text[self.index:]
		else:
			curstring = self.text
		print("cur:" + curstring)

		finalstring = proc.process_string(curstring)[0]

		self.exp = pprs.get_exp(finalstring)
		self.exp.assign_parents()
		self.surf = xts.smartSurface(self.exp)
		self.rect.size = self.surf.get_rect().size

		#must happen after this frame is drawn-- so that cursor is still there to be replaced next frame
		self.text = finalstring.replace("|","")
		self.index = proc.process_string(curstring)[1]

	def static_update():
		for ui in uiExpression.allUiExpressions:
			ui.update()

	def draw(self,screen):
		screen.blit(self.surf.surface,self.rect.topleft)

	def static_draw(screen):
		for ui in uiExpression.allUiExpressions:
			ui.draw(screen)

	def feed_mousedown(self,mouse_absolute):#returns if this ui expression was selected by the click
		mouse_rel = (mouse_absolute[0]-self.rect.topleft[0],mouse_absolute[1]-self.rect.topleft[1])
		if not self.rect.collidepoint(mouse_absolute):
			self.is_active = False
			return False


		xtstr.clearCursor(self.exp)
		smallestDist = 99999999999999999
		smallestExp = None
		xcoorCenter = -1
		for hb in self.surf.hitboxes:
			[irect,orect], hbExp, op_depth = hb

			acceptable_hitbox = (type(hbExp) == xp.NoOpExpression)
			''' this cannot be implemented yet
			if type(hbExp) == xp.Expression:
				if hbExp.op.strRep == "/":
					acceptable_hitbox = True
			'''

			if acceptable_hitbox:
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
		return True

	def static_feed_mousedown(mouse_absolute):
		for ui in uiExpression.allUiExpressions:
			ui.feed_mousedown(mouse_absolute)

	def feed_mouseup(self, mouse_absolute):
		mouse_rel = (mouse_absolute[0]-self.rect.topleft[0],mouse_absolute[1]-self.rect.topleft[1])

	def static_feed_mouseup(mouse_absolute):
		return False


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

	def static_feed_keydown(keydown):
		for ui in uiExpression.allUiExpressions:
			ui.feed_keydown(keydown)

	def feedAllowedSymbol(self, symbol):
		self.text=self.text[:self.index]+symbol+self.text[self.index:]
		self.index+=1

	def static_feedAllowedSymbol(symbol):
		for ui in uiExpression.allUiExpressions:
			ui.feed_AllowedSymbol(symbol)

	def handle_events(self, events, mouse_absolute):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.feed_mousedown(mouse_absolute)
			if event.type == pygame.KEYDOWN and self.is_active:
				if event.unicode in allowed_symbols:
					self.feedAllowedSymbol(event.unicode)
				else:
					self.feed_keydown(event.key)

	def static_handle_events(events,mouse_absolute):
		for ui in uiExpression.allUiExpressions:
			ui.handle_events(events,mouse_absolute)

class uiEquation:
	def __init__(self,leftside,rightside):
		self.leftside = leftside
		self.rightside = rightside



