import expression as xp
import settings as st
import pygame
import xml.etree.ElementTree as ET
import copy
import time

FONT_PATH = st.font_locator("final.ttf")
RM_FONT_PATH = st.font_locator("cmu.ttf")

SQRT2 = 1.4142135623731

DEFAULT_FONT_SIZE = 48
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.2
VINCULUM_SIZE = 0.05
PAREN_SCALE = 1.3

FONTS={}
RM_FONTS={}

BOTTOM_EM = 0
TOP_EM = 1386

def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

def tinyShift(color):
    first_is_zero = (color[0]==0)

    if not first_is_zero:
        newcolor = (color[0]-1,color[1],color[2])
    else:
        newcolor = (color[0]+1,color[1],color[2])
    return newcolor

fontXML = ET.parse('Resources/Fonts/final.ttx')
rmFontXML = ET.parse('Resources/Fonts/cmu.ttx')

def is_intable(string):
    try:
        i=int(string)
        return True
    except ValueError:
        return False

def get_bounds(xml):
    root = xml.getroot()
    head = root.find('head')
    xMin = int(head.find('xMin').get('value'))
    xMax = int(head.find('xMax').get('value'))
    yMin = int(head.find('yMin').get('value'))
    yMax = int(head.find('yMax').get('value'))
    return xMin,xMax,yMin,yMax

def get_height_offset(char,xml):
    try:
        root = xml.getroot()

        #get the character's name
        hex_val = hex(ord(char))
        cmap = root.find('cmap').find('cmap_format_4')
        charnode = [child for child in cmap.getchildren() if child.get('code')==hex_val][0]
        name = charnode.get('name')

        if name=="space":
            return get_height_offset("|",xml)#BOTTOM_EM, TOP_EM

        #find its boundary
        glyf_font = fontXML.getroot().find('glyf')
        glyph = [child for child in glyf_font.getchildren() if child.get('name')==name][0]
        ymin,ymax=int(glyph.get('yMin')),int(glyph.get('yMax'))
        return ymin,ymax
    except IndexError:
        return BOTTOM_EM, TOP_EM

def get_height_offset_str(string,xml):
    if string=='': return BOTTOM_EM, TOP_EM
    yMins,yMaxs=[],[]
    for char in string:
        ymin,ymax=get_height_offset(char,xml)
        yMins.append(ymin)
        yMaxs.append(ymax)
    return min(yMins),max(yMaxs)

def get_altitudes(ymin,ymax,height):
    return height-round(height*(BOTTOM_EM-ymin)/(ymax-ymin)),height-round(height*(TOP_EM-ymin)/(ymax-ymin))

def get_font(font_size):
    font = FONTS[font_size] if font_size in FONTS else pygame.freetype.Font(FONT_PATH, font_size)
    FONTS[font_size] = font
    return font

def get_rm_font(font_size):
    font = RM_FONTS[font_size] if font_size in RM_FONTS else pygame.freetype.Font(RM_FONT_PATH, font_size)
    RM_FONTS[font_size] = font
    return font

def update_xml(name):
    from fontTools import ttLib
    t=ttLib.ttFont.TTFont('Resources/Fonts/'+name+'.ttf')
    t.saveXML('Resources/Fonts/'+name+'.ttx')

