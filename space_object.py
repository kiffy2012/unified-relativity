# space_object.py
import numpy as np
from PyQt5.QtGui import QVector3D

class SpaceObject:
    def __init__(self, position, radius, color, mass=1.0):
        self.position = position
        self.radius = radius
        self.color = color
        self.mass = mass
