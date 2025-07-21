# boiler-plate code to set everything up
import os
from mpi4py import MPI

# Get the name of the machine that the code is currently being run on
# hostname = os.uname()[1]
# Start a new mpi process
world_comm = MPI.COMM_WORLD
#Get total number of mpi processes (ranks)
world_size = world_comm.Get_size()
#Get the number of my process (rank)
my_rank = world_comm.Get_rank()
# build and output message to screen
message = f"Hello this is process {my_rank} of {world_size}"
print(message)