class smartSurface:

    simpleOps = {'+','-','*',u'\u00B7'}
    mathrmOps = {'sin','cos','tan','cot','sec','csc','sinh','cosh','tanh','coth','sech','csch',
                 'arcsin','arccos','arctan','arccot','arcsec','arccsc','arcsinh','arccosh','arctanh','arccoth','arcsech','arccsch',
                 'log','exp','gcd','lcm','ord','loading...'}
    spacing = 10
    smallSpacing = 5

    def __init__(self, exp, frac_depth=0, script_depth=0, op_depth=0, cursor_show=True, silent=False, silentExp=None): #depth is number of layers into generation we are
        self.exp = exp
        self.y_bot = 0 #bot and top are with reference to bottom of surface
        self.y_top = 0
        self.y_mid = 0
        cursor_char = '|' if cursor_show else '\u0192'

        cursor = exp.cursor
        cursor_idx = exp.cursor_idx if cursor else None
        
        self.surface = pygame.Surface((0,0))

        if exp == silentExp: silent = True
        
        COLORKEY = tinyShift(st.backgroundColor)

        self.color = COLORKEY if silent else st.fontColor
        st.lock.acquire()
        self.hitboxes = [] #([irect,orect], self.exp, op_depth)
        font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
        self.font_size = font_size
        font = get_font(font_size)
        self.font = font
        
        try: #this'll see if there are any silent brackets whose cursors need to be added
            first = exp.expList[0]
            second = exp.expList[1]
            if first.op.strRep == "{}" and first.cursor:
                cursor = True
                cursor_idx = 0
            if second.op.strRep == "{}" and second.cursor:
                cursor = True
                cursor_idx = 1
        except: pass #if not, no big deal
        
        if type(exp) == xp.NoOpExpression:
            string = exp.strRep
            if cursor:
                string = string[:cursor_idx]+cursor_char+string[cursor_idx:]
            self.surface, rect = font.render(string,self.color,COLORKEY)
            ymin,ymax = get_height_offset_str(string, fontXML)
            self.y_bot, self.y_top = get_altitudes(ymin,ymax,self.surface.get_size()[1])
            self.y_mid = (self.y_bot+self.y_top)//2

            self.hitboxes.append(([self.surface.get_rect(), self.surface.get_rect()], self.exp, op_depth))
        elif exp.op.strRep in ["()","(",")"]:
            avg_color = [(self.color[i]+st.backgroundColor[i])//2 for i in range(3)]
            left_color = self.color if "(" in exp.op.strRep else avg_color
            right_color = self.color if ")" in exp.op.strRep else avg_color
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1, cursor_show, silent, silentExp)
            old_width, old_height = firstSurface.get_size()
            old_top = firstSurface.y_top
            old_bot = firstSurface.y_bot
            old_mid = firstSurface.y_mid
            internal_height = old_bot-old_top
            newFontSize=round(internal_height*PAREN_SCALE)
            newFont = get_font(newFontSize)
            left, rect = newFont.render(("|" if cursor and cursor_idx == 0 else "")+"(",left_color,COLORKEY)
            right, rect = newFont.render(")"+("|" if cursor and cursor_idx == 1 else ""),right_color,COLORKEY)
            left_width, left_height = left.get_size()
            right_width, right_height = right.get_size()
            
            paren_height = max(left_height,right_height)
            
            total_width = left_width+old_width+right_width

            paren_above = paren_below = (paren_height-internal_height)//2
            exp_above = old_top
            exp_below = old_height-old_bot

            finalAbove = max(exp_above,paren_above)
            finalBelow = max(exp_below,paren_below)

            total_height=finalAbove+internal_height+finalBelow

            leftParenAlt = finalAbove-(left_height-internal_height)//2
            rightParenAlt = finalAbove-(right_height-internal_height)//2
            expAlt = finalAbove-exp_above
            expLoc = (left_width,expAlt)

            
            self.surface = pygame.Surface((total_width,total_height))
            self.surface.fill((COLORKEY))

            self.surface.blit(left, (0,leftParenAlt))
            self.surface.blit(right, (total_width-right_width,rightParenAlt))
            self.surface.blit(firstSurface.surface, expLoc)

            self.y_bot = expAlt+old_bot
            self.y_mid = expAlt+old_mid
            self.y_top = expAlt+old_top
            
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLoc)
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
        elif exp.op.strRep in self.simpleOps:
            string = (cursor_char if cursor_idx == 0 else '')+exp.op.strRep+(cursor_char if cursor_idx == 0 else '')
            use_spacing = exp.op.strRep != "*"
            
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1, cursor_show, silent, silentExp)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth, op_depth+1, cursor_show, silent, silentExp)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()

            first_bot, first_mid, first_top = firstSurface.y_bot, firstSurface.y_mid, firstSurface.y_top
            second_bot, second_mid, second_top = secondSurface.y_bot, secondSurface.y_mid, secondSurface.y_top

            operatorSurface = pygame.Surface((0,0))
            op_bot = op_top = op_mid = 0
            if use_spacing: #not silent mul
                operatorSurface, rect = font.render(exp.op.strRep,self.color,COLORKEY)
                ymin,ymax = get_height_offset_str(exp.op.strRep, fontXML)
                op_bot,op_top = get_altitudes(ymin,ymax,operatorSurface.get_size()[1])
                op_mid = (op_bot+op_top)//2

            opWidth, opHeight = operatorSurface.get_size()

            finalWidth = (self.spacing*(1+3*use_spacing))//2+firstWidth+secondWidth+opWidth
            firstBelow = firstHeight - first_mid
            secondBelow = secondHeight - second_mid
            opBelow = opHeight - op_mid

            finalAbove = max(first_mid, second_mid, op_mid)
            finalBelow = max(firstBelow, secondBelow, opBelow)
            finalHeight = finalAbove + finalBelow

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill((COLORKEY))
            
            firstLoc = (0, finalAbove - first_mid)
            secondLoc = (finalWidth-secondWidth, finalAbove - second_mid)
            opLoc = (firstWidth+self.spacing*use_spacing, finalAbove - op_mid)
            opRect = pygame.Rect(opLoc[0],opLoc[1],opWidth,opHeight)

            self.surface.blit(firstSurface.surface, firstLoc)
            self.surface.blit(secondSurface.surface, secondLoc)
            self.surface.blit(operatorSurface, opLoc)

            self.y_mid = finalAbove
            self.y_bot = self.y_mid-min(first_mid-first_bot,second_mid-second_bot,op_mid-op_bot)
            self.y_top = self.y_mid+min(first_top-first_mid,second_top-second_mid,op_top-op_mid)
                
            self.hitboxes = self.hitboxes + firstSurface.translateHitboxes(firstLoc) + secondSurface.translateHitboxes(secondLoc)
            self.hitboxes.append(([opRect,self.surface.get_rect()],self.exp,op_depth))
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
                
            
        elif exp.op.strRep == "^":
            
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1, cursor_show, silent, silentExp)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth+1, op_depth+1, cursor_show, silent, silentExp)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()

            first_bot, first_mid, first_top = firstSurface.y_bot, firstSurface.y_mid, firstSurface.y_top
            second_bot, second_mid, second_top = secondSurface.y_bot, secondSurface.y_mid, secondSurface.y_top

            finalWidth = firstWidth + secondWidth
            firstAbove = first_top
            secondAbove = second_mid
            firstBelow = firstHeight-first_top
            secondBelow = secondHeight-second_mid

            finalAbove = max(firstAbove, secondAbove)
            finalBelow = max(firstBelow, secondBelow)
            finalHeight = finalAbove + finalBelow

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill((COLORKEY))

            firstLoc = (0, finalAbove - firstAbove)
            secondLoc = (finalWidth - secondWidth, finalAbove - secondAbove)

            self.surface.blit(firstSurface.surface, firstLoc)
            self.surface.blit(secondSurface.surface, secondLoc)

            self.y_mid = first_mid+firstLoc[1]
            self.y_bot = first_bot+firstLoc[1]
            self.y_top = min(finalAbove - secondAbove + second_top, finalAbove - firstAbove + first_top)
                
            self.hitboxes = self.hitboxes + firstSurface.translateHitboxes(firstLoc) + secondSurface.translateHitboxes(secondLoc)
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))

            if cursor:
                cursorSurf, rect = font.render(cursor_char,self.color,COLORKEY)
                cuWidth, cuHeight = cursorSurf.get_size()
                ymin,ymax = get_height_offset_str(cursor_char, fontXML)
                cu_bot, cu_top = get_altitudes(ymin,ymax,cuHeight)
                cu_mid = (cu_bot+cu_top)//2
                oldSurface = self.surface
                oldWidth, oldHeight = finalWidth, finalHeight
                oldHitboxes = self.hitboxes
                old_mid = self.y_mid
                old_bot = self.y_bot
                old_top = self.y_top
                oldBelow = oldHeight-old_mid
                cuBelow = cuHeight-cu_mid

                newAbove = max(old_mid, cu_mid)
                newBelow = max(oldBelow, cuBelow)

                self.y_mid = newAbove
                self.y_bot = self.y_mid-min(cu_mid-cu_bot,old_mid-old_bot)
                self.y_top = self.y_mid+min(cu_top-cu_mid, old_top-old_mid)

                newWidth = cuWidth+self.spacing+oldWidth
                newHeight = newAbove+newBelow
                self.surface = pygame.Surface((newWidth, newHeight))
                self.surface.fill((COLORKEY))
                if cursor_idx == 0:
                    cuLoc = (0, newAbove-cu_mid)
                    oldLoc = (newWidth-oldWidth, newAbove-old_mid)
                    self.surface.blit(oldSurface, oldLoc)
                    self.surface.blit(cursorSurf, cuLoc)
                    self.hitboxes = self.translateHitboxes(oldLoc)
                elif cursor_idx == 1:
                    cuLoc = (newWidth-cuWidth, newAbove-cu_mid)
                    oldLoc = (0, newAbove-old_mid)
                    self.surface.blit(oldSurface, oldLoc)
                    self.surface.blit(cursorSurf, cuLoc)
                    self.hitboxes = self.translateHitboxes(oldLoc)
            
        elif exp.op.strRep == "frac" or exp.op.strRep == "/":
            
            firstSurface = smartSurface(exp.expList[0], frac_depth+1, script_depth, op_depth+1, cursor_show, silent, silentExp)
            secondSurface = smartSurface(exp.expList[1], frac_depth+1, script_depth, op_depth+1, cursor_show, silent, silentExp)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()

            first_bot, first_mid, first_top = firstSurface.y_bot, firstSurface.y_mid, firstSurface.y_top
            second_bot, second_mid, second_top = secondSurface.y_bot, secondSurface.y_mid, secondSurface.y_top

            vinculumWidth = max(firstWidth, secondWidth)+round(2*FRAC_ADJUSTMENT*font_size)
            vinculumHeight = round(VINCULUM_SIZE*font_size)

            finalWidth = vinculumWidth
            finalHeight = firstHeight + vinculumHeight + secondHeight + round(2*FRAC_VERTICAL_TOLERANCE*font_size)
            vincAltitude = firstHeight+round(FRAC_VERTICAL_TOLERANCE*font_size)

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill((COLORKEY))

            firstLoc = ((finalWidth-firstWidth)//2,0)
            secondLoc = ((finalWidth-secondWidth)//2,finalHeight-secondHeight)

            self.surface.blit(firstSurface.surface, firstLoc)
            self.surface.blit(secondSurface.surface, secondLoc)

            vincRect = pygame.Rect(0,vincAltitude,vinculumWidth,vinculumHeight)
            pygame.draw.rect(self.surface, self.color, vincRect)

            self.y_mid = vincAltitude+vinculumHeight//2
            self.y_bot = secondLoc[1]+second_bot
            self.y_top = first_top
                
            self.hitboxes = self.hitboxes + firstSurface.translateHitboxes(firstLoc) + secondSurface.translateHitboxes(secondLoc)
            self.hitboxes.append(([vincRect,self.surface.get_rect()],self.exp,op_depth))
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))

            if cursor:
                cursorSurf, rect = font.render(cursor_char,self.color,COLORKEY)
                cuWidth, cuHeight = cursorSurf.get_size()
                ymin,ymax = get_height_offset_str(cursor_char, fontXML)
                cu_bot, cu_top = get_altitudes(ymin,ymax,cuHeight)
                cu_mid = (cu_bot+cu_top)//2
                oldSurface = self.surface
                oldWidth, oldHeight = finalWidth, finalHeight
                oldHitboxes = self.hitboxes
                old_mid = self.y_mid
                old_bot = self.y_bot
                old_top = self.y_top
                oldBelow = oldHeight-old_mid
                cuBelow = cuHeight-cu_mid

                newAbove = max(old_mid, cu_mid)
                newBelow = max(oldBelow, cuBelow)

                self.y_mid = newAbove
                self.y_bot = self.y_mid-min(cu_mid-cu_bot,old_mid-old_bot)
                self.y_top = self.y_mid+min(cu_top-cu_mid, old_top-old_mid)

                newWidth = cuWidth+self.spacing+oldWidth
                newHeight = newAbove+newBelow
                self.surface = pygame.Surface((newWidth, newHeight))
                self.surface.fill((COLORKEY))
                if cursor_idx == 0:
                    cuLoc = (0, newAbove-cu_mid)
                    oldLoc = (newWidth-oldWidth, newAbove-old_mid)
                    self.surface.blit(oldSurface, oldLoc)
                    self.surface.blit(cursorSurf, cuLoc)
                    self.hitboxes = self.translateHitboxes(oldLoc)
                elif cursor_idx == 1:
                    cuLoc = (newWidth-cuWidth, newAbove-cu_mid)
                    oldLoc = (0, newAbove-old_mid)
                    self.surface.blit(oldSurface, oldLoc)
                    self.surface.blit(cursorSurf, cuLoc)
                    self.hitboxes = self.translateHitboxes(oldLoc)

        elif exp.op.strRep == "{}":
            expression = exp.expList[0]
            otherSurf = smartSurface(expression, frac_depth, script_depth, op_depth, cursor_show, silent, silentExp)
            self.surface = otherSurf.surface
            self.hitboxes = otherSurf.hitboxes
            self.y_bot = otherSurf.y_bot
            self.y_top = otherSurf.y_top
            self.y_mid = otherSurf.y_mid
        elif exp.op.strRep in self.mathrmOps:
            opFont = get_rm_font(self.font_size)
            opSurface, rect = opFont.render(exp.op.strRep,self.color,COLORKEY)
            ymin,ymax = get_height_offset_str(exp.op.strRep, rmFontXML)
            opWidth, opHeight = opSurface.get_size()
            op_bot, op_top = get_altitudes(ymin,ymax,opHeight)
            op_mid = (op_bot+op_top)//2

            encSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1, cursor_show, silent, silentExp)
            encWidth, encHeight = encSurface.get_size()
            enc_bot, enc_mid, enc_top = encSurface.y_bot, encSurface.y_mid, encSurface.y_top

            finalWidth = opWidth+self.spacing+encWidth
            encBelow = encHeight - enc_mid
            opBelow = opHeight - op_mid

            finalAbove = max(enc_mid, op_mid)
            finalBelow = max(encBelow, opBelow)
            finalHeight = finalAbove + finalBelow

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill((COLORKEY))
            
            encLoc = (opWidth+self.spacing, finalAbove - enc_mid)
            opLoc = (0, finalAbove - op_mid)
            opRect = pygame.Rect(opLoc[0],opLoc[1],opWidth,opHeight)

            self.surface.blit(encSurface.surface, encLoc)
            self.surface.blit(opSurface, opLoc)

            self.y_mid = finalAbove
            self.y_bot = self.y_mid-min(enc_mid-enc_bot,op_mid-op_bot)
            self.y_top = self.y_mid+min(enc_top-enc_mid,op_top-op_mid)
                
            self.hitboxes = self.hitboxes + encSurface.translateHitboxes(encLoc)
            self.hitboxes.append(([opRect,self.surface.get_rect()],self.exp,op_depth))
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
        else:
            print('Unknown operator in',exp)
        self.surface.set_colorkey(COLORKEY)
        st.lock.release()

    def format_eq(firstSurface, secondSurface):
        COLORKEY = tinyShift(st.backgroundColor)
        firstWidth, firstHeight = firstSurface.get_size()
        secondWidth, secondHeight = secondSurface.get_size()

        first_bot, first_mid, first_top = firstSurface.y_bot, firstSurface.y_mid, firstSurface.y_top
        second_bot, second_mid, second_top = secondSurface.y_bot, secondSurface.y_mid, secondSurface.y_top

        font_size = max(firstSurface.font_size,secondSurface.font_size)
        font = get_font(font_size)
        operatorSurface, rect = font.render("=",st.fontColor,COLORKEY)
        ymin,ymax = get_height_offset_str('=', fontXML)
        op_bot,op_top = get_altitudes(ymin,ymax,operatorSurface.get_size()[1])
        op_mid = (op_bot+op_top)//2

        opWidth, opHeight = operatorSurface.get_size()

        finalWidth = 2*smartSurface.spacing+firstWidth+secondWidth+opWidth
        firstBelow = firstHeight - first_mid
        secondBelow = secondHeight - second_mid
        opBelow = opHeight - op_mid

        finalAbove = max(first_mid, second_mid, op_mid)
        finalBelow = max(firstBelow, secondBelow, opBelow)
        finalHeight = finalAbove + finalBelow

        surface = pygame.Surface((finalWidth, finalHeight))
        surface.fill((COLORKEY))
        
        firstLoc = (0, finalAbove - first_mid)
        secondLoc = (finalWidth-secondWidth, finalAbove - second_mid)
        opLoc = (firstWidth+smartSurface.spacing, finalAbove - op_mid)
        opRect = pygame.Rect(opLoc[0],opLoc[1],opWidth,opHeight)

        surface.blit(firstSurface.surface, firstLoc)
        surface.blit(secondSurface.surface, secondLoc)
        surface.blit(operatorSurface, opLoc)
        surface.set_colorkey(COLORKEY)
        
        return surface, opLoc, (firstLoc,secondLoc)

    def translateHitboxes(self,coordinates):
        newHitboxes = []
        for hb in self.hitboxes:
            [irect,orect], expression, op_depth = hb
            newHitboxes.append(([irect.move(coordinates[0],coordinates[1]),orect.move(coordinates[0],coordinates[1])], expression, op_depth))
        return newHitboxes

    def get_at_position(self,coordinates):
        best_exp=None
        best_op_depth=-1
        for hb in self.hitboxes:
            [irect,orect], expression, op_depth = hb
            if op_depth>best_op_depth and irect.collidepoint(coordinates): #if it's further in and the point is in the rect
                best_exp=expression
                best_op_depth = op_depth
        return best_exp

    def get_all_intersects(self,rectangle):
        toReturn = []
        for hb in self.hitboxes:
            [irect,orect], expression, op_depth = hb
            if irect.colliderect(rectangle):
                toReturn.append(expression)
        return toReturn

    def is_ancestor(old_guy,kid):
        if kid == old_guy:
            return True
        if kid == None:
            return False
        return smartSurface.is_ancestor(old_guy,kid.parent)

    def all_cousins_are_offspring(ancestor,children):
        for child in children:
            if not smartSurface.is_ancestor(ancestor,child):
                return False
        return True

    def get_youngest_common_ancestor(kids):
        candidate = kids[0]
        while not candidate==None:
            if smartSurface.all_cousins_are_offspring(candidate,kids):
                return candidate
            candidate = candidate.parent
        print("SOMETHING IS VERY WRONG WITH THE TREE STRUCTURE")
        return None

    def selectFromRect(self,rectangle):
        thelist = self.get_all_intersects(rectangle)
        if thelist == []: return None
        YCA = smartSurface.get_youngest_common_ancestor(thelist)
        return YCA

    def get_size(self):
        return self.surface.get_size()

    def get_rect(self):
        return self.surface.get_rect()
