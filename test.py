# -*- coding: utf-8 -*-
"""
Created on Thu May 24 08:56:07 2018

@author: Kellan Moorse
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
import random
from time import time
from queue import Queue
#import matplotlib.pyplot as plt

pygame.init()

gdisp = DispParms()
gdisp.W = 800
gdisp.H = 600
gameDisplay = pygame.display.set_mode((gdisp.W,gdisp.H))
pygame.display.set_caption('Test Window')

white = (255,255,255)

clock = pygame.time.Clock()

def gameloop(hexmap='load'):
    
    try:

        gameExit = False
        
        #Define hex grid instance and parameters
        hexg = HexGrid()
        hexg.s = 40 #hex side length
        hexg.aspect = 0.5
        
        #Load or generate hexmap tile properties
        if hexmap=='load':
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
        elif hexmap=='blank':
            hexg.griddim = (m.ceil(gdisp.H/(hexg.s/2)), m.ceil(gdisp.W/(m.sqrt(3)*hexg.s)))
            hexg.gridpts = np.zeros((hexg.griddim[0], hexg.griddim[1], 3))
            for i in range(hexg.gridpts.shape[0]):
                    for j in range(hexg.gridpts.shape[1]):
                        hexg.gridpts[i,j,:] = [0.5*(i*1.5*hexg.s), j*m.sqrt(3)*hexg.s + (i%2)*m.sqrt(3)/2*hexg.s, 1]        
        
        #Place test pawns at start positions
        engmt = Engagement(hexg)
        
        origin,_ = hexg.nearest_hex(500, 250)
        char1 = Char(gameDisplay, origin, 'Char1', engmt)
        engmt.add_unit(char1)
        origin,_ = hexg.nearest_hex(100, 700)
        char2 = Char(gameDisplay, origin, 'Char2', engmt)
        engmt.add_unit(char2)
        origin,_ = hexg.nearest_hex(100, 600)
        char3 = Char(gameDisplay, origin, 'Char3', engmt)
        engmt.add_unit(char3)
        
        engmt.init_init()
        
        hexg.engmt = engmt
        
        #initialize pointer mode
        point_mode = 'move'
        
        #Open main game loop
        while not gameExit:
            
            #Draw background
            hexg.render()

            #Check mouse position
            mpos_old = hexg.mpos
            hexg.mpos = pygame.mouse.get_pos()[::-1]
            hexg.mpos = (hexg.mpos[0]-hexg.sc_off[0], hexg.mpos[1]-hexg.sc_off[1])
            mpos_hex, mpos_hidx = hexg.nearest_hex(hexg.mpos[0], hexg.mpos[1])
            
            #Draw hexmap
            hexg.hexmap()
            
            #Draw movement range
            if point_mode == 'move' and engmt.activeunit.action == "move:input":
                hexg.disp_range(engmt.activeunit.loc, engmt.activeunit.mvmt)
            elif point_mode == 'move' and engmt.activeunit.action == "atk:input":
                hexg.disp_range(engmt.activeunit.loc, engmt.activeunit.atkrng, blktype="atk")
            else: hexg.tiles = np.empty([0,3])
            
            #Check for input events
            for event in pygame.event.get():
                
                #On EXIT, quit game
                if event.type == pygame.QUIT:
                    gameExit = True
                 
                #On LEFT CLICK (down), start timer
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        hexg.mouse_hold = True
                        t_click = time()
                
                #On LEFT CLICK (release), move char or paint tile
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        hexg.mouse_hold = False
                        t_click = time() - t_click
                        if t_click < 0.2: #If click is short
                            if point_mode == 'move' and mpos_hex in hexg.tiles:
                                engmt.activeunit.path = hexg.pathfind_bf(engmt.activeunit.loc, mpos_hex)
                                dist = len(engmt.activeunit.path)
                                engmt.activeunit.sp[1] -= 10+dist*5
                                engmt.activeunit.action = "move:anim"
                                #engmt.activeunit.loc = mpos_hex
                                #engmt.next()
                            if point_mode == 'paint:red':
                                hexg.gridpts[mpos_hidx[0], mpos_hidx[1],2] = 1
                            if point_mode == 'paint:blue':
                                hexg.gridpts[mpos_hidx[0], mpos_hidx[1],2] = 2
                
                if event.type == pygame.KEYDOWN:
                    #On SPACEBAR, change pointer mode
                    if event.key == 32:
                        if point_mode == 'move': point_mode = 'paint:red'
                        elif point_mode == 'paint:red': point_mode = 'paint:blue'
                        elif point_mode == 'paint:blue': point_mode = 'move'
                    #On M, begin movement input
                    if event.key == 109: engmt.activeunit.action = "move:input"
                    #On A, begin attack input
                    if event.key == 97: engmt.activeunit.action = "atk:input"
                    #On T, reset screen offset target to (0,0)
                    if event.key == 116: hexg.sc_target = (0,0)
                    #On ESC, exit game
                    if event.key == 27: gameExit = True
                        
                    print(event)
            
            #Draw pointer at nearest hex
            if engmt.activeunit.action == "move:input":
                hexg.cursor(mpos_hex[0]+hexg.sc_off[0], mpos_hex[1]+hexg.sc_off[1])
            hexg.pointer(hexg.mpos[0]+hexg.sc_off[0],hexg.mpos[1]+hexg.sc_off[1],point_mode)
            if engmt.activeunit.action == "move:input" and mpos_hex in hexg.path_check2(engmt.activeunit.loc, engmt.activeunit.mvmt):
                for hexx in hexg.pathfind_bf(engmt.activeunit.loc, mpos_hex):
                    hexg.cursor_mini(hexx[0]+hexg.sc_off[0], hexx[1]+hexg.sc_off[1])
        
            #Draw Characters
            engmt.render()
        
            pygame.display.update()
            clock.tick(30)
        
            if hexg.mouse_hold:
                mpos_off = (mpos_old[0] - hexg.mpos[0], mpos_old[1] - hexg.mpos[1])
                if np.linalg.norm(mpos_off) > 0:
                    hexg.sc_off = (hexg.sc_off[0] - mpos_off[0], hexg.sc_off[1] - mpos_off[1])
                    hexg.sc_target = hexg.sc_off
                    hexg.mpos = (hexg.mpos[0] + mpos_off[0], hexg.mpos[1] + mpos_off[1])
        
        #Save hexmap
        if hexmap=='load':
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
        self.engmt = None
        self.sc_off = (0,0)
        self.sc_target = (0,0)
        self.mouse_hold = False
        self.tiles = None
        self.mpos = None
        
        self.bgfile = 'bridge01.jpg'
        self.bgimg = pygame.image.load('bridge01.jpg')
        self.bgimg = pygame.transform.scale(self.bgimg, (m.floor(800*1.35), m.floor(555*1.35)))
        self.bgimg = pygame.transform.rotate(self.bgimg, 9)
        
        self.hextile = pygame.image.load('hex.png')
        self.hextile = pygame.transform.scale(self.hextile, (67, 38))
        self.hexpoint = pygame.image.load('hex2.png')
        self.hexpoint = pygame.transform.scale(self.hexpoint, (67, 38))

        self.circle_r = pygame.image.load('circle-r.png')
        self.circle_rsm = pygame.transform.scale(self.circle_r, (6, 6))
        self.circle_rlg = pygame.transform.scale(self.circle_r, (10, 10))
        self.circle_b = pygame.image.load('circle-b.png')
        self.circle_bsm = pygame.transform.scale(self.circle_b, (6, 6))
        self.circle_blg = pygame.transform.scale(self.circle_b, (10, 10))
        
    
    #Return all tiles within <dist> tiles of <origin>, ignoring obstacles
    def dist_check(self, origin, dist, blktype="move_gnd"):
        dy = (self.gridpts[:,:,0] - np.tile(origin[0], self.griddim))*2
        dx = self.gridpts[:,:,1] - np.tile(origin[1], self.griddim)
        
        rgb_dist = np.zeros((3, self.griddim[0], self.griddim[1]))
        rgb_dist[0] = np.round((m.sqrt(3)/3*dx - dy/3)/self.s) #red
        rgb_dist[1] = np.round(-(m.sqrt(3)/3*dx + dy/3)/self.s) #green
        rgb_dist[2] = np.round(2/3*dy/self.s) #blue
        rgb_dist = np.max(np.abs(rgb_dist), axis=0)
        
        tiles = self.gridpts[np.where(rgb_dist == dist)]
        if blktype in ["move_gnd", "move_air", "atk"]:
            tiles = tiles[np.where(tiles[:,2]==1)]
        if blktype in ["move_gnd", "move_air"]:
            tiles = np.vstack(row for row in tiles if not np.all(self.engmt.loclist==row[:2], 1).any())
        
        return tiles
    
    #Return all tiles within <dist> tiles of <origin>, avoiding obstacles
    def path_check(self, origin, dist, blktype="move_gnd"):
        tiles = self.dist_check(origin, 1)
        tiles_new = tiles
        for i in range(dist-1):
            tiles_check = tiles_new
            tiles_new = np.empty((0,3))
            for tile in tiles_check:
                tiles_new = np.append(tiles_new, self.dist_check(tile[:2], 1, blktype),0)
            tiles = np.append(tiles, tiles_new, 0)
            tiles = tiles[np.where(np.any(tiles[:,:2]!=origin, axis=1))]
        tiles = np.unique(tiles, axis=0)
  
        return tiles
    
    #Return all tiles within <dist> tiles of <origin>, avoiding obstacles
    def path_check2(self, origin, dist, blktype="move_gnd"):
        visited = set()
        visited.add(origin)
        fringes = [[]]
        fringes[0].append(list(origin))
        
        for k in range(1,dist+1):
            fringes.append([])
            for hexx in fringes[k-1]:
                for neighbor in self.dist_check(hexx, 1, blktype)[:,:2]:
                    neighbor = tuple(neighbor)
                    if neighbor not in visited:
                        visited.add(neighbor)
                        fringes[k].append(neighbor)
        
        visited.remove(origin)
        return visited
    
    #Display hexes within a given distance
    def disp_range(self, origin, dist, blktype="move_gnd"):
        self.tiles = self.path_check2(origin, dist, blktype)
        for tile in self.tiles:
            self.hexx(tile[0]+self.sc_off[0], tile[1]+self.sc_off[1])
    
    #Find hex path from <origin> to <target> via breadth-first search
    def pathfind_bf(self, origin, target):
        frontier = Queue()
        frontier.put(origin)
        came_from = {}
        came_from[origin] = None
        
        #Generate path map
        while not frontier.empty():
            current = frontier.get()
            if current == target: break
            for hexx in self.dist_check(current, 1)[:,:2]:
                hexx = tuple(hexx)
                if hexx not in came_from:
                    frontier.put(hexx)
                    came_from[hexx] = current
        
        #Backpropagate path from target to origin  
        current = target
        path = []
        while current != origin:
            path.append(current)
            current = came_from[current]
        #path.append(origin)
        path.reverse()
        
        return path
    
    #Generate blank hexmap
    def hexmap(self):
        for i in range(self.gridpts.shape[0]):
                for j in range(self.gridpts.shape[1]):
                    if self.gridpts[i,j,2] == 1:
                        self.gridmarker(self.gridpts[i,j,0]+self.sc_off[0], self.gridpts[i,j,1]+self.sc_off[1], 'r')
                    elif self.gridpts[i,j,2] == 2:
                        self.gridmarker(self.gridpts[i,j,0]+self.sc_off[0], self.gridpts[i,j,1]+self.sc_off[1], 'b')
    
    #Initialize draw functions
    def hexx(self, y, x):
        gameDisplay.blit(self.hextile, (x-33, y-20))
    def cursor(self, y, x):
        gameDisplay.blit(self.hexpoint, (x-33, y-20))
    def cursor_mini(self, y, x):
        gameDisplay.blit(pygame.transform.scale(self.hexpoint, (34,20)), (x-17, y-11))
    def pointer(self, y,x,point_mode):
        if point_mode=='paint:red': gameDisplay.blit(self.circle_rlg, (x-5, y-5))
        if point_mode=='paint:blue': gameDisplay.blit(self.circle_blg, (x-5, y-5))
    def gridmarker(self, y, x, color):
        if color=='r': gameDisplay.blit(self.circle_rsm, (x-3, y-3))
        if color=='b': gameDisplay.blit(self.circle_bsm, (x-3, y-3))
    
    #Find position and index of the hex nearest to the y-x input coordinates
    def nearest_hex(self, y, x):
        dist = np.sqrt(np.square(self.gridpts[:,:,0] - np.tile(y,self.griddim)) + np.square(self.gridpts[:,:,1] - np.tile(x,self.griddim)))
        mpos_hidx = np.where(dist==dist.min())
        mpos_hidx = (mpos_hidx[0][0], mpos_hidx[1][0])
        mpos_hex = (self.gridpts[mpos_hidx[0],mpos_hidx[1],0], self.gridpts[mpos_hidx[0],mpos_hidx[1],1])
        
        return mpos_hex, mpos_hidx

    def render(self):
        #Move screen toward target
        if np.linalg.norm(tplop(self.sc_off,self.sc_target,"sub"))>25:
            resid = tplop(self.sc_off, self.sc_target, "sub")
            self.sc_off = tplop(self.sc_off, (resid[0]/10, resid[1]/10), "sub")
        
        #Draw background
        gameDisplay.fill((255,255,255))
        gameDisplay.blit(self.bgimg, (-120+self.sc_off[1],-150+self.sc_off[0]))
        

class Engagement(HexGrid):
    
    def __init__(self, hexg):
        self.unitlist = np.empty((0,1))
        self.hexg = hexg
        
        self.rect_r = pygame.image.load('rect-r.png')
        self.rect_r = pygame.transform.scale(self.rect_r, (50, 8))
        self.rect_y = pygame.image.load('rect-y.png')
        self.rect_y = pygame.transform.scale(self.rect_y, (50, 8))
        
    def health_bar(self, y, x, pct):
        bar = pygame.transform.scale(self.rect_r, (m.floor(50*pct/100), 6))
        gameDisplay.blit(bar, (x-25+self.hexg.sc_off[1], y-3+self.hexg.sc_off[0]))
    def stamina_bar(self, y, x, pct):
        bar = pygame.transform.scale(self.rect_y, (m.floor(50*pct/100), 6))
        gameDisplay.blit(bar, (x-25+self.hexg.sc_off[1], y+5+self.hexg.sc_off[0]))
    
    def add_unit(self, char):
        self.unitlist = np.append(self.unitlist, char)
    
    #Check initiatives and activate first character
    def init_init(self):
        self.update_init()
        self.turncount = -1
        self.next()
        self.check_locs()
    
    #Update and print initiative order
    def update_init(self):
        self.initlist = np.empty([0])
        for unit in self.unitlist:
            self.initlist = np.append(self.initlist, unit.initiative)
        self.unitlist = self.unitlist[np.flipud(np.argsort(self.initlist))]
        print('----------')
        for unit in self.unitlist:
            print('%s: %i' % (unit.name, unit.initiative))
        print('----------')
        
    #Update unit location list
    def check_locs(self):
        self.loclist = np.zeros((0,2))
        for unit in self.unitlist:
            self.loclist = np.append(self.loclist, np.array([unit.loc]), 0)
    
    #Draw all characters
    def render(self):
        if self.activeunit.action == "move:anim":
            if len(self.activeunit.path) == 0:
                self.activeunit.action = "move:input"
                self.next()
            else:
                to_target = tplop(self.activeunit.path[0], self.activeunit.loc, "sub")
                if np.linalg.norm(to_target) < 5:
                    self.activeunit.loc = self.activeunit.path[0]
                    self.activeunit.path = self.activeunit.path[1:]
                else:
                    self.activeunit.loc = tplop(self.activeunit.loc, tplop(to_target, 1/np.linalg.norm(to_target)*5, "mult"), "add")
                self.activeunit
        
        self.check_locs()
        self.hexg.cursor(self.activeunit.loc[0]+self.hexg.sc_off[0], self.activeunit.loc[1]+self.hexg.sc_off[1])
        for unit in self.unitlist[np.argsort(self.loclist[:,0])]:
            unit.anim((unit.loc[0]+self.hexg.sc_off[0], unit.loc[1]+self.hexg.sc_off[1]))
            #Update displayed hp & sp toward actual
            if 0 < m.fabs(unit.hp[1]-unit.hp[0]) <= 5: unit.hp[0] = unit.hp[1]
            elif 5 < m.fabs(unit.hp[1]-unit.hp[0]): unit.hp[0] += 5*np.sign(unit.hp[1]-unit.hp[0])
            if 0 < m.fabs(unit.sp[1]-unit.sp[0]) <= 5: unit.sp[0] = unit.sp[1]
            elif 5 < m.fabs(unit.sp[1]-unit.sp[0]): unit.sp[0] += 5*np.sign(unit.sp[1]-unit.sp[0])
    
    #Move to next unit in initiative order
    def next(self):
        if self.turncount<self.unitlist.size-1:
            self.turncount += 1
        else: self.turncount = 0
        self.activeunit = self.unitlist[self.turncount]
        self.hexg.sc_target = tplop(tplop(self.activeunit.loc,-1,"mult"), (400,400), "add")
        self.activeunit.update_sp(self.activeunit.sp[1]/10)
        self.activeunit.action = "menu:input"
        print('Active: %s' % self.activeunit.name)

class Char(Engagement):
    
    #Initialize character object
    def __init__(self, disp, loc, name, engmt):
        self.name = name
        self.disp = disp
        self.loc = loc
        self.engmt = engmt
        self.initiative = random.randint(1,21) #Randomize initiative order
        self.frameidx = random.randint(1,15) #Randomize frame offset
        self.mvmt = 3
        self.atkrng = 1
        self.action = "menu:input"
        self.path = []
        self.hp = [100,100,100] #[display, actual, maximum]
        self.sp = [100,100,100]
        
        self.pawnfile = 'sprite-sheet.png'
        self.pawnsheet = pygame.image.load(self.pawnfile)
        self.pawndims = (self.pawnsheet.get_width()*3, self.pawnsheet.get_height()*3)
        self.pawnsheet = pygame.transform.scale(self.pawnsheet, (self.pawndims[0], self.pawndims[1]))
        self.pawn = pygame.Surface((60, self.pawndims[1]), pygame.SRCALPHA)
    
    def update_hp(self, change):
        self.hp[1] += change
        if self.hp[1]>self.hp[2]: self.hp[1]=self.hp[2]
        elif self.hp[1]<0: self.hp[1]=0
        
    def update_sp(self, change):
        self.sp[1] += change
        if self.sp[1]>self.sp[2]: self.sp[1]=self.sp[2]
        elif self.sp[1]<0: self.sp[1]=0
    
    #Cycle through animation frames
    def anim(self, loc, action='stand'):
        self.pawn.fill(pygame.Color(0,0,0,0))
        self.pawn.blit(self.pawnsheet, (0,0), (0+60*m.floor(self.frameidx/5),0,self.pawndims[1],self.pawndims[0]))
        self.disp.blit(self.pawn,(loc[1]-25,loc[0]-95))
        self.engmt.health_bar(self.loc[0], self.loc[1], self.hp[0]/self.hp[2]*100)
        self.engmt.stamina_bar(self.loc[0], self.loc[1], self.sp[0]/self.sp[2]*100)
        
        #Increment or loop frame counter
        if self.frameidx < 14: self.frameidx += 1
        else: self.frameidx = 0

#Perform an operation on one or two tuples
def tplop(a,b,op):
    if (op=="add" or op=="sub") and (len(a) != len(b)):
        print("For add/subtract, input tuples must be of equivalent length")
        return None
    if op=="add": c = tuple(a[i]+b[i] for i in range(len(a)))
    elif op=="sub": c = tuple(a[i]-b[i] for i in range(len(a)))
    if op=="mult": c = tuple(a[i]*b for i in range(len(a)))

    return c

e = gameloop(hexmap='load')
pygame.quit()
#quit()