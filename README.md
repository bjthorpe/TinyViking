# Building a DIY raspberry pi cluster using SLURM

## Flash the Raspberry Pis
First Dowload the rapbery pi imager software from the raspbery pi foundation website https://www.raspberrypi.com/software. 

Then For each pi in the cluster
 - connect to pi ethernet
- set each pi's hostname as somestring_unique_number verbatim eg raspberypi_01
- login to enable ssh, update via wifi and note down the local ip address 
    hit use hostname -I | cut -d' ' -f1)
- set system time via network with sudo apt install ntpdate -y


Finally choose 1 pi to be the login node and connect that to the screen and keyboard. The rest will be accessed by ssh.
    
- Plug the flash drive into one of the USB ports on the master node. Then, figure out its dev location by examining the output of lsblk:

- Format the drive to use the ext4 filesystem:

  sudo mkfs.ext4 /dev/sda1


A word of warning: double check to be sure you’re not about to overwrite your root / directory by accident.

Create the mount directory.
(Note that this should be the same across all the nodes.) In my cluster, I used /clusterfs:

sudo mkdir /clusterfs
sudo chown nobody.nogroup -R /clusterfs
sudo chmod 777 -R /clusterfs


- Setup automatic mounting. To mount our flash drive on boot, we need to find the UUID. To do this, run blkid and make note of the UUID from /dev/sda1 then edit fstab to mount the drive on boot.

sudo nano /etc/fstab


Add the following line:

UUID=${SOME_NUMBER}$ /clusterfs ext4 defaults 0 2

Finally, mount the drive with 

sudo mount -a.


- Set file permissions.

sudo chown nobody.nogroup -R /clusterfs
sudo chmod -R 766 /clusterfs



## Export the NFS Share
Now, we need to export the mounted drive as a network file system share so the other nodes can access it. Do this process on the master node.


- Install the NFS server.

sudo apt install nfs-kernel-server -y
- Export the NFS share.

Edit /etc/exports and add the following line:


/clusterfs    <ip addr>(rw,sync,no_root_squash,no_subtree_check)

Replace <ip addr> with the IP address schema used on your local network. This will allow any LAN client to mount the share.

- Lastly, run the following command to update the NFS kernel server:

sudo exportfs -a

## Mount the NFS Share on the Clients
Now that we’ve got the NFS share exported from the master node, we want to mount it on all of the other nodes so they can access it. Repeat this process for all of the other nodes.

## Install the NFS client.

This is easily done with run sudo apt install nfs-common -y
###Create the mount folder. 

This should be the same directory that you mounted the flash drive to on the master node. In my case, this is /clusterfs:

sudo mkdir /clusterfs
sudo chown nobody.nogroup /clusterfs
sudo chmod -R 777 /clusterfs
### Setup automatic mounting.
We want the NFS share to mount automatically when the nodes boot. Edit /etc/fstab to accomplish this by adding the following line:

<master node ip>:/clusterfs    /clusterfs    nfs    defaults   0 0
Now mount it with sudo mount -a and you should be able to create a file in /clusterfs and have it show up at the same path across all the nodes.
