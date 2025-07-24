from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Total number of points
total_points = 10000

# Points per process
points_per_proc = total_points // size

# Each process generates random points
np.random.seed(rank)  # Different seed per process
x = np.random.rand(points_per_proc)
y = np.random.rand(points_per_proc)

# Compute whether each point is inside the unit circle
inside = x**2 + y**2 <= 1.0

# Combine x, y, and inside info
local_points = np.column_stack((x, y, inside))

# Gather all points to root
gathered = comm.gather(local_points, root=0)

if rank == 0:
    # Concatenate all point arrays
    all_points = np.vstack(gathered)

    # Separate points inside and outside the circle
    inside_points = all_points[all_points[:, 2] == 1]
    outside_points = all_points[all_points[:, 2] == 0]

    # Plotting
    plt.figure(figsize=(6, 6))
    plt.scatter(outside_points[:, 0], outside_points[:, 1], color='red', s=1, label='Outside')
    plt.scatter(inside_points[:, 0], inside_points[:, 1], color='blue', s=1, label='Inside')
    plt.gca().set_aspect('equal')
    plt.title('Monte Carlo π Estimation')
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.tight_layout()
    plt.savefig('monte_carlo_pi.png')
    plt.show()