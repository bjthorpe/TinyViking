---
layout: page
title: "Build Instructions"
permalink: /Instructions/
toc: true
---

## Checklist of materials

To build the Raspberry Pi cluster you will need the following:

- **8 Raspberry Pis** model 3 or 4
- **8 microSD cards** recommended 32Gb
- **8 Raspberry Pi Poe+ Hats**
- **8 GPIO pin risers**
- **8 4 pin power risers**
- **8 Ethernet cables**
- **1 8-port network switch** must be POE capable
- **1 USB stick** for shared storage, recommended 128Gb
- **1 keyboard, monitor and HDMI/micro HDMI lead** for use with login node (Note: Pi4 uses micro HDMI)

## Flash the Raspberry Pis

First Download the raspberry pi imager software from the raspberry pi foundation website https://www.raspberrypi.com/software.

## Setting up the Pis

For each pi in the cluster:

- connect to pi ethernet
- run raspi-config

```bash
sudo raspi-config
```

- turn on ssh
- set WiFi country to GB
- set timezone
- turn on and connect to WiFi
- expand the filesystem

- set each pi's hostname as "somestring"_unique_number eg RaspberyPi_01

```bash
sudo hostname RaspberyPi_01       # whatever name you chose
sudo nano /etc/hostname    # change the hostname here too
sudo nano /etc/hosts       # change "raspberrypi" to "RaspberyPi_01"
```

- run apt update
- set a static unique local ip address for the ethernet port.

We used 192.168.50.X (where X is the number assigned to the pi) with a default gateway of 255.255.255.0.

- set system time via network

```bash
sudo apt install ntpdate -y
```

## Final setup steps for login node

Choose 1 pi to be the login node and connect that to the screen and keyboard. The rest will be accessed by ssh.

To make name resolution easier, we’re going to add hostnames of the nodes and their IP addresses to the /etc/hosts file. Edit /etc/hosts and add the following lines:

```bash 
sudo nano /etc/hosts

<ip addr of RaspberyPi_02>      RaspberyPi_02
<ip addr of RaspberyPi_03>      RaspberyPi_03
<ip addr of RaspberyPi_04>      RaspberyPi_04

```

- test you can login with:

```bash
ssh RaspberyPi_02" # repeat for nodes 3 to N 
```

- setup and add ssh keys for password less login

## Setting up shared storage

For the login node

- Plug the flash drive into one of the USB ports.
Note: you may wish to grab a copy of whatever is on there as the drive will be formatted.
- Figure out its dev location by examining the output of lsblk

```bash
lsblk
```

- Format the drive to use the ext4 filesystem:

```bash
sudo mkfs.ext4 /dev/sda1
```

A word of warning: double check to be sure you’re not about to overwrite your root / directory by accident.

- Create the mount directory

Note that this should be the same across all the nodes. In this example we will use /clusterfs:

```bash
sudo mkdir /clusterfs
sudo chown nobody:nogroup -R /clusterfs
sudo chmod 777 -R /clusterfs
```

- Setup automatic mounting. 

To mount our flash drive on boot, we need to find the UUID. To do this, run blkid and make note of the UUID from /dev/sda1 then edit fstab to mount the drive on boot.

```bash
sudo nano /etc/fstab
```

Add the following line:

```bash
UUID=${SOME_NUMBER}$ /clusterfs ext4 defaults 0 2
```

- Finally, mount the drive and set file permissions.

```bash
sudo mount -a.
sudo chown nobody:nogroup -R /clusterfs
sudo chmod -R 766 /clusterfs
```

## Export the NFS Share

Now, we need to export the mounted drive as a network file system share so the other nodes can access it. Do this process on the master node:

- Install the NFS server.

```bash
sudo apt install nfs-kernel-server -y
```

- Export the NFS share.

Edit /etc/exports and add the following line:

```bash
/clusterfs    <ip addr>(rw,sync,no_root_squash,no_subtree_check)
```

Replace <ip addr> with the IP address schema used on your local network. This will allow any LAN client to mount the share.

- Lastly, run the following command to update the NFS kernel server:

```bash
sudo exportfs -a
```

## Mount the NFS Share on the Clients

Now that we’ve got the NFS share exported from the master node, we want to mount it on all of the other nodes so they can access it. Repeat the following process for all of the other nodes.

### Install the NFS client

```bash
sudo apt install nfs-common -y
```

### Create the mount folder

