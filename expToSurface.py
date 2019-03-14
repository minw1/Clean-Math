import expression as xp
import settings as st

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")



def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

DEFAULT_FONT_SIZE = 48
PARENTHESES_ADJUSTMENT = 0.25
FRAC_ADJUSTMENT = 0.3
FRAC_VERTICAL_TOLERANCE = 0.4
VINCULUM_SIZE = 0.05

class smartSurface:

    simpleOps = {'+','-'} #'*' will appear as a cdot
    spacing = 10

    def __init__(self, exp, frac_depth, script_depth): #depth is number of layers into generation we are. 
    	self.surface = None
    	self.hitboxes = [] #(rect, self.exp)
    	self.font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
    	self.font = pygame.freetype.Font(LATEX_FONT_PATH, font_size)
    	self.iFont = pygame.freetype.Font(LATEX_iFONT_PATH, font_size)

    	if exp.op.strRep == "()":
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
    	elif exp.op.strRep in simpleOps:
    	elif exp.op.strRep == "^":
    	elif exp.op.strRep == "frac":
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
            self.hitboxes = self.hitboxes+numSurface.translateHitboxes(numLocation)
                                         +denomSurface.translateHitboxes(denomLocation)
    	elif exp.op.strRep == "*":

    def translateHitboxes(self,coordinates):
        newHitboxes = []
        for hb in self.hitboxes:
            rect, expression = hb
            newHitboxes.append((rect.move(coordinates[0],coordinates[1]), expression))
        return newHitboxes

    def get_size(self):
        return self.surface.get_size()

