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
import numpy as np
#import matplotlib.pyplot as plt

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
bg_bridge = pygame.image.load('bridge01.jpg')
bg_bridge_lg = pygame.transform.scale(bg_bridge, (m.floor(800*1.35), m.floor(555*1.35)))
bg_bridge_lgrot = pygame.transform.rotate(bg_bridge_lg, 9)
sprite = pygame.image.load('sprite.png')
sprite_lg = pygame.transform.scale(sprite, (49,84))
circle = pygame.image.load('circle.png')
circle_sm = pygame.transform.scale(circle, (20, 20))
circle_xsm = pygame.transform.scale(circle, (6, 6))
hextile = pygame.image.load('hex.png')
#hextile_sm = pygame.transform.scale(hextile, (100, 60))
hextile_sm = pygame.transform.scale(hextile, (67, 80))

def gameloop():
    
    
    s = 40 #hex side length
    origin = (4*3*s, 2*m.sqrt(3)*s) #location of start hex (y,x)
    
    gameExit = False
    
    pw_loc =  origin
    
    def pawn(y,x):
        gameDisplay.blit(sprite_lg, (x-25,y-75))
    def gridmarker(y,x):
        gameDisplay.blit(circle_xsm, (x-3, y-3))
    def marker(y,x):
        gameDisplay.blit(circle_sm, (x-10,y-10))
    def hexx(y,x):
        gameDisplay.blit(hextile_sm, (x-33, y-40))
    
    while not gameExit:
    
        griddim = (m.ceil(gdisp.H/(s/2)), m.ceil(gdisp.W/(m.sqrt(3)*s)))
        gridpts = np.zeros((griddim[0], griddim[1], 2))
    
        for i in range(gridpts.shape[0]):
            for j in range(gridpts.shape[1]):
                gridpts[i,j,:] = [(i*1.5*s), j*m.sqrt(3)*s + (i%2)*m.sqrt(3)/2*s]
        
        mpos = pygame.mouse.get_pos()[::-1]
        y = mpos[0]
        x = mpos[1]
        marker(mpos[0], mpos[1])
        dist = np.sqrt(np.square(gridpts[:,:,0] - np.tile(y,griddim)) + np.square(gridpts[:,:,1] - np.tile(x,griddim)))
        minidx = np.where(dist==dist.min())
        minidx = (minidx[0][0], minidx[1][0])
        minloc = (gridpts[minidx[0],minidx[1],0], gridpts[minidx[0],minidx[1],1])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pw_loc = minloc
    
#            if event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_LEFT:
#                    x_change = -5
#                elif event.key == pygame.K_RIGHT:
#                    x_change = 5
#            if event.type == pygame.KEYUP:
#                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
#                    x_change = 0
    
            #print(event)
    
        gameDisplay.fill(white)
        gameDisplay.blit(bg_bridge_lgrot, (-130,-150))
        
        for i in range(gridpts.shape[0]):
            for j in range(gridpts.shape[1]):
                gridmarker(gridpts[i,j,0],gridpts[i,j,1])
        
        hexx(minloc[0], minloc[1])
        
        dy = gridpts[:,:,0] - np.tile(pw_loc[0], griddim)
        dx = gridpts[:,:,1] - np.tile(pw_loc[1], griddim)
        
        rgb_dist = np.zeros((3, griddim[0], griddim[1]))
        rgb_dist[0] = np.round((m.sqrt(3)/3*dx - dy/3)/s) #red
        rgb_dist[1] = np.round(-(m.sqrt(3)/3*dx + dy/3)/s) #green
        rgb_dist[2] = np.round(2/3*dy/s) #blue
        rgb_dist = np.max(np.abs(rgb_dist), axis=0)
        for tile in gridpts[np.where(np.logical_and(1<=rgb_dist, rgb_dist<=3))]:
            hexx(tile[0], tile[1])
        pawn(pw_loc[0], pw_loc[1])
        
        
#        rr = (m.sqrt(3)/3*x - y/3)/s
#        gg = -(m.sqrt(3)/3*x + y/3)/s
#        bb = 2/3*y/s
        
        #hexx(xx, yy)
        #hexx(yy + 3/2*s*bb, xx + m.sqrt(3)*s*(bb/2+rr))
    
        pygame.display.update()
        clock.tick(30)
        
    return 0

gameloop()
pygame.quit()
#quit()