# space_object.py
# space_object.py
import numpy as np
from PyQt5.QtGui import QVector3D

class SpaceObject:
    def __init__(self, position, radius, color):
        self.position = position
        self.radius = radius
        self.color = color
