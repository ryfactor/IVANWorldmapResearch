# -*- coding: utf-8 -*-
"""

  IVAN Worldmap Research
  Copyright (C) Ryan van Herel
  Released under the GNU General
  Public License

  See LICENSING which should be included
  along with this file for more details

  @author: fejoa

"""

from random import randint
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

class worldmap:
    def __init__(self, length, width, smooth, steps, GENERATE_CONTINENTS):
        self.__length = length
        self.__width = width
        self.__area = length * width
        self.__AltitudeBuffer = np.zeros((width, length))
        self.__OldAltitudeBuffer = np.zeros((width, length))
        self.__DisplayMap = np.zeros((width, length))
        self.__gen_initial_map(smooth, steps, GENERATE_CONTINENTS)
        
    def __gen_initial_map(self, smooth, steps, GENERATE_CONTINENTS):
        #create initial random map
        HYBRID = 2
        if GENERATE_CONTINENTS == HYBRID or GENERATE_CONTINENTS == 1:
            for x in range(self.__width):
                for y in range(self.__length):
                    self.__AltitudeBuffer[x][y] = (4000 - randint(0, 8000))
        if GENERATE_CONTINENTS == HYBRID or GENERATE_CONTINENTS == 0:
            #create "splodges"
            for x in range(self.__width/2):
                for y in range(self.__length/2):
                    self.__AltitudeBuffer[x][y] += (randint(0, x*y)) - 800
            for x in range(self.__width/2, self.__width):
                for y in range(self.__length/2, self.__length):
                    self.__AltitudeBuffer[x][y] += (randint(0, (self.__width-x)*(self.__length-y))) - 800
            for x in range(self.__width/2):
                for y in range(self.__length/2, self.__length):
                    self.__AltitudeBuffer[x][y] += (randint(0, (x)*(self.__length-y))) - 800
            for x in range(self.__width/2, self.__width):
                for y in range(self.__length/2):
                    self.__AltitudeBuffer[x][y] += (randint(0, (self.__width-x)*(y))) - 800
        
        if smooth == 1:
            self.__smooth_altitude(steps)
            
        print "DONE"

    def __quantize_grid(self):
        LAND = 1
        SEA = 0
        for x in range(self.__width):
            for y in range(self.__length):
                if self.__AltitudeBuffer[x][y] > 0.0:
                     self.__DisplayMap[x][y] = LAND
                else:
                     self.__DisplayMap[x][y] = SEA

    def __smooth_altitude(self, steps):
        for c in range(steps):
            #self.show_world()
            self.__plot_landsea(c, steps)
            for y in range(self.__length): 
                self.__safe_smooth(0, y)
            for x in range(1, self.__width - 1):
                self.__safe_smooth(x, 0)
                for y in range(1, self.__length - 1):
                    self.__fast_smooth(x, y)
                self.__safe_smooth(x, self.__length - 1)
            for y in range(self.__length):
                self.__safe_smooth(self.__width - 1, y)
        
        
    def __safe_smooth(self, x, y):
        HeightNear = 0
        SquaresNear = 0
        DirX = [ -1, -1, -1, 0, 0, 1, 1, 1 ]
        DirY = [ -1, 0, 1, -1, 1, -1, 0, 1 ]
        
        for d in range(0, 4):
            X = x + DirX[d]
            Y = y + DirY[d]
            if self.__is_valid_position(X, Y):
                HeightNear += self.__OldAltitudeBuffer[X][Y]
                SquaresNear += 1
            
        for d in range(4, 7):
            X = x + DirX[d]
            Y = y + DirY[d]
            if self.__is_valid_position(X, Y):
                HeightNear += self.__AltitudeBuffer[X][Y]
                SquaresNear += 1
        
        self.__OldAltitudeBuffer[x][y] = self.__AltitudeBuffer[x][y]
        self.__AltitudeBuffer[x][y] = HeightNear / SquaresNear
        
        
    def __fast_smooth(self, x, y):
        HeightNear = 0
        DirX = [ -1, -1, -1, 0, 0, 1, 1, 1 ]
        DirY = [ -1, 0, 1, -1, 1, -1, 0, 1 ]
        
        for d in range(0, 4):
            HeightNear += self.__OldAltitudeBuffer[x + DirX[d]][y + DirY[d]]
        for d in range(4, 7):
            HeightNear += self.__AltitudeBuffer[x + DirX[d]][y + DirY[d]]
        
        self.__OldAltitudeBuffer[x][y] = self.__AltitudeBuffer[x][y];
        self.__AltitudeBuffer[x][y] = HeightNear / 8;

    def __is_valid_position(self, X, Y):
        return ((X >= 0) and (Y >= 0) and (X < self.__width) and (Y < self.__length))
    
    def __plot_landsea(self, step, maxsteps):
        print "max altitude is %d", np.max(self.__AltitudeBuffer)
        print "min altitude is %d", np.min(self.__AltitudeBuffer)
        destination = str(r'c:\\picts\\%d'% step) + str(r'.png')
        self.__quantize_grid()
        fig = plt.figure()
        plt.imshow(self.__DisplayMap, interpolation='bilinear', origin='lower', cmap=cm.winter)
        CS = plt.contour(self.__DisplayMap, [0, 1], cmap=cm.winter)
        CB = plt.colorbar(CS, shrink=0.8, extend='both')
        l,b,w,h = plt.gca().get_position().bounds
        ll,bb,ww,hh = CB.ax.get_position().bounds
        CB.ax.set_position([ll, b+0.1*h, ww, h*0.8])  
        plt.savefig(destination, bbox_inches='tight')        
        #if step >= 9:
        #    plt.show()
       
       
       
# useage: worldmap(XSize, YSize, use smoothing? [Y/n], number of steps in smoothing, 0=single island 1=lots of continents 2=continent with islands)
world = worldmap(128, 128, 1, 10, 1)
