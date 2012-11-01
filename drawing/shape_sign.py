# -*- coding: utf-8 -*-

import math
import cairo, gtk

def color_hex_unpack(spec, opacity=1.0):
    color = gtk.gdk.color_parse(spec)
    return [color.red/65535., color.green/65535., color.blue/65535., opacity]

class ShapeSign:
    """
    Stupid class providing only basepoint storage and drawing of 'TAXI'
    sign in Cairo context.
    """
    def __init__(self):
        pass

    def draw(self, ctx, centerpoint, basepoint=(0, 0),
             angle=0, scale_x=1.0, scale_y=1.0, 
             opacity=1,
             axes=True):
        """
        Context user space is translated to shape's basepoint before drawing.
        """
        ctx.set_line_width(3)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        
        ctx.translate(centerpoint[0], centerpoint[1])
        ctx.rotate(angle)
        ctx.scale(scale_x, scale_y)

        ctx.translate(basepoint[0], basepoint[1])

        # sign panels
        ctx.set_source_rgba(*color_hex_unpack("#3165A5", opacity))
        for c, p in zip([(50, 100), (-50, 100), (-50, -100), (50, -100)], xrange(4)):
            ctx.arc(c[0], c[1], 5, math.radians(p * 90), math.radians((p + 1) * 90))        
        ctx.close_path()
        ctx.fill()

        ctx.set_source_rgba(*color_hex_unpack("#EFEFEF", opacity))
        for c, p in zip([(35, 30), (-35, 30), (-35, -70), (35, -70)], xrange(4)):
            ctx.arc(c[0], c[1], 10, math.radians(p * 90), math.radians((p + 1) * 90))        
        ctx.close_path()
        ctx.fill()
        
        # text label
        ctx.set_source_rgba(*color_hex_unpack("#293531", opacity))
        ctx.set_font_size(18)
        ctx.move_to(-ctx.text_extents('Такси')[4] / 2, -50)
        ctx.show_text('Такси')

        # car shape
        ctx.move_to(0, -40)
        ctx.curve_to(20, -40, 10, -10, 30, -10)
        ctx.curve_to(40, -10, 40, 15, 30, 15)

        # wheels
        ctx.curve_to(15, 15, 30, 30, 15, 30)
        ctx.curve_to(0, 30, 15, 15, 0, 15)

        ctx.curve_to(-15, 15, 0, 30, -15, 30)
        ctx.curve_to(-30, 30, -15, 15, -30,  15)

        ctx.curve_to(-40, 15, -40, -10, -30, -10)
        ctx.curve_to(-10, -10, -20, -40, 0, -40)
        ctx.close_path()
        ctx.fill()

        # windscreen
        ctx.set_source_rgba(*color_hex_unpack("#EFEFEF", opacity))
        ctx.move_to(0, -30)
        for point in [(5, -30), (10, -10), (-10, -10), (-5, -30), (0, -30)]:
            ctx.line_to(point[0], point[1])
        ctx.close_path()
        ctx.fill()

        # lights
        for c in 17, -17:
            ctx.move_to(c, -3)
            for point in [(c + 5, -3), (c + 5, 5), (c - 5, 5), (c - 5, -3)]:
                ctx.line_to(point[0], point[1])
            ctx.close_path()
            ctx.stroke()

        ctx.translate(-basepoint[0], -basepoint[1])

        ctx.scale(1/scale_x, 1/scale_y)
        ctx.rotate(-angle)
        ctx.translate(-centerpoint[0], -centerpoint[1])
