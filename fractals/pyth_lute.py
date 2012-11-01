#!/usr/bin/python

from math import sin, radians, sqrt
from random import randrange
import Image
import ImageDraw
from polygon import Polygon

# ############################
# Configurable data
gCanvas         = (1280, 1024)
gBase           = ((750, 700), (1150, 700))
gMaxDepth       = 9 
# End of configurable data
# ############################

gGold = (1+sqrt(5))/2

Img = Image.new("RGB",gCanvas)
Draw = ImageDraw.Draw(Img)
gColors = []
gColors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )

def Step(base, depth=1):
        global gSides, gGold

        if depth > gMaxDepth:
                return

        vertices = Polygon(base=base, sides=5).Vertices

        # Connect non-adjacent vertices too
        for vertice in range(len(vertices)):
            for oppose in range(vertice+2, vertice+len(vertices)-1):
                try:
                    Draw.line((vertices[vertice], vertices[oppose]), fill=gColors[depth-1])
                except:
                    pass

        # Generate a new color for generation
        if len(gColors)-1 < depth:
            gColors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )


        angle = radians(18)

        # Find a second point for a base of new pentagon
        x = (base[0][0] - (base[1][0] - base[0][0]) * (2 - gGold) / (2 * sin(angle)), base[0][1] - (base[1][1] - base[0][1]) * (2 - gGold) / (2 * sin(angle)))
        Step((x, base[0]), depth+1)

        #for n in (1,2,3,4):
        #    x = (vertices[n][0] - (vertices[n-1][0] - vertices[n][0]) * (2 - gGold) / (2 * sin(angle)), vertices[n][1] - (vertices[n-1][1] - vertices[n][1]) * (2 - gGold) / (2 * sin(angle)))
        #    Step((x,vertices[n]), depth+1)


Step(gBase)
#Img.show()
Img.save("out.png")
