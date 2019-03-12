import pygame
import pygame.freetype
import string
import settings as st
from math import sqrt
SQRT2 = sqrt(2)

def floatcastable(str):
    try:
        float(str)
        return True
    except:
        return False

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")

def size_to_pixels(font_size):
    font = pygame.freetype.Font(LATEX_FONT_PATH, font_size)
    return font.render('1234567890')[0].get_size()[1]

print(size_to_pixels(100))

def makeSmaller(font_size):
    return round(font_size/SQRT2)

def findEndOfOperand(tex):
    pass #implement

'''
Notes: apply only to TeX strings that have spaces around operators.
We can't insert spaces upon receiving them into smartSurface because of
smartSurface's recursive nature.
'''

class smartSurface:
    operators = {'+','-','*','^'} #'*' will appear as a cdot
    spacing = 10
    
    def __init__(self, tex, pos, font_size, depth): #depth is number of layers into generation we are. 
        self.surface = None
        font = pygame.freetype.Font(LATEX_FONT_PATH, font_size)
        iFont = pygame.freetype.Font(LATEX_iFONT_PATH, font_size)
        st.lock.acquire()
        self.tex = tex
        self.hitboxes=[]

        if tex[0]=="\\":
            pass
        elif tex[0]=="(":
            depth_in=0
            i=0
            while True:
                if tex[i]=="(":
                    depth_in+=1
                elif tex[i]==")":
                    depth_in-=1
                i+=1
                if depth_in==0:
                    break
            if depth_in>0:
                raise ValueError("Mismatched parentheses")
            firstTex = tex[1:i-1]
            lastTex = tex[i:]
            firstSurface = None
            if lastTex[0] in operators:
                endOfSecondOperand = 1+findEndOfOperand(lastTex[1:])
                secondTex = tex[i:i+endOfSecondOperand]
                pass #read through until we hit the end of the second operand
            else:
                pass #we can treat this as self-contained
            #generate first
            #generate last
            #add parens around first
            #splice
        else:
            hasOperator = -1
            for i in range(len(tex)):
                if tex[i] in operators:
                    hasOperator=i
                    break
            if hasOperator == -1:
                pass #interpret w/o operators
            else:
                before=tex[:hasOperator]
                operator = tex[hasOperator]
                secondOperand = tex[i:hasOperator+1+findEndOfOperand(tex[hasOperator+1:])]
                
                
        
                


















        
        '''if tex in list(string.ascii_letters):
            self.surface,rect = iFont.render(tex,st.fontColor)
            self.hitboxes.append((self.surface.get_rect(),pos))
        elif floatcastable(tex):
            self.surface,rect = font.render(tex,st.fontColor)
            self.hitboxes.append((self.surface.get_rect(),pos))
        elif tex[0] =="\\":
            pass
        elif tex[0] == "(":
            pass
        elif tex[0] == ")":
            pass
        else:
            for i in range(0,len(tex)):
                if tex[i] in self.operators:
                    firstSurface = smartSurface(tex[0:i],[0,i],font_size)
                    firstWidth, firstHeight = firstSurface.get_size()
                    secondSurface = smartSurface(tex[i+1:],[i+1,len(tex)],font_size)
                    secondWidth, secondHeight = secondSurface.get_size()
                    operatorSurface, operatorRect = font.render(tex[i],st.fontColor)
                    operatorWidth, operatorHeight = operatorSurface.get_size()
                    finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing
                    finalHeight = max(firstHeight,secondHeight,operatorHeight)
                    self.surface = pygame.Surface((finalWidth, finalHeight))
                    self.surface.fill((255,255,255))
                    self.surface.blit(firstSurface.surface, (0,(finalHeight-firstHeight)//2))
                    self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,(finalHeight-secondHeight)//2))
                    self.surface.blit(operatorSurface, (firstWidth+self.spacing,(finalHeight-operatorHeight)//2))

                    for (hitbox,value) in firstSurface.hitboxes:
                        self.hitboxes.append((hitbox.move(0,(finalHeight-firstHeight)//2),value))
                    for (hitbox,value) in secondSurface.hitboxes:
                        self.hitboxes.append((hitbox.move(finalWidth-secondWidth,(finalHeight-secondHeight)//2),value))

                    self.hitboxes.append((operatorSurface.get_rect().move(firstWidth+self.spacing,(finalHeight-operatorHeight)//2),value))
                    break
            if self.surface == None:
                i=1
                while floatcastable(tex[:i]) or tex[i-1]=='.': #if it's part of a float
                    i+=1
                i-=1
                firstSurface = smartSurface(tex[0:i],[0,i],font_size)
                firstWidth, firstHeight = firstSurface.get_size()
                secondSurface = smartSurface(tex[i:],[i,len(tex)],font_size)
                secondWidth, secondHeight = secondSurface.get_size()
                finalWidth = firstWidth+secondWidth+self.spacing
                finalHeight = max(firstHeight,secondHeight)
                self.surface = pygame.Surface((finalWidth, finalHeight))
                self.surface.fill((255,255,255))
                self.surface.blit(firstSurface.surface, (0,(finalHeight-firstHeight)//2))
                self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,(finalHeight-secondHeight)//2))
                for (hitbox,value) in firstSurface.hitboxes:
                    self.hitboxes.append((hitbox.move(0,(finalHeight-firstHeight)//2),value))
                for (hitbox,value) in secondSurface.hitboxes:
                    self.hitboxes.append((hitbox.move(finalWidth-secondWidth,(finalHeight-secondHeight)//2),value))'''
                
        st.lock.release()

                    

    def get_size(self):
        return self.surface.get_size()

    def __hash__(self):
        return hash(self.tex)

#pygame.init()
#screen = pygame.display.set_mode([800,600], pygame.RESIZABLE)

#expression = smartSurface("3a+2-2",[0,5],24)
#pygame.image.save(expression.surface,'C:/Users/carls/desktop/test1.bmp')
#screen.fill((255,255,255))
#screen.blit(expression.surface,(0,0))
#pygame.display.update()
'''from math import ceil
for n in range(5,1000):
    font = pygame.freetype.Font(LATEX_FONT_PATH, n)
    e3,r3=font.render('1234567890',(0,0,0),(255,255,255))
    if e3.get_size()[1]!= ceil(0.7*(n+0.5)):
        print(n,e3.get_size()[1],ceil(0.7*(n+0.5)))'''
