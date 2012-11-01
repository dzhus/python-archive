#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import radians, exp, cos, sin, atan2, pi

# temporarily hardcoded
FUNC_FROM = 0
FUNC_TO = 2 * pi

# UGLY HACK >:-)
class Func:
    "sin(x)"
    def __init__(self, start=FUNC_FROM, end=FUNC_TO):
        # hardcoded
        self.x = self.start = start
        self.end = end
        self.max = .5
        self.min = -.5
        self.finished = False

    def inc(self, step=0.01):
        self.x = self.x + step
        if self.x >= self.end + step / 2.:
            self.finished = True
        return self.x

    def eval(self):
        x = self.x
        #return exp(-self.x) * self.x**2 * cos(self.x)
        return exp(-x) * x * cos(x**2)
        # return sin(self.x)
    
    def tangent(self, scale_x, scale_y):
        x = self.x
        #return atan2(-exp(-x) * (x**2 * sin(x) + (x**2 - 2 * x) * cos(x)) * scale_x, scale_y)
        #return atan2(cos(self.x) * scale_x, scale_y)
        return atan2(-exp(-x)*(2*x**2*sin(x**2)+(x-1)*cos(x**2)) * scale_x, scale_y)

    def restart(self):
        self.x = self.start
        self.finished = False
