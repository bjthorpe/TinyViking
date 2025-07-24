---
layout: page
title: "Mpi python Tutorial"
permalink: /Tutorial/
---

Here's a step-by-step tutorial for using MPI in Python, using the mpi4py library. This will cover installation, basic concepts, and some example programs to get you started with parallel computing using MPI.

Note: all the examples we are using are just "toybox examples" for reference only. These are useful for learning. However, if you want to do any of these things seriously, there are likely third party library’s that can do the same thing in better and more efficient ways without resorting to MPI.

1. toc
{:toc}

## 🔧 Part 1: Prerequisites, Installing MPI and mpi4py

To use mpi we will need to install the following:

* Python 3.x
* The mpi4py python package
* An MPI implementation (MPICH, Intel MPI or OpenMPI)

### The Easy way (using Anaconda)

We recommend using a python distribution called Ananconda.
This contains not only python itself, but also many
packages common packages and tools used for science, data
analysis and AI. Including, for our purposes, MPI, numpy
and matplotlib.

Instructions for Downloading and installing anacionda can be
found at https://www.anaconda.com/docs/getting-started/anaconda/install#anaconda-website

Once this is downloaded and installed:

On Windows start Anaconda Prompt and Type the following commands:

``` bash
conda create -n "mpi_tutorial" python==3.12
conda activate mpi_tutorial
conda install mpi4py matplotlib numpy
```

Note: MacOs and Linux users can just enter the same commands in a regular terminal.

In order, these commands:

* **create a new conda environment called mpi_tutorial with python fixed at version 3.12.** 

This is good practice as it isolates everything we are installing and gives us a clean slate to work with.

* **activate the conda environment.**

Note you will need to run this every time you restart. If this was successful you should now see the words "mpi_tutorial" in brackets.

* **install mpi4py matplotlib and numpy into our conda environment**

You will see a lot of output and it may take a while, however, when prompted to continue type y.

### The Hard way (Manual install)

You can also install mpi4py using standard python and pip

On Windows:
  
* Download and install python from https://www.python.org/downloads/
* Download and install Microsoft MPI from https://www.microsoft.com/en-us/download/details.aspx?id=57467
* Open Microsoft Powershell and type:

```powershell
wget https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
pip install mpi4py
```

On Linux (Ubuntu/Debian) open a terminal and type:

```bash
sudo apt update
sudo apt install mpich
pip install mpi4py
```

On MacOS (using Homebrew) open a terminal and type:

```bash
brew install open-mpi
pip install mpi4py
```

## Part 2. 🚀 Running our first MPI Programs in Python

Now that we, hopefully, have everything setup and installed we can start running some scripts.

You cannot run mpi4py scripts like regular Python scripts. Instead, we need to use mpiexec or mpirun:

```bash 
mpiexec -n 4 python your_script.py
```

This command runs your Python script with 4 processes.

To demonstrate this we will start with the classic "hello world" program
running on 4 processes.

Copy the following into your favourite text editor:

```python
# hello.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Hello from process {rank} out of {size}")
```

If you just run the script with normal python you will get the following:

```bash
python hello.py

Hello from process 0 out of 1
```

As we can see this is just running a single copy of hello.py with a single process. Which works but is probably not what we want.

However if we run the script using:

```bash
mpiexec -n 4 python hello.py

Hello from process 0 out of 4
Hello from process 1 out of 4
Hello from process 3 out of 4
Hello from process 2 out of 4
```

You should see 4 lines printed, one from each process. Thus we are now running 4 identical copies of hello.py in parallel.

Try changing the number of processes n (-n 2, -n 8, etc.).

* Is there a limit to how many you can run?
* Do you notice anything about the order of the process outputs?

Running multiple identical copies of our script is all well and good. However, its not of much practical use unless the processes can talk to
one another which is what we will cover in the next sections.

## Part 3. 📬 Point-to-Point Communication

Processes in MPI can communicate directly with one another by sending using the .send() and .recv() methods as follows:

```python
# send_recv.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = {"key": "value", "rank": rank}
    comm.send(data, dest=1, tag=11)
    print("Process 0 sent data to Process 1")
elif rank == 1:
    data = comm.recv(source=0, tag=11)
    print(f"Process 1 received data: {data}")
```

### The Send method

The send method takes in 3 parameters, 2 are required and 1 is optional.

1. **Data**: The data you wish to send, can be any, **pickleable**, python object.
2. **Source**: The ID of the rank you wish to send data to. Must be an integer
3. **Tag**: an optional message, this allows for finer control when sending/receiving several messages.  Must be convertible to a string.

#### **Wait, what does pickleable mean?**

