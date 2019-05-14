import expression as xp
import settings as st
import pygame
import xml.etree.ElementTree as ET
import copy
import time

FONT_PATH = st.font_locator("final.ttf")

SQRT2 = 1.4142135623731

DEFAULT_FONT_SIZE = 48
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.2
VINCULUM_SIZE = 0.05
PAREN_SCALE = 1.3

FONTS={}

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

def update_xml(name):
    from fontTools import ttLib
    t=ttLib.ttFont.TTFont('Resources/Fonts/'+name+'.ttf')
    t.saveXML('Resources/Fonts/'+name+'.ttx')

class smartSurface:

    simpleOps = {'+','-','*',u'\u00B7'}
    spacing = 10
    smallSpacing = 5

    def __init__(self, exp, frac_depth=0, script_depth=0, op_depth=0, cursor_show=True): #depth is number of layers into generation we are
        self.exp = exp
        self.y_bot = 0 #bot and top are with reference to bottom of surface
        self.y_top = 0
        self.y_mid = 0
        cursor_char = '|' if cursor_show else '\u0192'
        self.surface = pygame.Surface((0,0))
        
        COLORKEY = tinyShift(st.backgroundColor)
        st.lock.acquire()
        self.hitboxes = [] #([irect,orect], self.exp, op_depth)
        font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
        self.font_size = font_size
        font = get_font(font_size)
        self.font = font
        
        if type(exp) == xp.NoOpExpression:
            string = exp.strRep
            if exp.cursor:
                string = string[:exp.cursor_idx]+cursor_char+string[exp.cursor_idx:]
            self.surface, rect = font.render(string,st.fontColor,COLORKEY)
            ymin,ymax = get_height_offset_str(string, fontXML)
            self.y_bot, self.y_top = get_altitudes(ymin,ymax,self.surface.get_size()[1])
            self.y_mid = (self.y_bot+self.y_top)//2

            self.hitboxes.append(([self.surface.get_rect(), self.surface.get_rect()], self.exp, op_depth))


        elif exp.op.strRep in ["()","(",")"]: #parens are irrevocably broken
            avg_color = [(st.fontColor[i]+st.backgroundColor[i])//2 for i in range(3)]
            left_color = st.fontColor if "(" in exp.op.strRep else avg_color
            right_color = st.fontColor if ")" in exp.op.strRep else avg_color
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1, cursor_show)
            old_width, old_height = firstSurface.get_size()
            old_top = firstSurface.y_top
            old_bot = firstSurface.y_bot
            old_mid = firstSurface.y_mid
            internal_height = old_bot-old_top
            newFontSize=round(internal_height*PAREN_SCALE) #FIX THIS
            newFont = get_font(newFontSize)
            left, rect = newFont.render("(",left_color,COLORKEY)
            right, rect = newFont.render(")",right_color,COLORKEY)
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
            use_spacing = exp.op.strRep != "*"
            
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1, cursor_show)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth, op_depth+1, cursor_show)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()

            first_bot, first_mid, first_top = firstSurface.y_bot, firstSurface.y_mid, firstSurface.y_top
            second_bot, second_mid, second_top = secondSurface.y_bot, secondSurface.y_mid, secondSurface.y_top

            operatorSurface = pygame.Surface((0,0))
            op_bot = op_top = op_mid = 0
            if use_spacing: #not silent mul
                operatorSurface, rect = font.render(exp.op.strRep,st.fontColor,COLORKEY)
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
                
            
        elif exp.op.strRep == "^":
            
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1, cursor_show)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth+1, op_depth+1, cursor_show)

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
            self.hitboxes.append(([pygame.Rect(-100,-100,0,0),self.surface.get_rect()],self.exp,op_depth))
            
        elif exp.op.strRep == "frac" or exp.op.strRep == "/":
            
            firstSurface = smartSurface(exp.expList[0], frac_depth+1, script_depth, op_depth+1, cursor_show)
            secondSurface = smartSurface(exp.expList[1], frac_depth+1, script_depth, op_depth+1, cursor_show)

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
            pygame.draw.rect(self.surface, st.fontColor, vincRect)

            self.y_mid = vincAltitude+vinculumHeight//2
            self.y_bot = secondLoc[1]+second_bot
            self.y_top = first_top
                
            self.hitboxes = self.hitboxes + firstSurface.translateHitboxes(firstLoc) + secondSurface.translateHitboxes(secondLoc)
            self.hitboxes.append(([vincRect,self.surface.get_rect()],self.exp,op_depth))

        elif exp.op.strRep == "{}":
            expression = exp.expList[0]
            otherSurf = smartSurface(expression, frac_depth, script_depth, cursor_show)
            self.surface = otherSurf.surface
            self.hitboxes = otherSurf.hitboxes
            self.y_bot = otherSurf.y_bot
            self.y_top = otherSurf.y_top
            self.y_mid = otherSurf.y_mid
        else:
            print('Unknown operator in',exp)
        self.surface.set_colorkey(COLORKEY)
        st.lock.release()

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
