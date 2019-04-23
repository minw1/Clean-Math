import expression as xp
import settings as st
import pygame
import xml.etree.ElementTree as ET
import copy

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")

SQRT2 = 1.4142135623731

def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

def tinyShift(color):
    first_is_zero = (color[0]==0)

    if not first_is_zero:
        newcolor = (color[0]-1,color[1],color[2])
    else:
        newcolor = (color[0]+1,color[1],color[2])
    return newcolor

DEFAULT_FONT_SIZE = 48
PARENTHESES_ADJUSTMENT = 0.05
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.4
VINCULUM_SIZE = 0.05

FONTS={}
IFONTS={}

def is_intable(string):
    try:
        i=int(string)
        return True
    except ValueError:
        return False

fontXML = ET.parse('Resources/Fonts/cmu.ttx')
iFontXML = ET.parse('Resources/Fonts/cmu_i.ttx')

def get_bounds(xml):
    root = xml.getroot()
    head = root.find('head')
    xMin = int(head.find('xMin').get('value'))
    xMax = int(head.find('xMax').get('value'))
    yMin = int(head.find('yMin').get('value'))
    yMax = int(head.find('yMax').get('value'))
    return xMin,xMax,yMin,yMax

EM_SQUARE = 1400

def get_height_offset(char,xml):
    root = xml.getroot()

    #get the character's name
    hex_val = hex(ord(char))
    cmap = root.find('cmap').find('cmap_format_4')
    charnode = [child for child in cmap.getchildren() if child.get('code')==hex_val][0]
    name = charnode.get('name')

    if name=="space":
        return 0,EM_SQUARE

    #find its boundary
    glyf_font = fontXML.getroot().find('glyf')
    glyph = [child for child in glyf_font.getchildren() if child.get('name')==name][0]
    ymin,ymax=int(glyph.get('yMin')),int(glyph.get('yMax'))
    return ymin,ymax

def get_height_offset_str(string,xml):
    if string=='': return (0,EM_SQUARE)
    yMins,yMaxs=[],[]
    for char in string:
        ymin,ymax=get_height_offset(char,xml)
        yMins.append(ymin)
        yMaxs.append(ymax)
    return min(yMins),max(yMaxs)

def get_altitudes(ymin,ymax,height):
    return round(height*(-ymin)/(ymax-ymin)),round(height*(EM_SQUARE-ymin)/(ymax-ymin))

