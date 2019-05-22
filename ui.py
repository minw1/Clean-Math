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
import copy
from settings import selectedcell
import expression as xp
import expToSurface as xts
import plyParser as pprs
import expToStr as xtstr
import re
import processString as proc




MILLIS_SHOW = 200
#number of milliseconds for cursor to show
MILLIS_HIDE = 200

SHOW_INPUT_DELAY = 200
#how long after key input will the cursor show


def elemwiseAdd(a,b):
    return [sum(x) for x in zip(a,b)]


def sandwich(A,B):#is A inclusively between (B1,B2)?
    maxi = max(B[0],B[1])
    mini = min(B[0],B[1])
    return A>=mini and A<=maxi



def distPointRect(point,rect): #squared distance of point and rectangle. We don't need the real distance to compare distance sizes.
    if rect.collidepoint(point):
        return 0

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




def show_cursor():
    n=round(time.clock()*1000)
    return (n%(MILLIS_SHOW+MILLIS_HIDE)<MILLIS_SHOW) #or (time_since_input<200)



class uiExpression: #static methods operate on the whole list of created uiExpressions
    allUiExpressions = []
    last_input_time = 0
    time_since_input = 0

    def __init__(self,topleft):
        self.midleft = topleft
        self.text = ""
        self.index = 0
        self.exp = xp.NoOpExpression("")
        self.surf = xts.smartSurface(self.exp, cursor_show=show_cursor())
        self.rect = pygame.Rect((self.midleft[0], self.midleft[1]),(self.surf.get_rect().w, self.surf.get_rect().h))
        self.is_active = False
        uiExpression.allUiExpressions += [self]

    def update(self):
        uiExpression.time_since_input = (time.clock()-uiExpression.last_input_time)*1000


        if self.is_active:
            curstring = self.text[:self.index]+'|'+self.text[self.index:]
        else:
            curstring = self.text
        #print("cur:" + curstring)

        finalstring = proc.process_string(curstring)[0]

        self.exp = pprs.get_exp(finalstring)

        self.exp.assign_parents()
        self.surf = xts.smartSurface(self.exp, cursor_show= (show_cursor() or (uiExpression.time_since_input<200)))

        self.rect.size = self.surf.get_rect().size
        self.rect.topleft = self.midleft[0], self.midleft[1]-self.surf.y_mid

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
                smallestExp.cursor_idx = len(smallestExp.strRep)#this needs to become more sophisticated later
                        

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
                uiExpression.last_input_time = time.clock()

                if event.unicode in allowed_symbols:
                    self.feedAllowedSymbol(event.unicode)
                else:
                    self.feed_keydown(event.key)
            #if event.type == pygame.VIDEORESIZE:
            #	self.mult_by(xp.NoOpExpression("2"))


    def static_handle_events(events,mouse_absolute):
        for ui in uiExpression.allUiExpressions:
            ui.handle_events(events,mouse_absolute)

    def mult_by(self,factor):
        newexp = xp.Expression('\u00B7',[copy.copy(self.exp),factor])
        self.exp = newexp
        self.exp.assign_parents()
        self.text = xtstr.expToStr(self.exp)
        self.text = self.text.replace("|","")
    def add_to(self,toadd):
        newexp = xp.Expression('+',[copy.copy(self.exp),toadd])
        self.exp = newexp
        self.exp.assign_parents()
        self.text = xtstr.expToStr(self.exp)
        self.text = self.text.replace("|","")
    def sub_this_from(self,positive):
        newexp = xp.Expression('-',[positive,copy.copy(self.exp)])
        self.exp = newexp
        self.exp.assign_parents()
        self.text = xtstr.expToStr(self.exp)
        self.text = self.text.replace("|","")
    def sub_from_this(self,negative):
        newexp = xp.Expression('-',[copy.copy(self.exp),negative])
        self.exp = newexp
        self.exp.assign_parents()
        self.text = xtstr.expToStr(self.exp)
        self.text = self.text.replace("|","")
    def raise_to(self,ponent):
        newexp = xp.Expression('^',[copy.copy(self.exp),ponent])
        self.exp = newexp
        self.exp.assign_parents()
        self.text = xtstr.expToStr(self.exp)
        self.text = self.text.replace("|","")


    def find_all_adds(exp,pos):
        if type(exp) == xp.NoOpExpression:
            return [(exp,pos)]
        if exp.op == "+":
            return find_all_adds(exp.expList[0],pos) + find_all_adds(exp.expList[1],pos)
        elif exp.op == "-":
            return find_all_adds(exp.expList[0],pos) + find_all_adds(exp.expList[1],not pos)
        else:
            return [(exp,pos)]


    #def tidy_up_addition(self):





class uiEquation:
    alluiEquations = []
    def __init__(self,leftside,rightside,eqmid):
        self.leftside = leftside
        self.rightside = rightside
        self.eqmid = eqmid
        uiEquation.alluiEquations += [self]

    def draw(self,screen):
        self.leftside.update()
        self.rightside.update()
        surface, opLoc, (firstLoc,secondLoc) = xts.smartSurface.format_eq(self.leftside.surf,self.rightside.surf)
        self.leftside.midleft = elemwiseAdd(elemwiseAdd(firstLoc,self.eqmid),(-opLoc[0],0))
        self.rightside.midleft = elemwiseAdd(elemwiseAdd(secondLoc,self.eqmid),(-opLoc[0],0))
        
        print(surface.get_size(), self.leftside.surf.get_size(), self.rightside.surf.get_size())

        self.leftside.update()
        self.rightside.update()


        for x in self.leftside.surf.hitboxes:
                [irect,orect], hbExp, op_depth = x
                transrect = irect.move(self.leftside.midleft).move((0,-opLoc[1]))
                pygame.draw.rect(screen,(255,0,0),transrect,1)

        for x in self.rightside.surf.hitboxes:
                [irect,orect], hbExp, op_depth = x
                transrect = irect.move(self.rightside.midleft).move((0,-opLoc[1]))
                pygame.draw.rect(screen,(255,0,0),transrect,1)

        
        topleft = self.eqmid[0]-opLoc[0], self.eqmid[1]-opLoc[1]
        screen.blit(surface,topleft)

    def static_draw(screen):
        for uq in uiEquation.alluiEquations:
            uq.draw(screen)

    def handle_events(self,events,mouse_absolute):
        self.leftside.handle_events(events,mouse_absolute)
        self.rightside.handle_events(events,mouse_absolute)
    def static_handle_events(events,mouse_absolute):
        for uq in uiEquation.alluiEquations:
            uq.handle_events(events,mouse_absolute)

class uiMaster:
    typing_first_expression = True
    uiEq1 = uiExpression((100,100))
    
    def init():
        uiMaster.uiEq1.is_active = True

    def handle_events(events,mouse_absolute):
        if uiMaster.typing_first_expression:
            if uiMaster.uiEq1.is_active:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_EQUALS:
                            if not(pygame.key.get_mods() & pygame.KMOD_SHIFT):
                                uiMaster.typing_first_expression = False
                                uiMaster.uiEq1.is_active = False
                                rightsideui = uiExpression((0,0))
                                rightsideui.is_active = True
                                newEQ = uiEquation(uiMaster.uiEq1,rightsideui,(500,100))


            uiMaster.uiEq1.handle_events(events,mouse_absolute)
        else:
            uiEquation.static_handle_events(events,mouse_absolute)

    def draw(screen):
        if uiMaster.typing_first_expression:
            uiMaster.uiEq1.update()
            uiMaster.uiEq1.draw(screen)
        else:
            uiEquation.static_draw(screen)






