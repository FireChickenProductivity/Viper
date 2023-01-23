#The display code is heavily based on the mouse grid code in the knausj_talon repository distributed under the following license:
#"MIT License

# Copyright (c) 2021 Jeff Knaus, Ryan Hileman, Zach Dwiel, Michael Arntzenius, and others

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE."

from talon import canvas, ui
from talon.skia import Paint, Rect
from .fire_chicken.mouse_position import MousePosition

class SingleLineDisplay:
    def __init__(self):
        self.screen = None
        self.rect = None
        self.mcanvas = None

    def display(self, start: MousePosition, ending: MousePosition, location: MousePosition):
        self.start = start
        self.ending = ending
        self.location = location
        self.setup_canvas()
        self.show()

    def setup_canvas(self):
        if self.mcanvas is not None:
            self.mcanvas.close()
        distance_between_points = self.start.distance_from(self.ending)
        self.mcanvas = canvas.Canvas(0, 0, distance_between_points*2, distance_between_points*2)
        self.mcanvas.move(self.location.get_horizontal() - distance_between_points, self.location.get_vertical() - distance_between_points)
        
    def show(self):
        self.mcanvas.register("draw", self.draw)
        self.mcanvas.freeze()
        return

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "FF0000"
        paint.style = Paint.Style.FILL

        canvas.draw_line(self.start.get_horizontal(), self.start.get_vertical(), self.ending.get_horizontal(), self.ending.get_vertical())

    def hide(self):
        if self.mcanvas:
            self.mcanvas.unregister("draw", self.draw)
            self.mcanvas.close()
            self.mcanvas = None