Python has a module called [pickle](https://www.geeksforgeeks.org/python/understanding-python-pickling-example/). This allows you to convert many python objects into raw data (binary) to send over a network or save to file.

For our purposes, we should not need to worry about this to much. Most common objects as well as all basic types (lists, strings, ints, floats, arrays ect.) are pickleable.

However, not every object in python is. This is usually just system objects such as file handlers, errors, mpi communicators groups ect. However, if you need to send something more complex it's best to check the documentation of whatever package you are using.

In any case at this stage just be aware that, whilst you can use MPI to send many objects. You can't just send whatever you like.

### The Recv method

The Recv method (which stands for receive) works with 2 parameters input and returns the received data.

1. **Source**: The ID of the rank that originally sent the data (i.e. the rank the process is listening for data from). Must be an integer
2. **Tag**: an optional message, this allows for finer control when sending/receiving several messages.  Must be convertible to a string.

## Part 4: 📢 MPI Broadcast

The Broadcast method sends a single message from one process (identified by the input parameter **root**) to all others.

In this example we send data from process 0 to all other processes.

```python
# broadcast.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = "Broadcast message"
else:
    data = None

data = comm.bcast(data, root=0)
print(f"Process {rank} received data: {data}")
```

## Part 5: 🍱 Scatter, Gather and Reduce

Scatter and gather are logical extensions of broadcast allowing to processes to send or receive data from all processes.

```python
# scatter_gather.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    data = [i*2 for i in range(size)]
else:
    data = None

# Scatter data from root to all processes
recv_data = comm.scatter(data, root=0)
print(f"Process {rank} received: {recv_data}")

# Each process does some work
processed_data = recv_data + 1

# Gather results back to root
gathered = comm.gather(processed_data, root=0)
if rank == 0:
    print(f"Root process gathered: {gathered}")
```

### 🧠 Wait? what's the difference between broadcast and scatter?

The simple answer is efficiency. Broacast sends exactly the same data to all processes, this allows the underlying MPI implementation to make certain optimisations for efficiency.

Scatter on the other hand can send different parts of the data to different processes. e.g. sending one slice of a large array to each process. This is less efficient for small messages (or when you need to send all the data) as it can't be optimised as much. However it can be extremally beneficial for sending large data as it reduces the overall communication to just the data that is needed (which is usually the bottleneck).

### Reduce

Reduce is an extension of Gather.

The main difference is after collecting all the data from each process onto the root process we then apply a function 

Some functions you can apply are:

- MPI_MAX - Returns the maximum element.
- MPI_MIN - Returns the minimum element.
- MPI_SUM - Sums the elements.
- MPI_PROD - Multiplies all elements.
- MPI_MAXLOC - Returns the maximum value and the rank of the process that owns it.
- MPI_MINLOC - Returns the minimum value and the rank of the process that owns it.

```python
# scatter_gather.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    data = [i*2 for i in range(size)]
else:
    data = None

# Scatter data from root to all processes
recv_data = comm.scatter(data, root=0)
print(f"Process {rank} received: {recv_data}")

# Each process does some work
processed_data = recv_data + 1

# Gather results back to root and find the Maximum
max_val = comm.reduce(local_count, op=MPI.MAX, root=0)
if rank == 0:
    print(f"The maximum value is: {max_val}")
```

## Part 7: 🧪 Lets put this to use: $\pi$ by Montecarlo

Let’s walk through a real-world example using MPI in Python: parallelizing a Monte Carlo simulation to estimate $\pi$.

### 🎯 Goal

We’ll estimate the value of $\pi$ using a Monte Carlo method:

* Randomly generate points in a square.
* Count how many fall inside the unit circle.
* compute $\pi$ ≈ 4 × (points inside circle / total points)

### 🖥️ 🔂 Sequential Version (for comparison)

```python
# pi_sequential.py
import random
import math
def estimate_pi(n):
    inside = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x**2 + y**2 <= 1.0:
            inside += 1
    return 4 * inside / n

if __name__ == "__main__":
    s1 = str(estimate_pi(10_000_000))
    #s2 = str(math.pi)
    s2 = "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
    print(f"Estimated π: {s1}")
    print(f"For reference the actual value of π to {len(s2)-2} decimal places is:")
    print(s2)
    # calculate how many decimal places we are off by
    left = 0
    for i,s in enumerate(s1):
        if s2[i] == s:
            left = left+1
    print(f"you were accurate to {left-2} decimal places")
```

This runs on a single CPU. Now, let’s parallelize it using MPI.

### 🚀 Parallel Monte Carlo with MPI

```python
# pi_mpi.py
from mpi4py import MPI
import random
import time

def monte_carlo_pi(samples):
    count = 0
    for _ in range(samples):
        x, y = random.random(), random.random()
        if x**2 + y**2 <= 1.0:
            count += 1
    return count

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Total number of points to generate (adjust as needed)
total_samples = 10_000_000

# Split the work among processes
samples_per_proc = total_samples // size

# Start timer
if rank == 0:
    start_time = time.time()

# Each process runs its portion
local_count = monte_carlo_pi(samples_per_proc)

# Gather all local counts at root
total_count = comm.reduce(local_count, op=MPI.SUM, root=0)

# Only root computes and prints the final estimate
if rank == 0:
    pi_estimate = 4 * total_count / total_samples
    duration = time.time() - start_time
    print(f"Estimated π: {pi_estimate}")
    print(f"Time taken with {size} processes: {duration:.4f} seconds")
```

✅ Now we run It

```bash
mpiexec -n 4 python pi_mpi.py

Estimated π: 3.141836
Time taken with 4 processes: 1.2345 seconds
```

### 🧠 What's Happening?

* Each process estimates a portion of $\pi$
* reduce() then Combines all local results into one total
* The Root process computes the final $\pi$ value and prints it

### 🚀 Next Steps

Try changing the number of processes (-n 2, -n 8, etc.) and compare performance!

* Is there a point of diminishing returns?
* Why do we think this is?

## Part 8: 📈 Non-Blocking Monte Carlo $\pi$ Estimator

Finally let's upgrade the Monte Carlo $\pi$ estimator to use non-blocking communication with mpi4py.

This is especially useful in performance-critical applications where you want to overlap computation with communication.

### 🚀 What’s Non-blocking Communication?

With blocking functions (send, recv, gather, etc.), a process waits until the operation is done.
Non-blocking functions (isend, irecv, Iscatter, etc.) initiate the communication and immediately return, allowing computation to continue in parallel.

In mpi4py, non-blocking communication returns a request object, and you use .Wait() (or .Test()) to complete the operation.

### 🔬 When Does This Help?

* When you have large computations and want to hide communication latency.

* When communication cost is high (e.g., across several machines in a cluster).

* When doing multiple communications that can be overlapped.

### ✅ Example Code with Non-Blocking Communication

For our code we'll:

* parallelizeMonte Carlo point generation & local estimation
* use Non-blocking Ireduce to sum up the total number of points inside the circle

```python
# pi_mpi_nonblocking.py
from mpi4py import MPI
import random
import time

def monte_carlo_pi(samples):
    count = 0
    for _ in range(samples):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:
            count += 1
    return count

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

total_samples = 10_000_000
samples_per_proc = total_samples // size

start_time = time.time()

# Each process estimates its count
local_count = monte_carlo_pi(samples_per_proc)

# Use non-blocking Ireduce
req = comm.Ireduce(local_count, None if rank != 0 else 0, op=MPI.SUM, root=0)

# While waiting for reduction, do something else (optional)
# For demo, simulate work with a sleep (replace with useful computation)
time.sleep(0.1)

# Wait for the non-blocking operation to complete
if rank == 0:
    result = 0
    req = comm.Ireduce(local_count, result, op=MPI.SUM, root=0)
    req.Wait()
    pi_estimate = 4 * result / total_samples
    duration = time.time() - start_time
    print(f"Estimated π: {pi_estimate}")
    print(f"Time taken with {size} processes (non-blocking): {duration:.4f} seconds")
else:
    req.Wait()
```

### 🔍 Key Points

* Ireduce() starts a non-blocking reduction.

* We can perform extra computation between starting and finishing communication.

* .Wait() ensures that the operation finishes before we use the result.

* ⚠️ Ireduce with root must pass a valid storage location for result (not just None).

To fix that, let’s use numpy to store the result.
✅ Improved Version with NumPy Buffer

```python
# pi_mpi_nonblocking_numpy.py
from mpi4py import MPI
import numpy as np
import random
import time

def monte_carlo_pi(samples):
    count = 0
    for _ in range(samples):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:
            count += 1
    return count

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

total_samples = 10_000_000
samples_per_proc = total_samples // size

start_time = time.time()

local_count = monte_carlo_pi(samples_per_proc)

# Use numpy array to store the result on the root
recv_buf = np.zeros(1, dtype='i') if rank == 0 else None
send_buf = np.array(local_count, dtype='i')

# Non-blocking reduction
req = comm.Ireduce(send_buf, recv_buf, op=MPI.SUM, root=0)

# Simulate other work or overlap
time.sleep(0.1)

# Finalize communication
req.Wait()

if rank == 0:
    pi_estimate = 4 * recv_buf[0] / total_samples
    duration = time.time() - start_time
    print(f"Estimated π: {pi_estimate}")
    print(f"Time taken with {size} processes (non-blocking): {duration:.4f} seconds")
```

### ⚠️ Caution

* Don’t forget .Wait() or .Test() — skipping it leads to undefined behavior.

* Don’t modify buffers involved in non-blocking communication before it's complete.

## Part 8: 🧹 Tips & Best Practices

* Always match **send()** with **recv()**, or you may cause a deadlock.

* Where appropriate use non-blocking communication (isend, irecv) for better performance in large programs.

* Start with small examples and increase complexity gradually.
* get something working serially before even thinking about doing it parallel.
* Debugging parallel programs is harder – use logs or process-specific prints.

## Part 9: 🧰 Resources

mpi4py documentation

MPI tutorials (general, in C/C++): https://mpitutorial.com

Books: Parallel Programming with MPI by Peter Pacheco