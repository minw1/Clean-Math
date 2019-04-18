import expression as xp
import settings as st
import pygame

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")

SQRT2 = 1.4142135623731

def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

DEFAULT_FONT_SIZE = 48
PARENTHESES_ADJUSTMENT = 0.05
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.4
VINCULUM_SIZE = 0.05

FONTS={}
IFONTS={}

class smartSurface:

    simpleOps = {'+','-','*'} 
    spacing = 10

    def __init__(self, exp, frac_depth=0, script_depth=0, op_depth=0): #depth is number of layers into generation we are. 
        st.lock.acquire()
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
        print(exp)
        if type(exp) == xp.NoOpExpression:
            if exp.strRep == "|":
                middleColor = [(st.fontColor[i]+st.backgroundColor[i])//2 for i in range(3)]
                self.surface,rect = font.render('|',middleColor,st.backgroundColor)
                self.hitboxes.append((self.surface.get_rect(),self,op_depth))
            else:
                self.surface,rect = font.render(exp.strRep,st.fontColor,st.backgroundColor)
                self.hitboxes.append((self.surface.get_rect(),self,op_depth))
            self.yline = self.surface.get_rect().height//2
        elif exp.op.strRep == "()":
            containedExp = exp.expList[0]
            firstSurface = smartSurface(containedExp, frac_depth, script_depth, op_depth+1)
            width, height = firstSurface.get_size()
            newFontSize=height*SQRT2+round(2*PARENTHESES_ADJUSTMENT*font_size)
            newFont = pygame.freetype.Font(LATEX_FONT_PATH, newFontSize)
            openParen, openRect = newFont.render("(",st.fontColor,st.backgroundColor)
            closeParen, closeRect = newFont.render(")",st.fontColor,st.backgroundColor)
            openWidth, openHeight = openParen.get_size()
            closeWidth, closeHeight = closeParen.get_size()
            endWidth = openWidth+width+closeWidth
            endHeight = max(openHeight, height, closeHeight)
            self.surface = pygame.Surface((endWidth,endHeight))
            self.surface.fill(st.backgroundColor)
            self.surface.blit(openParen,(0,(endHeight-openHeight)//2))
            self.surface.blit(closeParen,(endWidth-closeWidth,(endHeight-closeHeight)//2))
            expLocation = (openWidth, (endHeight-height)//2)
            self.surface.blit(firstSurface.surface, expLocation)
            self.hitboxes = self.hitboxes+firstSurface.translateHitboxes(expLocation,1)
            self.yline = endHeight//2
        elif exp.op.strRep in self.simpleOps:
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1)
            secondSurface = smartSurface(exp.expList[1], frac_depth, script_depth, op_depth+1)

            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()
            firstYline, secondYline = firstSurface.yline,secondSurface.yline

            character = '.' if exp.op.strRep == '*' else exp.op.strRep # we want multiplication to appear as cdots
            operatorSurface, operatorRect = font.render(character,st.fontColor,st.backgroundColor)
            operatorWidth, operatorHeight = operatorSurface.get_size()
            operatorYline = operatorHeight//2

            finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing
            finalYline = max(firstYline,secondYline)
            finalHeight = max(firstYline,secondYline) + max(firstHeight-firstYline,secondHeight-secondYline)


            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill(st.backgroundColor)
            self.surface.blit(firstSurface.surface, (0, finalYline - firstYline))
            self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,finalYline - secondYline))
            self.surface.blit(operatorSurface, (firstWidth+self.spacing,finalYline-operatorYline))

            self.hitboxes = firstSurface.translateHitboxes([0,finalYline-firstYline],1) + secondSurface.translateHitboxes([finalWidth-secondWidth,finalYline-secondYline],1)
            self.hitboxes += [(operatorSurface.get_rect().move(firstWidth+self.spacing,finalYline-operatorYline),exp,op_depth)]
            self.yline = finalYline

        elif exp.op.strRep == "^":
            firstSurface = smartSurface(exp.expList[0], frac_depth, script_depth, op_depth+1)
            secondSurface = smartSurface(exp.expList[1],frac_depth,script_depth+1, op_depth+1)
            firstWidth, firstHeight = firstSurface.get_size()
            secondWidth, secondHeight = secondSurface.get_size()
            firstYline, secondYline = firstSurface.yline,secondSurface.yline


            finalWidth = firstWidth + secondWidth
            finalHeight = firstHeight + secondYline
            self.yline = firstYline+secondYline

            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.fill(st.backgroundColor)
            self.surface.blit(firstSurface.surface, (0,secondYline))
            self.surface.blit(secondSurface.surface, (firstWidth,0))
            self.hitboxes = firstSurface.translateHitboxes([0,secondYline],1) + secondSurface.translateHitboxes([firstWidth,0],1)
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
            self.surface.fill(st.backgroundColor)
            numLocation = ((endWidth-numWidth)//2,0)
            denomLocation = ((endWidth-denomWidth)//2,endHeight-denomHeight)
            vincHeight = numHeight+round(FRAC_VERTICAL_TOLERANCE*font_size)
            self.surface.blit(numSurface.surface, numLocation)
            self.surface.blit(denomSurface.surface, denomLocation)
            pygame.draw.rect(self.surface, st.fontColor, (0,vincHeight,vinculumWidth,vinculumHeight))
            self.hitboxes = self.hitboxes+numSurface.translateHitboxes(numLocation,1)+denomSurface.translateHitboxes(denomLocation,1)
            self.yline = vincHeight + (vinculumHeight//2)
        elif exp.op.strRep == "{}":
            expression = exp.expList[0]
            otherSurf = smartSurface(expression, frac_depth, script_depth)
            self.surface = otherSurf.surface
            self.hitboxes = otherSurf.hitboxes
            self.yline = otherSurf.yline
        st.lock.release()

    def translateHitboxes(self,coordinates,op_depthAdd):
        newHitboxes = []
        for hb in self.hitboxes:
            rect, expression, op_depth = hb
            newHitboxes.append((rect.move(coordinates[0],coordinates[1]), expression, op_depth+op_depthAdd))
        return newHitboxes

    def get_at_position(self,coordinates):
        best_exp=None
        best_op_depth=0
        for hb in self.hitboxes:
            rect, expression, op_depth = hb
            if op_depth>best_op_depth and rect.collidepoint(coordinates): #if it's further in and the point is in the rect
                best_exp=expression
                best_op_depth = op_depth
        return best_exp

    def get_size(self):
        return self.surface.get_size()
