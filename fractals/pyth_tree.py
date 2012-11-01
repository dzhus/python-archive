#!/usr/bin/python

# This program draws a Pythagoras tree using
# Python Imaging Library

# Import modules
from random import randrange
from math import floor
import Image, ImageDraw


# ############################
# Configurable options

# X and Y values are respective canvas dimensions
X = 800
Y = 400

# A, B are tuples setting coordinates of initial rectangle base vertices
A = (375, 325)
D = (425, 325)

# K is a rectangle side factor
# Say ABCD is our rectangle, AD - base. Then CD=AD*K.
# if K<1, rectangle will be "wide"
# if K=1, we will get a square
# if K>1, rectangle will be tall
K = 1

# How deep fractal is?
MaxDepth = 12 

# No more configurable options.
# ############################


Img = Image.new("RGB", (X,Y))
Draw = ImageDraw.Draw(Img)
Colors = []
Colors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )

def Step(A, D, depth=0):
    # Depth-check
    if depth > MaxDepth:
            return

    # Calculate coordinates for another two vertices
    B = ( A[0]+(D[1]-A[1])*K, A[1]+(A[0]-D[0])*K )
    C = ( D[0]+(D[1]-A[1])*K, D[1]+(A[0]-D[0])*K )

    # Generate a new color for generation
    if len(Colors)-1 < depth:
        Colors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )

    # Draw rectangle
    Draw.polygon((A, B, C, D), outline=Colors[depth])

    # Calculate coordinate for top of the "hat"
    O = ( round(B[0]+(C[0]-A[0])/2), round(B[1]+(C[1]-A[1])/2) )

    # Draw hat
    Draw.polygon((B, O, C), outline=Colors[depth])

    # Do the same with sides of the hat
    Step( B, O, depth+1 )
    Step( O, C, depth+1 )


# Run process
Step(A, D)

# Show the result
Img.show()
Img.save("out.png")
