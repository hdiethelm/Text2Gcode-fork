import sys
import os
from PySide6.QtWidgets import (
    QApplication
)

from helper import text_to_path, path_to_gcode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if len(sys.argv) != 4 and len(sys.argv) != 8:
        print("Usage: main_cli.py font fontsize text [x y z feed]", file=sys.stderr)
        sys.exit(-1)
    
    font_family = sys.argv[1]
    font_size = float(sys.argv[2])
    scale = 0.1  # Same scale as in path_to_gcode
    
    text = sys.argv[3]

    # Get offset and feedrate values
    if len(sys.argv) == 8:
        x_offset = float(sys.argv[4])
        y_offset = float(sys.argv[5])
        z_offset = float(sys.argv[6])
        feedrate = float(sys.argv[7])
    else:
        x_offset = 0
        y_offset = 0
        z_offset = 0
        feedrate = 500

    path = text_to_path(text, font_family=font_family, font_size=font_size)

    # Calculate dimensions
    bounds = path.boundingRect()
    width_mm = bounds.width() * scale
    height_mm = bounds.height() * scale

    gcode = path_to_gcode(path, scale=scale,
                          x_offset=x_offset, y_offset=y_offset, z_offset=z_offset, feedrate=feedrate)

    print("; Text = " + sys.argv[1])
    print(f"; Dimensions: {width_mm:.2f} x {height_mm:.2f} mm")
    print(gcode)