class smartSurface:

    simpleOps = {'+','-','*'} 
    spacing = 10

    def __init__(self, exp, frac_depth=0, script_depth=0, op_depth=0): #depth is number of layers into generation we are.
        self.exp = exp
        self.yline = 0
        st.lock.acquire()
        COLORKEY = tinyShift(st.backgroundColor)
        self.surface = None
        self.hitboxes = [] #(rect, self.exp, op_depth)
        font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
        self.font_size = font_size
        font = FONTS[font_size] if font_size in FONTS else pygame.freetype.Font(LATEX_FONT_PATH, font_size)
        FONTS[font_size]=font
        self.font = font
        iFont = IFONTS[font_size] if font_size in IFONTS else pygame.freetype.Font(LATEX_iFONT_PATH, font_size)
        IFONTS[font_size]=iFont
        self.iFont = iFont
        if type(exp) == xp.NoOpExpression:
            is_int = is_intable(exp.strRep)
            if exp.strRep == "|":
                middleColor = [(st.fontColor[i]+COLORKEY[i])//2 for i in range(3)]
                self.surface,rect = font.render('|',middleColor,COLORKEY)
                self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            elif is_int:
                self.surface,rect = font.render(exp.strRep,st.fontColor,COLORKEY)
                self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            elif exp.strRep == " ":
                self.surface,rect = font.render('|',COLORKEY,COLORKEY)
                self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            else:
                self.surface,rect = iFont.render(exp.strRep,st.fontColor,COLORKEY)
                self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            ymin,ymax=get_height_offset_str(exp.strRep,(fontXML if (is_int or exp.strRep == "|") else iFontXML))
            minY,maxY = get_altitudes(ymin,ymax,self.surface.get_size()[1])
            self.yline=(minY+maxY)//2
            self.surface.set_colorkey(COLORKEY)
        elif exp.op.strRep == "()":
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1)
            width, height = firstSurface.get_size()
            newFontSize=height*SQRT2+round(2*PARENTHESES_ADJUSTMENT*font_size)
            newFont = pygame.freetype.Font(LATEX_FONT_PATH, newFontSize)
            openParen, openRect = newFont.render("(",st.fontColor,COLORKEY)
            closeParen, closeRect = newFont.render(")",st.fontColor,COLORKEY)
            openWidth, openHeight = openParen.get_size()
            closeWidth, closeHeight = closeParen.get_size()
            endWidth = openWidth+width+closeWidth
            endHeight = max(openHeight, height, closeHeight)
            self.surface = pygame.Surface((endWidth,endHeight))
            self.surface.fill(COLORKEY)
            self.surface.blit(openParen,(0,(endHeight-openHeight)//2))
            self.surface.blit(closeParen,(endWidth-closeWidth,(endHeight-closeHeight)//2))
            expLocation = (openWidth, (endHeight-height)//2)
            self.surface.blit(firstSurface.surface, expLocation)
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLocation)
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            self.yline = endHeight//2            
        elif exp.op.strRep == "(":
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1)
            width, height = firstSurface.get_size()
            newFontSize=height*SQRT2+round(2*PARENTHESES_ADJUSTMENT*font_size)
            newFont = pygame.freetype.Font(LATEX_FONT_PATH, newFontSize)
            openParen, openRect = newFont.render("(",st.fontColor,COLORKEY)
            closeParen, closeRect = newFont.render(")",tuple([(x+255)//2 for x in st.fontColor]),COLORKEY)
            openWidth, openHeight = openParen.get_size()
            closeWidth, closeHeight = closeParen.get_size()
            endWidth = openWidth+width+closeWidth
            endHeight = max(openHeight, height, closeHeight)
            self.surface = pygame.Surface((endWidth,endHeight))
            self.surface.fill(COLORKEY)
            self.surface.blit(openParen,(0,(endHeight-openHeight)//2))
            self.surface.blit(closeParen,(endWidth-closeWidth,(endHeight-closeHeight)//2))
            expLocation = (openWidth, (endHeight-height)//2)
            self.surface.blit(firstSurface.surface, expLocation)
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLocation)
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            self.yline = endHeight//2
            self.surface.set_colorkey(COLORKEY)
        elif exp.op.strRep == ")":
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1)
            width, height = firstSurface.get_size()
            newFontSize=height*SQRT2+round(2*PARENTHESES_ADJUSTMENT*font_size)
            newFont = pygame.freetype.Font(LATEX_FONT_PATH, newFontSize)
            openParen, openRect = newFont.render("(",tuple([(x+255)//2 for x in st.fontColor]),COLORKEY)
            closeParen, closeRect = newFont.render(")",st.fontColor,COLORKEY)
            openWidth, openHeight = openParen.get_size()
            closeWidth, closeHeight = closeParen.get_size()
            endWidth = openWidth+width+closeWidth
            endHeight = max(openHeight, height, closeHeight)
            self.surface = pygame.Surface((endWidth,endHeight))
            self.surface.fill(COLORKEY)
            self.surface.blit(openParen,(0,(endHeight-openHeight)//2))
            self.surface.blit(closeParen,(endWidth-closeWidth,(endHeight-closeHeight)//2))
            expLocation = (openWidth, (endHeight-height)//2)
            self.surface.blit(firstSurface.surface, expLocation)
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLocation)
            self.hitboxes.append(([self.surface.get_rect(),self.surface.get_rect()],self.exp,op_depth))
            self.yline = endHeight//2
            self.surface.set_colorkey(COLORKEY)
        elif exp.op.strRep in self.simpleOps:
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth, op_depth+1)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()
            firstYline, secondYline = firstSurface.yline,secondSurface.yline

            character = u'\u00B7' if exp.op.strRep == '*' else exp.op.strRep # we want multiplication to appear as cdots
            operatorSurface, operatorRect = font.render(character,st.fontColor,COLORKEY)
            operatorWidth, operatorHeight = operatorSurface.get_size()

            firstAbove = firstHeight-firstYline
            secondAbove = secondHeight-secondYline
            ymin,ymax = get_height_offset(character,fontXML)
            opmin,opmax = get_altitudes(ymin,ymax,operatorHeight)
            operatorYline = (opmin+opmax)//2
            operatorAbove = operatorHeight-operatorYline

            finalAbove = max(firstAbove, secondAbove, operatorAbove)
            finalBelow = max(firstYline, secondYline, operatorYline)
            finalHeight = finalAbove+finalBelow
            finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill(COLORKEY)
            self.surface.blit(firstSurface.surface, (0,finalAbove-firstAbove))
            self.surface.blit(operatorSurface, (firstWidth+self.spacing, finalAbove-operatorAbove))
            self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,finalAbove-secondAbove))

            operatorLoc = pygame.Rect(firstWidth+self.spacing,finalAbove-operatorAbove,operatorRect.w,operatorRect.h)
            self.hitboxes = firstSurface.translateHitboxes([0,finalAbove-firstAbove]) + secondSurface.translateHitboxes([finalWidth-secondWidth,finalAbove-secondAbove])
            self.hitboxes.append(([operatorLoc,self.surface.get_rect()],self.exp,op_depth))
            self.surface.set_colorkey(COLORKEY)
            self.yline = finalBelow

        elif exp.op.strRep == "^":
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1)
            secondSurface = smartSurface(exp.expList[1],frac_depth,script_depth+1, op_depth+1)
            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()
            firstYline, secondYline = firstSurface.yline,secondSurface.yline


            finalWidth = firstWidth + secondWidth
            finalHeight = firstHeight + secondHeight-secondYline
            self.yline = firstYline

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill(COLORKEY)
            self.surface.blit(firstSurface.surface, (0,secondHeight-secondYline))
            self.surface.blit(secondSurface.surface, (firstWidth,0))
            self.hitboxes = firstSurface.translateHitboxes([0,secondHeight-secondYline]) + secondSurface.translateHitboxes([firstWidth,0])

            self.surface.set_colorkey(COLORKEY)
            self.hitboxes.append(([pygame.Rect(0,0,0,0),self.surface.get_rect()],self.exp,op_depth))

        elif exp.op.strRep == "frac" or exp.op.strRep == "/":

            numeratorExp = exp.expList[0]
            denominatorExp = exp.expList[1]
            numSurface = smartSurface(numeratorExp, frac_depth+1, script_depth, op_depth+1)
            denomSurface = smartSurface(denominatorExp, frac_depth+1, script_depth, op_depth+1)
            numWidth, numHeight = numSurface.get_size()
            denomWidth, denomHeight = denomSurface.get_size()
            vinculumWidth = max(numWidth, denomWidth)+round(2*FRAC_ADJUSTMENT*font_size)
            vinculumHeight = round(VINCULUM_SIZE*font_size)

            endWidth = vinculumWidth
            endHeight = numHeight + vinculumHeight + denomHeight + round(2*FRAC_VERTICAL_TOLERANCE*font_size)
            
            self.surface = pygame.Surface((endWidth, endHeight))
            self.surface.fill(COLORKEY)
            numLocation = ((endWidth-numWidth)//2,0)
            denomLocation = ((endWidth-denomWidth)//2,endHeight-denomHeight)
            vincHeight = numHeight+round(FRAC_VERTICAL_TOLERANCE*font_size)
            self.surface.blit(numSurface.surface, numLocation)
            self.surface.blit(denomSurface.surface, denomLocation)

            vincRect = pygame.Rect(0,vincHeight,vinculumWidth,vinculumHeight)

            pygame.draw.rect(self.surface, st.fontColor, vincRect)
            self.hitboxes = self.hitboxes+numSurface.translateHitboxes(numLocation)+denomSurface.translateHitboxes(denomLocation)
            self.hitboxes.append(([vincRect,self.surface.get_rect()],self.exp,op_depth))
            self.yline = vincHeight + (vinculumHeight//2)
            self.surface.set_colorkey(COLORKEY)
        elif exp.op.strRep == "{}":
            expression = exp.expList[0]
            otherSurf = smartSurface(expression, frac_depth, script_depth)
            self.surface = otherSurf.surface
            self.hitboxes = otherSurf.hitboxes
            self.yline = otherSurf.yline
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
