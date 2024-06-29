# space_time_grid.py
import numpy as np

class SpaceTimeGrid:
    def __init__(self, x_size, y_size, z_size, w_size, t_size, resolution):
        self.resolution = resolution
        self.grid = np.zeros((x_size, y_size, z_size, w_size, t_size), dtype=complex)
        self.curvature = np.zeros((x_size, y_size, z_size, t_size))
    
    def set_point(self, x, y, z, w, t, value):
        self.grid[x, y, z, w, t] = value
    
    def get_point(self, x, y, z, w, t):
        return self.grid[x, y, z, w, t]
    
    def set_curvature(self, x, y, z, t, value):
        self.curvature[x, y, z, t] = value
    
    def get_curvature(self, x, y, z, t):
        return self.curvature[x, y, z, t]

    def print_grid_info(self):
        print(f"Grid shape: {self.grid.shape}")
        print(f"Curvature shape: {self.curvature.shape}")
        print(f"Resolution: {self.resolution}")
        
