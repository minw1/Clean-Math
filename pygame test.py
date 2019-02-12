import pygame
import pygame.freetype
import math
 
# Initialize the game engine
pygame.init()

FONT = pygame.freetype.Font("Futura.ttf", 24)

 
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

width = 400
height = 300

boxSideLength = 20
boxStrokeWidth = 1


celldimensions = [math.ceil(float(width)/20),math.ceil(float(height)/20)]



# Set the height and width of the screen
size = [width, height]
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
 
pygame.display.set_caption("Example code for the draw module")
 
#Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
 
while not done:
 
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)

    celldimensions = [math.ceil(float(width)/20),math.ceil(float(height)/20)]

    print(celldimensions)

     
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)
            width = event.w
            height = event.h
 
    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.
     
    # Clear the screen and set the screen background
    screen.fill(WHITE)

    #draw vertical lines
    vertLineOrigin = 0

    
    while(vertLineOrigin < width):
          pygame.draw.line(screen, BLACK, [vertLineOrigin, 0], [vertLineOrigin,height],boxStrokeWidth)
          vertLineOrigin += boxSideLength

    #use same process to draw horizontal lines
    horLineOrigin = 0
    while(horLineOrigin < height):
          pygame.draw.line(screen, BLACK, [0, horLineOrigin], [width,horLineOrigin],boxStrokeWidth)
          horLineOrigin += boxSideLength
 
    FONT.render_to(screen,(0,0),"CELL DIMENSIONS: ({},{})".format(celldimensions[0],celldimensions[1]),WHITE,BLACK)
    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()
 
# Be IDLE friendly
pygame.quit()
