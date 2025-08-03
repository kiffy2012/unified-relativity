# space_object.py
from PyQt5.QtGui import QVector3D

class SpaceObject:
    def __init__(self, position, radius, color, mass=1.0, velocity=None):
        self.position = position
        self.radius = radius
        self.color = color
        self.mass = mass
        # Store velocity as a QVector3D. Defaults to zero velocity.
        self.velocity = velocity if velocity is not None else QVector3D(0.0, 0.0, 0.0)
