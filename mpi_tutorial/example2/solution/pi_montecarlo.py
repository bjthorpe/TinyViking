from mpi4py import MPI
from random import random
import numpy as np
# get basic information about the MPI communicator
world_comm = MPI.COMM_WORLD
world_size = world_comm.Get_size()
my_rank = world_comm.Get_rank()

def calculate_pi(number_of_samples):
    within_circle_count = 0

    for _ in range(number_of_samples):
        x = random()
        y = random()

        if x ** 2 + y ** 2 < 1:
            within_circle_count += 1

    return within_circle_count

# how many seconds since 00:00 on the 01/01/1970
#replce time.time with MPI.Wtime
start = MPI.Wtime()
total_number_of_samples = 1000000000
local_number_of_samples=int(total_number_of_samples/world_size)
within_circle_count= calculate_pi(local_number_of_samples)
end = MPI.Wtime()

if my_rank == 0:
    
    world_sum = within_circle_count
    for i in range( 1, world_size ):
        sum_np = np.array(1)
        world_comm.Recv( [sum_np, MPI.DOUBLE], source=i, tag=77 )
        world_sum += sum_np
    x = (world_sum/total_number_of_samples)*4
    time_secs = end - start
    print('pi is approximately:' ,x)
    print('This took:',time_secs,'Seconds')
    pi_exact="3.14159265358979323"
    # print the final value of pi and elapsed time
    print("For reference the exact value of pi is:")
    print(pi_exact)
else:
        sum_np = np.array( [within_circle_count] )
        world_comm.Send( [sum_np, MPI.DOUBLE], dest=0, tag=77 )