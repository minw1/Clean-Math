import expToSurface as exs
import expression as xp
import RPNtoEXP as rte
import pygame
import pygame.freetype
import time


junk,toDraw = rte.RPNtoEXP(["4","2","3","+","^"])
surface = exs.smartSurface(toDraw)
pygame.init()
screen = pygame.display.set_mode([400,300], pygame.RESIZABLE)
clock = pygame.time.Clock()
currentTime = time.clock()
running = True
while running:
        clock.tick(20)
        currentTime = time.clock()
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False

        screen.blit(surface.surface,(0,0))
        pygame.display.flip()
pygame.quit()
