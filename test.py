# -*- coding: utf-8 -*-
"""
Created on Thu May 24 08:56:07 2018

@author: ic_admin
"""

#Container for display parameters
class dispParms(object):
    def __init__(self):
        self.W = None
        self.H = None

import pygame
import math as m

pygame.init()

gdisp = dispParms()
gdisp.W = 800
gdisp.H = 600
gameDisplay = pygame.display.set_mode((gdisp.W,gdisp.H))
pygame.display.set_caption('Test Window')

black = (0,0,0)
white = (255,255,255)

car_width = 73

clock = pygame.time.Clock()

bg_grid = pygame.image.load('grid.png')
sprite = pygame.image.load('sprite.png')
sprite_lg = pygame.transform.scale(sprite, (49*2,84*2))
circle = pygame.image.load('circle.png')
circle_sm = pygame.transform.scale(circle, (20, 20))
hextile = pygame.image.load('hex.png')
hextile_sm = pygame.transform.scale(hextile, (100, 119))

def gameloop():
    
    s = 60 #hex side length
    origin = (300, 250) #location of hex (0,0,0)
    
    gameExit = False
    
    x =  (gdisp.W * 0.45)
    y = (gdisp.H * 0.8)
    x_change = 0
    car_speed = 0
    
    def pawn(x,y):
        gameDisplay.blit(sprite_lg, (x,y))
    def marker(x,y):
        gameDisplay.blit(circle_sm, (x-10,y-10))
    
    i = 0
    while not gameExit:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -5
                elif event.key == pygame.K_RIGHT:
                    x_change = 5
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0
    
            #print(event)
    
        gameDisplay.fill(white)
        #gameDisplay.blit(bg_grid, (0,0))
        
        mpos = pygame.mouse.get_pos()
        x = mpos[0]
        y = mpos[1]
        
#        rr = (m.sqrt(3)/3*x - y/3)/s
#        gg = -(m.sqrt(3)/3*x + y/3)/s
#        bb = 2/3*y/s
        
        rr = 0
        gg = 1
        bb = -1
        
        marker(mpos[0], mpos[1])
        gameDisplay.blit(hextile_sm, origin)
        xx = origin[0]
        yy = origin[1]
        gameDisplay.blit(hextile_sm, (xx + m.sqrt(3)*s*(bb/2+rr), yy + 3/2*s*bb))
        
        if x > gdisp.W - car_width or x < 0:
            gameExit = True
    
        pygame.display.update()
        clock.tick(30)
#        print(i)
#        i+=1

gameloop()
pygame.quit()
quit()