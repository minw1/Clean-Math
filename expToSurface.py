import expression as xp
import settings as st
import pygame.freetype
import pygame

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")

SQRT2 = 1.41421356237

def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

DEFAULT_FONT_SIZE = 48
PARENTHESES_ADJUSTMENT = 0.25
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.4
VINCULUM_SIZE = 0.05

class smartSurface:

    simpleOps = {'+','-','*'} 
    spacing = 10

    def __init__(self, exp, frac_depth=0, script_depth=0): #depth is number of layers into generation we are. 
        st.lock.acquire()
        self.surface = None
        self.hitboxes = [] #(rect, self.exp)
        self.font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
        self.font = pygame.freetype.Font(LATEX_FONT_PATH, self.font_size)
        self.iFont = pygame.freetype.Font(LATEX_iFONT_PATH, self.font_size)
        if exp.op == "()":
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth)
            width, height = firstSurface.get_size()
            newFontSize=height*SQRT2+round(2*PARENTHESES_ADJUSTMENT*font_size)
            newFont = pygame.freetype.Font(LATEX_FONT_PATH, newFontSize)
            openParen, openRect = newFont.render("(")
            closeParen, closeRect = newFont.render(")")
            openWidth, openHeight = openParen.get_size()
            closeWidth, closeHeight = closeParen.get_size()
            endWidth = openWidth+width+closeWidth
            endHeight = max(openHeight, height, closeHeight)
            self.surface = pygame.Surface(endWidth,endHeight)
            self.surface.fill((255,255,255))
            self.surface.blit(openParen,(0,(endHeight-openHeight)//2))
            self.surface.blit(closeParen,(0,endWidth-closeWidth,(endHeight-closeHeight)//2))
            expLocation = (openWidth, (endHeight-height)//2)
            self.surface.blit(firstSurface.surface, expLocation)
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLocation)
        elif exp.op in self.simpleOps:

            firstSurface = smartSurface(exp.expList[0])
            secondSurface = smartSurface(exp.expList[1])

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()

            operatorSurface, operatorRect = self.font.render(exp.op,st.fontColor)
            operatorWidth, operatorHeight = operatorSurface.get_size()

            finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing
            finalHeight = max(firstHeight,secondHeight,operatorHeight)
            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.blit(firstSurface.surface, (0,(finalHeight-firstHeight)//2))
            self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,(finalHeight-secondHeight)//2))
            self.surface.blit(operatorSurface, (firstWidth+self.spacing,(finalHeight-operatorHeight)//2))
            self.hitboxes = firstSurface.translateHitboxes([0,(finalHeight-firstHeight)//2]) + secondSurface.translateHitboxes([finalWidth-secondWidth,(finalHeight-secondHeight)//2])
            self.hitboxes += [(operatorSurface.get_rect().move(firstWidth+self.spacing,(finalHeight-operatorHeight)//2),exp)]
        elif exp.op == "^":
            firstSurface = smartSurface(exp.expList[0])
            secondSurface = smartSurface(exp.expList[1],frac_depth,script_depth+1)
            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()
            finalWidth = firstWidth + secondWidth
            finalHeight = firstHeight + secondHeight//2
            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.blit(firstSurface.surface, (0,secondHeight//2))
            self.surface.blit(secondSurface.surface, (firstWidth,0))
            self.hitboxes = firstSurface.translateHitboxes([0,(finalHeight-firstHeight)//2]) + secondSurface.translateHitboxes([finalWidth-secondWidth,(finalHeight-secondHeight)//2])
        elif exp.op == "frac":
            numeratorExp = exp.expList[0]
            denominatorExp = exp.expList[1]
            numSurface = smartSurface(numeratorExp, frac_depth+1, script_depth)
            denomSurface = smartSurface(denominatorExp, frac_depth+1, script_depth)
            numWidth, numHeight = numSurface.get_size()
            denomWidth, denomHeight = denomSurface.get_size()
            vinculumWidth = max(numWidth, denomWidth)+round(2*FRAC_ADJUSTMENT*font_size)
            vinculumHeight = round(VINCULUM_SIZE*font_size)
            endWidth = vinculumWidth
            endHeight = numHeight + vinculumHeight + denomHeight + round(2*FRAC_VERTICAL_TOLERANCE*font_size)
            self.surface = pygame.Surface(endWidth, endHeight)
            self.surface.fill((255,255,255))
            numLocation = ((endWidth-numWidth)//2,0)
            denomLocation = ((endWidth-denomWidth)//2,endHeight-denomHeight)
            vincHeight = numHeight+round(FRAC_VERTICAL_TOLERANCE*font_size)
            self.surface.blit(numSurface.surface, numLocation)
            self.surface.blit(denomSurface.surface, denomLocation)
            pygame.draw.rect(self.surface, (0,0,0), (0,vincHeight,vinculumWidth,vinculumHeight))
            self.hitboxes = self.hitboxes+numSurface.translateHitboxes(numLocation)+denomSurface.translateHitboxes(denomLocation)
        elif exp.op == "none":
            self.surface,rect = self.font.render(exp.expList[0],st.fontColor)
            self.hitboxes += [(self.surface.get_rect(),str(exp.expList[0]))]
        st.lock.release()

    def translateHitboxes(self,coordinates):
        newHitboxes = []
        print (self.hitboxes)
        for hb in self.hitboxes:
            newHitboxes.append((hb[0].move(coordinates[0],coordinates[1]), hb[1]))
        return newHitboxes

    def get_size(self):
        return self.surface.get_size()


