import sys
import os
from PySide6.QtWidgets import (
    QApplication
)

from helper import text_to_path, path_to_gcode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    text = sys.argv[1]
    font_family = "Noteworthy"
    font_size = 100
    scale = 0.1  # Same scale as in path_to_gcode

    # Get offset values
    x_offset = 0
    y_offset = 0
    z_offset = 0

    # Get feedrate value
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