This should be the same directory that you mounted the flash drive to on the master node. In our case, this is /clusterfs:

```bash
sudo mkdir /clusterfs
sudo chown nobody.nogroup /clusterfs
sudo chmod -R 777 /clusterfs
```

### Setup automatic mounting

We want the NFS share to mount automatically when the nodes boot. Edit /etc/fstab to accomplish this by adding the following line:

```bash
<master node ip>:/clusterfs    /clusterfs    nfs    defaults   0 0
```

Now mount it with:

```bash
sudo mount -a
```

At this stage you should be able to create a file in /clusterfs and have it show up at the same path across all the nodes.

## Installing MPI and MPI4py

on each node run the following:

```bash
sudo apt install mpich python3-mpi4py
```

test mpi works by running a test script hello.py

```bash
cd /clusterfs
mpirun python hello.py
```

Now test running across multiple nodes

```bash
mpirun -N 2 -H RaspberyPi_01,RaspberyPi_02 python hello.py
```

## OPTIONAL: Installing and Configuring SLURM on the Master Node

### Install SLURM

```bash
sudo apt install slurm-wlm -y
```

### SLURM Configuration

We’ll use the default SLURM configuration file as a base.

```bash
cd /etc/slurm-llnl
cp /usr/share/doc/slurm-client/examples/slurm.conf.simple.gz .
gzip -d slurm.conf.simple.gz
mv slurm.conf.simple slurm.conf
```

### Set the control machine info.

All the edits in this section are done in the configuration file /etc/slurm-llnl/slurm.conf

```bash
sudo nano /etc/slurm-llnl/slurm.conf
```

We'll start by including the hostname of the master node, and its IP address. Edit the line containing SlurmctldHost to:

```text
SlurmctldHost=RaspberyPi_01(<ip addr of RaspberyPi_01>)
# e.g.: RaspberyPi_01(192.168.1.14)
```

Next we'll customize the scheduler algorithm.

SLURM can allocate resources to jobs in a number of different ways, but for our cluster we’ll use the “consumable resources” method. This basically means that each node has a consumable resource (in this case, CPU cores), and it allocates resources to jobs based on these resources. So, edit the SelectType field and provide parameters, like so:

```text
SelectType=select/cons_res
SelectTypeParameters=CR_Core
```

Then set the cluster name.

```text
ClusterName=TinyViking
```

Now we need to tell SLURM about the compute nodes. Near the end of the file, there should be an example entry for the compute node. Delete it, and add the following configurations for the cluster nodes:

```text
NodeName=RaspberyPi_01 NodeAddr=<ip addr RaspberyPi_01> CPUs=4 State=UNKNOWN
NodeName=RaspberyPi_02 NodeAddr=<ip addr RaspberyPi_02> CPUs=4 State=UNKNOWN
NodeName=RaspberyPi_03 NodeAddr=<ip addr RaspberyPi_03> CPUs=4 State=UNKNOWN
NodeName=RaspberyPi_04 NodeAddr=<ip addr RaspberyPi_04> CPUs=4 State=UNKNOWN
```

SLURM runs jobs on ‘partitions,’ or groups of nodes. We’ll create a default partition and add our 7 compute nodes to it. Be sure to delete the example partition in the file, then add the following on one line:

```text
PartitionName=mycluster Nodes=node[02-08] Default=YES MaxTime=INFINITE State=UP
```

### Configuring Cgroups

SLURM has integrated support for cgroups kernel isolation, which restricts access to system resources. We need to tell SLURM what resources to allow jobs to access. To do this, create the file /etc/slurm-llnl/cgroup.conf:

```bash
sudo nano /etc/slurm-llnl/cgroup.conf
```

```text
CgroupMountpoint="/sys/fs/cgroup"
CgroupAutomount=yes
CgroupReleaseAgentDir="/etc/slurm-llnl/cgroup"
AllowedDevicesFile="/etc/slurm-llnl/cgroup_allowed_devices_file.conf"
ConstrainCores=no
TaskAffinity=no
ConstrainRAMSpace=yes
ConstrainSwapSpace=no
ConstrainDevices=no
AllowedRamSpace=100
AllowedSwapSpace=0
MaxRAMPercent=100
MaxSwapPercent=100
MinRAMSpace=30
```

Now, whitelist system devices by creating the file /etc/slurm-llnl/cgroup_allowed_devices_file.conf:

