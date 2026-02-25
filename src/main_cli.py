import sys
import os
from PySide6.QtWidgets import (
    QApplication
)

from helper import text_to_path, path_to_gcode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if len(sys.argv) != 4 and len(sys.argv) != 10:
        print("Usage: main_cli.py font fontsize text [x y z feed gcode_prefix gcode_postfix]", file=sys.stderr)
        sys.exit(-1)
    
    font_family = sys.argv[1]
    font_size = float(sys.argv[2])
    scale = 0.1  # Same scale as in path_to_gcode
    
    text = sys.argv[3]

    # Get offset and feedrate values
    if len(sys.argv) == 10:
        x_offset = float(sys.argv[4])
        y_offset = float(sys.argv[5])
        z_offset = float(sys.argv[6])
        feedrate = float(sys.argv[7])
        g_prefix =  sys.argv[8].splitlines()
        g_postfix = sys.argv[9].splitlines()
    else:
        x_offset = 0
        y_offset = 0
        z_offset = 0
        feedrate = 500
        g_prefix = [
            "G21 ; mm mode",
            "G90 ; absolute positioning"
        ]
        g_postfix = [
            "M2 ; Program end"
        ]
    
    path = text_to_path(text, font_family=font_family, font_size=font_size)

    # Calculate dimensions
    bounds = path.boundingRect()
    width_mm = bounds.width() * scale
    height_mm = bounds.height() * scale

    # Add information
    g_prefix = ["; Text = " + "\\n".join(text.splitlines()), f"; Dimensions: {width_mm:.2f} x {height_mm:.2f} mm"] + g_prefix;

    gcode = path_to_gcode(path, scale=scale,
                          x_offset=x_offset, y_offset=y_offset, z_offset=z_offset, feedrate=feedrate,
                          g_prefix=g_prefix, g_postfix=g_postfix)

    print(gcode)
