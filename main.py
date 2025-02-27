from space_time_grid import SpaceTimeGrid
from grid_visualizer import visualize_grid

def main():
    # Create a grid for visualization
    grid = SpaceTimeGrid(x_size=20, y_size=20, z_size=20, w_size=5, t_size=10, resolution=0.1)
    
    # Visualize the grid
    visualize_grid(grid)

if __name__ == "__main__":
    print("Starting main")
    grid = SpaceTimeGrid(x_size=20, y_size=20, z_size=20, w_size=5, t_size=10, resolution=0.1)
    print("Grid created, calling visualize_grid")
    visualize_grid(grid)
    print("visualize_grid finished")
    main()
