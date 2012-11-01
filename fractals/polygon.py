#!/usr/bin/python

import math

class Polygon:
        """Class for drawing any equal-sided polygons.
        
        Usage: obj = Polygon(args)
        Check Polygon.__init__.__doc___ for possible arguments.
        """

        def __init__(self, base=((100,100),(150,100)), sides=5):
                """Init method for creating polygons

                \rArguments are: 

                \rbase\tTuple with coordinates of two first vertices
                of a polygon, forming a first side of polygon,
                e.g. base = ((100,100),(200,100))

                \rsides\tHow many sides will polygon have.

                As the result, Polygon instance will have Vertices,
                Angle, SideLength properties.

                """

                # Pass arguments
                self.Sides = sides

                # First and "Last" point
                F = base[0]
                L = base[1]

                # Polygon vertices coordinates
                self.Vertices = []

                # Angle between adjacent sides in radians
                self.Angle = math.radians(90-360/sides)

                self.SideLength = math.sqrt((F[0]-L[0])**2 + (F[1]-L[1])**2)
                
                self.__polygonStep(F, L)

        def __polygonStep(self, A, B, depth=1):
                if depth > self.Sides:
                        return

                self.Vertices.append(A)

                # Calculate coordinates for another vertice
                C = (   A[0] - self.SideLength * math.sin(self.Angle - math.atan2((B[1]-A[1]),(B[0]-A[0]))),\
                        A[1] - self.SideLength * math.cos(self.Angle - math.atan2((B[1]-A[1]),(B[0]-A[0])))    )
                
                self.__polygonStep(C, A, depth+1)
