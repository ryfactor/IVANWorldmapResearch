# -*- coding: utf-8 -*-
"""

  IVAN Worldmap Research
  Copyright (C) Ryan van Herel
  Released under the GNU General
  Public License

  See LICENSING which should be included
  along with this file for more details

  @author: fejoa
  code adapted from an implementation of poisson disc sampling by Connor Johnson 
  http://connor-johnson.com/2015/04/08/poisson-disk-sampling/

"""

import numpy as np
from random import random
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
"""
class pds:
 
    def __init__( self, w, h, r, n ):
        # w and h are the width and height of the field
        self.w = w
        self.h = h
        # n is the number of test points
        self.n = n
        self.r2 = r**2
        self.A = 3*self.r2
        # cs is the cell size
        self.cs = r / np.sqrt(2)
        # gw and gh are the number of grid cells
        self.gw = int( np.ceil( self.w/self.cs ) )
        self.gh = int( np.ceil( self.h/self.cs ) )
        # create a grid and a queue
        self.grid = [ None ] * self.gw * self.gh 
        self.queue = list()
        # set the queue size and sample size to zero
        self.qs, self.ss = 0, 0
 
    def distance( self, x, y ):
        # find where (x,y) sits in the grid
        x_idx = int( x/self.cs )
        y_idx = int( y/self.cs )
        # determine a neighborhood of cells around (x,y)
        x0 = max( x_idx-2, 0 )
        y0 = max( y_idx-2, 0 )
        x1 = max( x_idx-3, self.gw )
        y1 = max( y_idx-3, self.gh )
        # search around (x,y)
        for y_idx in range( y0, y1 ):
            for x_idx in range( x0, x1 ):
                step = y_idx*self.gw + x_idx
                # if the sample point exists on the grid
                if self.grid[ step ]:
                    s = self.grid[ step ]
                    dx = ( s[0] - x )**2
                    dy = ( s[1] - y )**2
                    # and it is too close 
                    if dx + dy < self.r2:
                        # then barf
                        return False
        return True
 
    def set_point( self, x, y ):
        s = [ x, y ]
        self.queue.append( s )
        # find where (x,y) sits in the grid
        x_idx = int( x/self.cs )
        y_idx = int( y/self.cs )
        step = self.gw*y_idx + x_idx
        self.grid[ step ] = s
        self.qs += 1
        self.ss += 1
        return s
 
    def rvs( self ):
        if self.ss == 0:
            x = random() * self.w
            y = random() * self.h
            self.set_point( x, y )
        while self.qs:
            x_idx = int( random() * self.qs )
            s = self.queue[ x_idx ]
            for y_idx in range( self.n ):
                a = 2 * np.pi * random()
                b = np.sqrt( self.A * random() + self.r2 )
                x = s[0] + b*np.cos( a )
                y = s[1] + b*np.sin( a )
                if( x >= 0 )and( x < self.w ):
                    if( y >= 0 )and( y < self.h ):
                        if( self.distance( x, y ) ):
                            self.set_point( x, y )
            del self.queue[x_idx]
            self.qs -= 1
        sample = list( filter( None, self.grid ) )
        sample = np.asfarray( sample )
        return sample

"""
obj = pds( 128, 128, 10, 10 )
sample1 = obj.rvs()
#sample2 = obj.rvs()

x1 = [int(p[0]) for p in sample1]
y1 = [int(q[1]) for q in sample1]

print "number of points in range is %d", len(x1)
print "x1 is", x1

plt.scatter(x1, y1, color='red')
plt.show()


#print "sample1[0,:] is %d", [p[0] for p in sample1]

"""
