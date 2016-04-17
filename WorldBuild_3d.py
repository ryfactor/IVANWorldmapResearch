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

import os
from random import randint
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import axes3d
from matplotlib.colors import LinearSegmentedColormap

cdict = {'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 1.0),
                   (1.0, 0.1, 1.0)),

         'blue':  ((0.0, 0.0, 0.1),
                   (0.5, 1.0, 0.0),
                   (1.0, 0.0, 0.0)),

        'alpha': ((0.0, 1.0, 1.0),
                #   (0.25,1.0, 1.0),
                   (0.5, 0.3, 0.3),
                #   (0.75,1.0, 1.0),
                   (1.0, 1.0, 1.0))
        }

valpuri = LinearSegmentedColormap('valpurus', cdict)
plt.register_cmap(cmap=valpuri)

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
        mini = np.min(self.__AltitudeBuffer)
        maxi = np.max(self.__AltitudeBuffer)
        difi = (maxi - mini) / 9
        absmax = max(abs(mini), maxi)
        
        print "max altitude is ", maxi
        print "min altitude is ", mini
        destination =  os.path.dirname(os.path.abspath(__file__)) + str(r'\outputs\%d'% step) + str(r'.png')
        #self.__quantize_grid()
#        fig = plt.figure()
#        plt.imshow(self.__DisplayMap, interpolation='bilinear', origin='lower', cmap=cm.winter)
#        CS = plt.contour(self.__DisplayMap, [0, 1], cmap=cm.winter)
#        CB = plt.colorbar(CS, shrink=0.8, extend='both')
#        l,b,w,h = plt.gca().get_position().bounds
#        ll,bb,ww,hh = CB.ax.get_position().bounds
#        CB.ax.set_position([ll, b+0.1*h, ww, h*0.8])  
#        plt.savefig(destination, bbox_inches='tight') 

        elevations = [-2000, -200, -100, -50, 0, 1, 50, 100, 200, 2000]
        cols = ('#0000e6', '#0000ff', '#1a1aff', '#3333ff', '#33cc33', '#2eb82e', '#29a329', '#248f24', '#1f7a1f', '#1a651a')
        
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.view_init(elev=20, azim=30)
        x = y = np.linspace(0,127,128)
        X, Y = np.meshgrid(x, y)
        Z = self.__AltitudeBuffer
        ax.plot_surface(X, Y, Z, rstride=4, cstride=4, alpha=0.3, cmap=valpuri, linewidth=0.1)
        #cset = ax.contourf(X, Y, Z, zdir='z', offset=mini, cmap=valpuri, levels=elevations) # , colors=cols)#np.arange(mini, maxi, difi))
        cset = ax.contourf(X, Y, Z, zdir='z', offset=mini, colors=cols, levels=elevations)
        #cset.cmap.set_under('#0000e6')
        #cset.cmap.set_over('#1a651a')


        plt.title(str(r'Valpuri step %d'% step))
        ax.set_xlabel('X')
        ax.set_xlim(0, 127)
        ax.set_ylabel('Y')
        ax.set_ylim(0, 127)
        ax.set_zlabel('Z')
        #ax.set_zlim(-4000, 4000)
        ax.set_zlim(-absmax, absmax)
        #ax.set_zlim(mini, maxi)
        cbar = plt.colorbar(cset)
        
        plt.savefig(destination, bbox_inches='tight')
        
        #plt.show()

        if step >= 9:
            plt.show()
       
       
       
# useage: worldmap(XSize, YSize, use smoothing? [Y/n], number of steps in smoothing, 0=single island 1=lots of continents 2=continent with islands)
world = worldmap(128, 128, 1, 10, 1)
