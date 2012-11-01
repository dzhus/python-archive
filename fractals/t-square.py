#!/usr/bin/python

from random import randrange
from datetime import datetime as time
import Image
import ImageDraw

# ############################
# Configurable data
gCanvasSize     = 5000
gMaxDepth       = 9 
# End of configurable data
# ############################

Img = Image.new("RGB",(gCanvasSize, gCanvasSize))
Draw = ImageDraw.Draw(Img)

def Step(base, depth=1):
    if depth > gMaxDepth:
        return

    side = (base[1][0] - base[0][0])

    Draw.rectangle(((base[0][0] + side / 4, base[0][1] - side / 4), (base[1][0] - side / 4, base[1][1] - 3 * side / 4)), fill='white')

    Step(((base[0][0], base[0][1] - side / 2), (base[0][0] + side / 2, base[0][1] - side / 2)), depth + 1)
    Step(((base[0][0] + side / 2, base[0][1] - side / 2), (base[1][0], base[0][1] - side / 2)), depth + 1)
    Step(((base[0][0], base[0][1]), (base[0][0] + side / 2, base[0][1])), depth + 1)
    Step(((base[0][0] + side / 2, base[0][1]), (base[1][0], base[0][1])), depth + 1)
        


start = time.now()
Step(((0, gCanvasSize), (gCanvasSize, gCanvasSize)), 1)
print "Time taken to draw fractal: " + str(time.now() - start)
Img.save("out.png")
