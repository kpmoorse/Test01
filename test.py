# -*- coding: utf-8 -*-
"""
Created on Thu May 24 08:56:07 2018

@author: ic_admin
"""

#Container for display parameters
class DispParms(object):
    def __init__(self):
        self.W = None
        self.H = None

import pygame
import math as m
import numpy as np
import traceback
import csv
#import matplotlib.pyplot as plt

pygame.init()

gdisp = DispParms()
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

circle_r = pygame.image.load('circle-r.png')
circle_rsm = pygame.transform.scale(circle_r, (6, 6))
circle_rlg = pygame.transform.scale(circle_r, (10, 10))
circle_b = pygame.image.load('circle-b.png')
circle_bsm = pygame.transform.scale(circle_b, (6, 6))
circle_blg = pygame.transform.scale(circle_b, (10, 10))

hextile = pygame.image.load('hex.png')
hextile_sm = pygame.transform.scale(hextile, (67, 38))

def gameloop():
    
    try:

        gameExit = False
        
        #Define hex grid instance and parameters
        hexg = HexGrid()
        hexg.s = 40 #hex side length
        hexg.aspect = 0.5
        
#        hexg.griddim = (m.ceil(gdisp.H/(hexg.s/2)), m.ceil(gdisp.W/(m.sqrt(3)*hexg.s)))
#        hexg.gridpts = np.zeros((hexg.griddim[0], hexg.griddim[1], 3))
#        for i in range(hexg.gridpts.shape[0]):
#                for j in range(hexg.gridpts.shape[1]):
#                    hexg.gridpts[i,j,:] = [0.5*(i*1.5*hexg.s), j*m.sqrt(3)*hexg.s + (i%2)*m.sqrt(3)/2*hexg.s, 1]
        
        #Open hexmap file and read tile values
        with open('bridge_hexmap.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            rowidx = -1
            for row in reader:
                if rowidx == -1:
                    hexg.griddim = np.array(row).astype(int)
                    hexg.gridpts = np.zeros((hexg.griddim[0], hexg.griddim[1], 3))
                else:
                    i = m.floor(rowidx/hexg.griddim[1])
                    j = rowidx%hexg.griddim[1]
                    hexg.gridpts[i,j] = np.array(row).astype(float)
                rowidx += 1
        
        #Place test pawn at start position
        origin = (4*3*hexg.s, 2*m.sqrt(3)*hexg.s) #location of start hex (y,x)
        pw_loc =  origin
        
        #Initialize graphic objects
        def pawn(y,x):
            gameDisplay.blit(sprite_lg, (x-25,y-75))
        def gridmarker(y,x,color):
            if color=='r': gameDisplay.blit(circle_rsm, (x-3, y-3))
            if color=='b': gameDisplay.blit(circle_bsm, (x-3, y-3))
        def pointer(y,x,point_mode):
            if point_mode=='paint:red': gameDisplay.blit(circle_rlg, (x-5, y-5))
            if point_mode=='paint:blue': gameDisplay.blit(circle_blg, (x-5, y-5))
        def hexx(y,x):
            gameDisplay.blit(hextile_sm, (x-33, y-20))
        
        #initialize pointer mode
        point_mode = 'move'
        
        #Open main game loop
        while not gameExit:
            
            
            mpos = pygame.mouse.get_pos()[::-1]
            minloc, minidx = hexg.xy_to_hex(mpos[0], mpos[1])
            
            
        
            gameDisplay.fill(white)
            gameDisplay.blit(bg_bridge_lgrot, (-130,-150))
            
            for i in range(hexg.gridpts.shape[0]):
                for j in range(hexg.gridpts.shape[1]):
                    if hexg.gridpts[i,j,2] == 1:
                        gridmarker(hexg.gridpts[i,j,0],hexg.gridpts[i,j,1], 'r')
                    elif hexg.gridpts[i,j,2] == 2:
                        gridmarker(hexg.gridpts[i,j,0],hexg.gridpts[i,j,1], 'b')
            
            hexx(minloc[0], minloc[1])
            
            # tiles = path_check(4, pw_loc, hexg.gridpts, hexg.griddim, s)
            if point_mode == 'move':
                tiles = hexg.path_check(4, pw_loc)
                for tile in tiles:
                    hexx(tile[0], tile[1])
                pointer(mpos[0],mpos[1],point_mode)
            else: tiles = np.empty([0,3])
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if point_mode == 'move' and np.all(tiles[:,:2]==minloc, axis=1).any():
                            pw_loc = minloc
                        if point_mode == 'paint:red':
                            hexg.gridpts[minidx[0],minidx[1],2] = 1
                        if point_mode == 'paint:blue':
                            hexg.gridpts[minidx[0],minidx[1],2] = 2
                if event.type == pygame.KEYDOWN:
                    if event.key == 32:
                        if point_mode == 'move': point_mode = 'paint:red'
                        elif point_mode == 'paint:red': point_mode = 'paint:blue'
                        elif point_mode == 'paint:blue': point_mode = 'move'
                
            pawn(pw_loc[0], pw_loc[1])
        
            pygame.display.update()
            clock.tick(30)
        
        with open('bridge_hexmap.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(hexg.griddim)
            for i in range(hexg.griddim[0]):
                for j in range(hexg.griddim[1]):
                    writer.writerow(hexg.gridpts[i,j])
            
    except Exception as e:
        traceback.print_exc()
        return e
        
    return 0

class HexGrid(object):
    
    #Initialize instance attributes
    def __init__(self):
        self.s = None
        self.aspect = None
        self.gridpts = None
        self.griddim = None
    
    #Return all tiles within <dist> tiles of <origin>, ignoring obstacles
    def dist_check(self, dist, origin, blocked = True):
        dy = (self.gridpts[:,:,0] - np.tile(origin[0], self.griddim))*2
        dx = self.gridpts[:,:,1] - np.tile(origin[1], self.griddim)
        
        rgb_dist = np.zeros((3, self.griddim[0], self.griddim[1]))
        rgb_dist[0] = np.round((m.sqrt(3)/3*dx - dy/3)/self.s) #red
        rgb_dist[1] = np.round(-(m.sqrt(3)/3*dx + dy/3)/self.s) #green
        rgb_dist[2] = np.round(2/3*dy/self.s) #blue
        rgb_dist = np.max(np.abs(rgb_dist), axis=0)
        
        tiles = self.gridpts[np.where(rgb_dist == dist)]
        if blocked:
            tiles = tiles[np.where(tiles[:,2]==1)]
        
        return tiles
    
    #Return all tiles within <dist> tiles of <origin>, avoiding obstacles
    def path_check(self, dist, origin, blocked = True):
        tiles = self.dist_check(1, origin)
        tiles_new = tiles
        for i in range(dist-1):
            tiles_check = tiles_new
            tiles_new = np.empty((0,3))
            for tile in tiles_check:
                tiles_new = np.append(tiles_new, self.dist_check(1, tile[:2]),0)
            tiles = np.append(tiles, tiles_new, 0)
            tiles = tiles[np.where(np.any(tiles[:,:2]!=origin, axis=1))]
        tiles = np.unique(tiles, axis=0)
  
        return tiles
    
    def xy_to_hex(self, y, x):
        dist = np.sqrt(np.square(self.gridpts[:,:,0] - np.tile(y,self.griddim)) + np.square(self.gridpts[:,:,1] - np.tile(x,self.griddim)))
        minidx = np.where(dist==dist.min())
        minidx = (minidx[0][0], minidx[1][0])
        minloc = (self.gridpts[minidx[0],minidx[1],0], self.gridpts[minidx[0],minidx[1],1])
        
        return minloc, minidx
    

e = gameloop()
pygame.quit()
#quit()