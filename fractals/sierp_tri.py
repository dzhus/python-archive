#!/usr/bin/python

# This program draws a Sierpinsky triangle using
# Python Imaging Library

# Import modules
from random import randrange
import Image, ImageDraw

# ############################
# Configurable options

# X and Y values are respective canvas dimensions
X = 1024 
Y = 768

# A, B, C are tuples setting coordinates of initial triangle
# vertices, e.g. A=(100,50)
A = (512, 0)
B = (0, 768)
C = (1024, 768)

# How deep fractal is?
MaxDepth = 6 

FancyMode = 1

# No more configurable options.
# ############################

Img = Image.new("RGB", (X,Y))
Draw = ImageDraw.Draw(Img)
Colors = []
BgColors = []
Colors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )
BgColors.append( (randrange(0,255), randrange(0,255), randrange(0,255)) )

def Step(A, B, C, depth=0):
    # Depth-check
    if depth > MaxDepth:
            return

    # Draw triangle
    Draw.polygon((A, B, C), outline=(255,255,255))

    # Generate coordinates of median triangle vertices
    nA = ( A[0]+(B[0]-A[0])/2, A[1]+(B[1]-A[1])/2 )
    nB = ( A[0]+(C[0]-A[0])/2, A[1]+(C[1]-A[1])/2 )
    nC = ( C[0]+(B[0]-C[0])/2, B[1]+(C[1]-B[1])/2 )

    # Generate a new color for generation
    if len(Colors)-1 < depth:
        Colors.append( (randrange(0,255), randrange(0,255), randrange(120,255)) )
    if len(BgColors)-1 < depth:
        BgColors.append( (randrange(0,255), randrange(0,255), randrange(120,255)) )

    # And draw median triangle
    if FancyMode:
        Draw.polygon((nA, nB, nC), outline=(randrange(0,255), randrange(0,255), randrange(0,255)), fill=(randrange(0,255), randrange(0,255), randrange(0,255)))
    else:
        Draw.polygon((nA, nB, nC), outline=Colors[depth], fill=BgColors[depth])

    
    # Draw children
    Step( A, nA, nB, depth+1 )
    Step( nA, B, nC, depth+1 )
    Step( nB, nC, C, depth+1 )

# Run process
Step(A, B, C)

# Show the result
Img.save("out.png")
