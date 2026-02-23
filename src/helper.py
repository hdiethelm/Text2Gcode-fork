import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainterPath

# Helper function: Convert text to path
def text_to_path(text, font_family="Arial", font_size=50):
    font = QFont(font_family, font_size)
    path = QPainterPath()
    path.addText(0, 0, font, text)
    return path

def elem2xy(elem: QPainterPath.Element, scale=0.1, x_offset=0.0, y_offset=0.0):
    #print(elem.type)
    #print(elem.x)
    #print(elem.y)
    x = elem.x * scale + x_offset
    y = -elem.y * scale + y_offset  # Invert Y-axis for CNC
    return [x, y]

# Helper function: Convert path to G-Code
def path_to_gcode(path: QPainterPath, scale=0.1, safe_z=5.0, cut_z=0.0, feedrate=500,
                 x_offset=0.0, y_offset=0.0, z_offset=0.0, use_g5=True):
    gcode = [
        "G21 ; mm mode",
        "G90 ; absolute positioning"
    ]

    if path.elementCount() == 0:
        return "\n".join(gcode)

    pen_down = True #Stat with pen_down so first move is up to save position

    i = 0
    while i < path.elementCount():
        elem = path.elementAt(i)
        
        if elem.isMoveTo():
            if pen_down:
                gcode.append(f"G0 Z{safe_z + z_offset:.2f}")  # Pen up
                pen_down = False
            [x0, y0] = elem2xy(elem, scale, x_offset, y_offset)
            gcode.append(f"G0 X{x0:.2f} Y{y0:.2f}")  # Position

        elif elem.isLineTo():  # LineTo
            assert(i != 0) #First should be move to
            if not pen_down:
                gcode.append(f"G1 Z{cut_z + z_offset:.2f} F{feedrate}")  # Pen down
                pen_down = True
            [x0, y0] = elem2xy(elem, scale, x_offset, y_offset)
            gcode.append(f"G1 X{x0:.2f} Y{y0:.2f} F{feedrate}")
            
        elif elem.isCurveTo():  # CurveTo
            assert(i != 0) #First should be move to
            if not pen_down:
                gcode.append(f"G1 Z{cut_z + z_offset:.2f} F{feedrate}")  # Pen down
                pen_down = True
            
            # See: https://doc.qt.io/qt-6/qpainterpath.html#cubicTo
            # and https://linuxcnc.org/docs/html/gcode/g-code.html#gcode:g5
            
            #x0, y0: Start is given by last element
            [x1, y1] = elem2xy(elem, scale, x_offset, y_offset) #c1
            
            i=i+1;
            elem = path.elementAt(i)
            assert(elem.type == QPainterPath.CurveToDataElement) #CurveTo is always followed by two CurveToDataElement
            [x2, y2] = elem2xy(elem, scale, x_offset, y_offset) #c2
            
            i=i+1;
            elem = path.elementAt(i)
            assert(elem.type == QPainterPath.CurveToDataElement) #CurveTo is always followed by two CurveToDataElement
            [x3, y3] = elem2xy(elem, scale, x_offset, y_offset) #end
            
            if use_g5:
                gcode.append(f"G5 I{x1-x0:.2f} J{y1-y0:.2f} P{x2-x3:.2f} Q{y2-y3:.2f} X{x3:.2f} Y{y3:.2f} F{feedrate}")
            else:
                #Just move trough control points, looks better, even if it is basicaly wrong
                #ToDo: Do interpolation somehow?
                gcode.append(f"G1 X{x1:.2f} Y{y1:.2f} F{feedrate}")
                gcode.append(f"G1 X{x2:.2f} Y{y2:.2f} F{feedrate}")
                gcode.append(f"G1 X{x3:.2f} Y{y3:.2f} F{feedrate}")
            
            #End is next start for spline
            x0=x3
            y0=y3
            
        i=i+1

    if pen_down:
        gcode.append(f"G0 Z{safe_z + z_offset:.2f}")  # Pen up at the end

    gcode.append("M2 ; Program end")
    return "\n".join(gcode)
