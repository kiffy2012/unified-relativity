"""Simple multidimensional grid container without external dependencies."""


class SpaceTimeGrid:
    def __init__(self, x_size, y_size, z_size, w_size, t_size, resolution):
        self.resolution = resolution
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        self.w_size = w_size
        self.t_size = t_size
        # Five‑dimensional grid storing complex numbers
        self.grid = [
            [
                [
                    [[0j for _ in range(t_size)] for _ in range(w_size)]
                    for _ in range(z_size)
                ]
                for _ in range(y_size)
            ]
            for _ in range(x_size)
        ]
        # Four‑dimensional curvature tensor storing floats
        self.curvature = [
            [
                [[0.0 for _ in range(t_size)] for _ in range(z_size)]
                for _ in range(y_size)
            ]
            for _ in range(x_size)
        ]
    
    def set_point(self, x, y, z, w, t, value):
        self.grid[x, y, z, w, t] = value
    
    def get_point(self, x, y, z, w, t):
        return self.grid[x, y, z, w, t]
    
    def set_curvature(self, x, y, z, t, value):
        self.curvature[x, y, z, t] = value
    
    def get_curvature(self, x, y, z, t):
        return self.curvature[x, y, z, t]

    def print_grid_info(self):
        print(
            f"Grid dimensions: ({self.x_size}, {self.y_size}, {self.z_size}, {self.w_size}, {self.t_size})"
        )
        print(
            f"Curvature dimensions: ({self.x_size}, {self.y_size}, {self.z_size}, {self.t_size})"
        )
        print(f"Resolution: {self.resolution}")
        
