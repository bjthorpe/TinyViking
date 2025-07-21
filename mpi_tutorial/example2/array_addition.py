import numpy as np
from mpi4py import MPI
#Setup mpi
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
world_size = comm.Get_size()

stat_time = MPI.Wtime()
N = 10000000

# determine the workload of each rank
workloads = [ N // world_size for i in range(world_size) ]
for i in range( N % world_size ):
    workloads[i] += 1

my_start = 0
for i in range( rank ):
    my_start += workloads[i]
my_end = my_start + workloads[rank]

# initialize a
a = np.ones( N )

# initialize b
b = np.zeros( N )
for i in range(N):
    b[i] = 1.0 + i

# average the result
sum = 0.0
# add the two arrays
for i in range(my_start,my_end):
    a[i] = a[i] + b[i]

for i in range(my_start,my_end):
    sum += a[i]

if rank ==0:
    for i in range(1,world_size):
        data = comm.recv(source=i,tag=11)
        sum += data
    average = sum / N
else:
    sum =[sum]
    comm.send(sum,dest=0,tag=11)

end_time = MPI.Wtime()
total_time = end_time - stat_time
if rank==0:
    print("Average: " + str(average),'seconds')
    print('this took:',total_time)