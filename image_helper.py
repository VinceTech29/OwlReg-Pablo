"""
Image loading helper for OwlReg
Provides functions to safely load images, with fallbacks for missing files
"""
import os
from PyQt6.QtGui import QPixmap, QIcon
import traceback

def get_image_path(filename):
    """Get the absolute path to an image file in the application directory"""
    return os.path.join(os.path.dirname(__file__), filename)

def load_pixmap(filename, default_size=(100, 100)):
    """
    Safely load a QPixmap from a file with error handling
    Returns a valid pixmap even if the file is missing
    """
    try:
        # Try to load the specified image file
        path = get_image_path(filename)
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                return pixmap

        # If file doesn't exist or couldn't be loaded, create a blank pixmap
        print(f"Warning: Could not load image '{filename}', using placeholder instead.")
        pixmap = QPixmap(default_size[0], default_size[1])
        pixmap.fill()  # Fill with default color
        return pixmap

    except Exception as e:
        print(f"Error loading image '{filename}': {e}")
        traceback.print_exc()
        # Return a blank pixmap on error
        pixmap = QPixmap(default_size[0], default_size[1])
        pixmap.fill()  # Fill with default color
        return pixmap

def load_icon(filename):
    """
    Safely load a QIcon from a file with error handling
    Returns a valid icon even if the file is missing
    """
    return QIcon(load_pixmap(filename))
