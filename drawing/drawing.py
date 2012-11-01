#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import radians

import time

import gtk, gtk.glade
import gobject
import cairo

from shape_sign import ShapeSign
from function import Func

M_NONE = 0
M_SELECT_MOVE = 1
M_SELECT_CENTER = 2
M_FUNC = 4
M_ROLL = 8

# how often area_draw_func will be called via gobject timer
AUTO_TIMEOUT = 50

class Base:
    def area_expose(self, area, event=None):
        """
        Expose-event handler for drawing area.
        """
        ctx = area.window.cairo_create()
        
        if not self.mode in (M_FUNC, M_ROLL):
            # workaround to handle misbehaving Gtk 'scale' widgets
            # (aren't setting value to zero when expected to)
            if abs(self.scale_x.get_value()) > 1E-5 and abs(self.scale_y.get_value()) > 1E-5:
                self.area_draw_basic(ctx)
        elif self.mode == M_FUNC:
            self.area_draw_func(ctx)
        elif self.mode == M_ROLL:
            self.area_draw_roll(ctx)
                
    def area_draw_basic(self, ctx):
        "Redraw shape according to current position, rotation and angle once"
        # draw current shape position
        self.shape.draw(ctx, 
                        self.centerpoint, self.basepoint, 
                        radians(self.angle.get_value()),
                        self.scale_x.get_value(), self.scale_y.get_value(),
                        )
        
        # draw ghost
        if self.mode == M_SELECT_MOVE:
            self.shape.draw(ctx, self.blip,
                            self.basepoint,
                            radians(self.angle.get_value()),
                            self.scale_x.get_value(), self.scale_y.get_value(),
                            opacity = 0.5)
        elif self.mode == M_SELECT_CENTER:
            self.shape.draw(ctx, self.blip,
                            ([self.basepoint[n] + self.centerpoint[n] - self.blip[n]
                              for n in (0, 1)]),
                            radians(self.angle.get_value()),
                            self.scale_x.get_value(), self.scale_y.get_value(),
                            opacity = 0.5)
            
        # draw centerpoint mark
        ctx.set_source_color(gtk.gdk.color_parse("#36B241"))
        ctx.arc(self.centerpoint[0], self.centerpoint[1], 1.5, 0, 360)
        ctx.stroke()

    def area_draw_func(self, ctx):
        "Draw current state of function-following shape"
        # calculate plot scales
        plot_scale_x = self.area.window.get_size()[0] / (self.func.end - self.func.start)
        plot_scale_y = self.area.window.get_size()[1] / (self.func.max - self.func.min)
        
        old_x = self.func.x
        self.func.restart()
        # move shape to the beginning of plot
        self.centerpoint = ((self.func.x - self.func.start) * plot_scale_x,
                            (self.func.max - self.func.eval()) * plot_scale_y)
            
        # function plot for background
        ctx.set_line_width(3)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(*self.centerpoint)
        while not self.func.finished:
            ctx.line_to((self.func.x - self.func.start) * plot_scale_x,
                        (self.func.max - self.func.eval()) * plot_scale_y)
            self.func.inc(self.xml.get_widget('func_speed').get_value())
        ctx.stroke()
        self.func.restart()
        self.func.x = old_x

        self.shape.draw(ctx,
                        ((self.func.x - self.func.start) * plot_scale_x,
                         (self.func.max - self.func.eval()) * plot_scale_y),
                        angle = -(0, self.func.tangent(plot_scale_y, plot_scale_x))[self.xml.get_widget('func_tangent').get_active()]
                        )
        self.func.inc(self.xml.get_widget('func_speed').get_value())
        
        # self-kill function plotting process if finished
        if self.func.finished:
            gobject.source_remove(self.auto_timer)
            self.xml.get_widget('func_start').set_active(0)

    def area_draw_roll(self, ctx):
        "Rolling step"
        global ROLL_SIDE
        ctx.translate(*map(lambda x: x/2, self.area.window.get_size()))
        ctx.rotate(radians(self.xml.get_widget('roll_angle').get_value()))

        # draw base line
        ctx.set_line_width(3)
        ctx.move_to(-self.area.window.get_size()[0], 0)
        ctx.line_to(self.area.window.get_size()[0], 0)
        ctx.stroke()

        self.shape.draw(ctx, self.centerpoint, self.basepoint,
                        angle=radians(self.angle.get_value()))
        self.angle.set_value(self.angle.get_value() + 1)

        # Following shit strongly depends on linear dimensions of shape
        # Thus, the following code and the whole rolling subprograms DO SUCK
        if self.angle.get_value() == 90:
            self.centerpoint[0] += 210
            self.basepoint = (-55, 105)
            self.roll_side = 2
        elif self.angle.get_value() == 180:
            self.centerpoint[0] += 110
            self.basepoint = (55, 105)
            self.roll_side = 3
        elif self.angle.get_value() == 270:
            self.centerpoint[0] += 210
            self.basepoint = (55, -105)
            self.roll_side = 4
        if self.angle.get_value() == 360:
            self.centerpoint[0] += 110
            self.basepoint = (-55, -105)
            self.roll_side = 1
            self.angle.set_value(0)
          
    def area_click(self, area, event):
        "Handle click on area according to current mode"
        if self.mode == M_SELECT_MOVE:
            self.centerpoint = self.blip
            self.xml.get_widget('button_move_point').set_active(0)
        elif self.mode == M_SELECT_CENTER:
            self.basepoint = ([self.basepoint[n] + self.centerpoint[n] - event.get_coords()[n]
                               for n in (0, 1)])
            self.centerpoint = event.get_coords()
            self.xml.get_widget('button_center_point').set_active(0)
        self.area.queue_draw()
        
    def area_pointer_move(self, area, event):
        """
        Handle moving mouse over the area in 'Select position' and
        'Select centerpoint' modes: update 'blip' point and redraw
        shape 'ghost'.
        """
        if self.mode in (M_SELECT_CENTER, M_SELECT_MOVE):
            self.blip = event.get_coords()
            self.area.queue_draw()

    def area_scroll(self, area, event):
        "Scroll mouse wheel in drawing area"
        if event.direction == gtk.gdk.SCROLL_UP:
            delta = .1
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            delta = -.1
        for s in self.scale_x, self.scale_y:
            s.set_value(s.get_value() + delta)
        
    def button_move_point_toggled(self, button):
        """
        Click on 'Move system'.
        
        The difference between moving the system and moving the
        central point is that moving the whole system keeps the
        distance from central point of system to base point of shape,
        whilst moving the central point is relative to basepoint.
        
        This behaviour may be changed in future versions.
        """
        self.mode = [M_NONE, M_SELECT_MOVE][button.get_active()]
        if button.get_active():
            self.xml.get_widget('button_center_point').set_active(0)

    def button_center_point_toggled(self, button):
        "Click on 'Set up a new center point position'"
        self.mode = (M_NONE, M_SELECT_CENTER)[button.get_active()]
        if button.get_active():
            self.xml.get_widget('button_move_point').set_active(0)

    def button_move_click(self, button):
        if button.name == 'button_move_center':
            self.centerpoint = map(lambda x: x / 2., self.area.window.get_size())
            self.basepoint = (0, 0)
        # this needs to be reviewed
        if button.name == 'button_move_up':
            self.centerpoint = (self.centerpoint[0],
                                self.centerpoint[1] - self.area.window.get_size()[0] / 20)
        if button.name == 'button_move_down':
            self.centerpoint = (self.centerpoint[0],
                                self.centerpoint[1] + self.area.window.get_size()[1] / 20)            
        if button.name == 'button_move_right':
            self.centerpoint = (self.centerpoint[0] + self.area.window.get_size()[0] / 20,
                                self.centerpoint[1])
        if button.name == 'button_move_left':
            self.centerpoint = (self.centerpoint[0] - self.area.window.get_size()[1] / 20,
                                self.centerpoint[1])
        self.area.queue_draw()

    def force_area_redraw(self):
        """
        Special callback to be used in couple with
        `gobject.timeout_add(..., force_area_redraw)` in order to
        create area redraw loops.
        """
        self.area.queue_draw()
        # here is all the magic:
        return True

    def func_start_toggled(self, button):
        """
        Set mode and start queueing area to redraw. The rest is done
        within `area_draw_func`.
        """
        self.mode = (M_NONE, M_FUNC)[button.get_active()]
        if self.mode == M_FUNC:
            if self.func.finished:
                self.func.restart()
            # initiate function drawing process
            self.auto_timer =  gobject.timeout_add(AUTO_TIMEOUT, 
                                                   self.force_area_redraw)
        else:
            gobject.source_remove(self.auto_timer)

    def roll_start_toggled(self, button):
        """
        Start queueing area to redraw rollin' sign. See
        `area_draw_roll` for rolling step handler.
        """
        self.mode = (M_NONE, M_ROLL)[button.get_active()]
        if self.mode == M_ROLL:
            self.auto_timer =  gobject.timeout_add(AUTO_TIMEOUT, 
                                                   self.force_area_redraw)
            # @MAGIC
            self.angle.set_value(0)
            self.basepoint = [-55, -105]
            self.centerpoint = [-self.area.window.get_size()[0] / 2, 0]
            self.roll_side = 1
        else:
            gobject.source_remove(self.auto_timer)


    def reset_all(self, caller, data=0, data2=0):
        "Revert all transformations"
        # move shape to center
        self.button_move_click(self.xml.get_widget('button_move_center'))

        # reset transformations
        self.angle.set_value(0)
        self.scale_x.set_value(1.0)
        self.scale_y.set_value(1.0)

        self.mode = M_NONE
        [self.xml.get_widget(w).set_active(0) 
         for w in ('func_start', 'roll_start', 'button_move_point', 'button_center_point')]

        # stop redrawing in automatic modes
        try:
            gobject.source_remove(self.auto_timer)
        except:
            pass

        self.area.queue_draw()

    def window_press_key(self, window, event):
        "Handle keyboard button pressing"
        if event.state & gtk.gdk.SHIFT_MASK:
            # move shape on Shift+arrows
            for key in ('Left', 'Right', 'Up', 'Down'):
                if event.keyval == gtk.gdk.keyval_from_name(key):
                    self.button_move_click(self.xml.get_widget('button_move_' + str.lower(key)))
                    return True

    def __init__(self):
        self.xml = gtk.glade.XML("glade/drawing.glade")

        # gtk.DrawingArea widget to draw shape on
        self.area = self.xml.get_widget('area')

        # create fancy function to plot later
        self.func = Func()
        self.auto_timer = None

        self.scale_x, self.scale_y, self.angle = [self.xml.get_widget(w)
                                                      for w in 'scale_x', 'scale_y', 'angle']
        self.bar = self.xml.get_widget('statusbar')

        self.xml.signal_autoconnect(
            {
                'area_expose': self.area_expose,
                'area_click' : self.area_click,
                'area_pointer_move' : self.area_pointer_move,
                'area_scroll' : self.area_scroll,
                          
                'button_move_click' : self.button_move_click,
                'button_move_point_toggled' : self.button_move_point_toggled,
                'button_center_point_toggled' : self.button_center_point_toggled,
                
                'angle_change' : lambda w: self.area.queue_draw(),
                'scale_change' : lambda w: self.area.queue_draw(),
                
                'func_start_toggled':self.func_start_toggled,
                'roll_start_toggled':self.roll_start_toggled,
                
                'gtk_main_quit' : lambda w: gtk.main_quit(),
                'reset_all' : self.reset_all,
                'window_press_key': self.window_press_key
                }
            )

        self.xml.get_widget('window').show_all()

        # centerpoint is Cairo user-space origin; when drawing
        # shape, Cairo context space is translated to centerpoint
        self.centerpoint = map(lambda x: x / 2., self.area.window.get_size())

        # shape's basepoint is relative to centerpoint!
        self.basepoint = (0, 0)
        self.shape = ShapeSign()

        # blip is used as temporarty centerpoint or basepoint,
        # depending on active mode; stored relative to current centerpoint
        self.blip = None

        self.mode = M_NONE

        self.roll_side = 1

    def main(self):
        gtk.main()

Base().main()