```bash
sudo nano /etc/slurm-llnl/cgroup_allowed_devices_file.conf
```

```text
/dev/null
/dev/urandom
/dev/zero
/dev/sda*
/dev/cpu/*/*
/dev/pts/*
/clusterfs*
```

Note that this configuration is pretty permissive, but is fine for our purposes, just don't use this in production.

In order for the other nodes to be controlled by SLURM, they need to have the same configuration file, as well as the Munge key file. Copy those to shared storage to make them easier to access, like so:

```bash
sudo cp slurm.conf cgroup.conf cgroup_allowed_devices_file.conf /clusterfs
sudo cp /etc/munge/munge.key /clusterfs
```

```text
A word about Munge:

Munge is the access system that SLURM uses to run commands and processes on the other nodes. Similar to key-based SSH, it uses a private key on all the nodes, then requests are timestamp-encrypted and sent to the node, which decrypts them using the identical key. This is why it is so important that the system times be in sync, and that they all have the munge.key file.
```

Next we enable and Start SLURM Control Services.

First we'll start munge:

```bash
sudo systemctl enable munge
sudo systemctl start munge
```

Then the SLURM daemons:

```bash
# slurm Daemon
sudo systemctl enable slurmd
sudo systemctl start slurmd
# control daemon
sudo systemctl enable slurmctld
sudo systemctl start slurmctld
```

### Reboot. (optional)

This step is optional, but if you are having problems with Munge authentication, or your nodes can’t communicate with the SLURM controller, try rebooting it.

## Configure the Compute Nodes

On each compute node:

First Install the SLURM Client

```bash
sudo apt install slurmd slurm-client -y
```

Update the /etc/hosts file like we did on the master node. Add all of the nodes and their IP addresses to the /etc/hosts file of each node, excluding that node. Something like this:

```bash
sudo nano /etc/hosts

<ip addr>    RaspberyPi_01
<ip addr>    RaspberyPi_03
<ip addr>    RaspberyPi_04
```

Next we need to make sure that the configuration on the compute nodes matches the configuration on the master node exactly. So, copy it over from shared storage:

```bash
sudo cp /clusterfs/munge.key /etc/munge/munge.key
sudo cp /clusterfs/slurm.conf /etc/slurm-llnl/slurm.conf
sudo cp /clusterfs/cgroup* /etc/slurm-llnl
```

### Munge setup
Now we will test that the Munge key copied correctly and that the SLURM controller can successfully authenticate with the client nodes.

Enable and start Munge on each compute node.

```bash
sudo systemctl enable munge
sudo systemctl start munge
```

We can manually test Munge to see if it is communicating. Run the following to generate a key on the master node and try to have the client node decrypt it. (Run this on the client.)

```bash
ssh pi@RaspberyPi_01 munge -n | unmunge
```

If it works, you should see something like this:

```text
pi@RaspberyPi_02 ~> ssh RaspberyPi_01 munge -n | unmunge
pi@RaspberyPi_01's password: 
STATUS:           Success (0)
ENCODE_HOST:      RaspberyPi_01
ENCODE_TIME:      2018-11-15 15:48:56 -0600 (1542318536)
DECODE_TIME:      2018-11-15 15:48:56 -0600 (1542318536)
TTL:              300
CIPHER:           aes128 (4)
MAC:              sha1 (3)
ZIP:              none (0)
UID:              pi
GID:              pi
LENGTH:           0
```

If you get an error, make sure that the /etc/munge/munge.key file is the same across all the different nodes, then reboot them all and try again.

Finally we can Start the SLURM Daemon (again run this on each compute node)

```bash
sudo systemctl enable slurmd
sudo systemctl start slurmd
```

Complete this configuration on each of the compute nodes.


## Testing SLURM

Now that we’ve configured the SLURM controller and each of the nodes, we can check to make sure that SLURM can see all of the nodes by running sinfo on the master node (a.k.a. “the login node”):

```bash
sinfo

PARTITION    AVAIL  TIMELIMIT  NODES  STATE NODELIST
mycluster*      up   infinite      7   idle node[02-08]
```

Now we can run a test job by telling SLURM to give us all 7 nodes, and run the hostname command on each of them:

```bash
srun --nodes=7 hostname
```

If all goes well, we should see something like:

```text
RaspberyPi_02
RaspberyPi_03
RaspberyPi_04
RaspberyPi_05
RaspberyPi_06
RaspberyPi_07
RaspberyPi_08
```