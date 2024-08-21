####
** MOUNT USB dev**
*описание*


root@isam:/home/user# `lsblk`
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0 55,9G  0 disk 
├─sda1   8:1    0 54,9G  0 part /
├─sda2   8:2    0    1K  0 part 
└─sda5   8:5    0  975M  0 part [SWAP]
sdb      8:16   0  1,8T  0 disk 
└─sdb1   8:17   0  1,8T  0 part /media/user/2T
sr0     11:0    1 1024M  0 rom  


root@isam:/home/user# `fdisk -l`
Disk /dev/sda: 55,9 GiB, 60022480896 bytes, 117231408 sectors
Disk model: KINGSTON SV300S3
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x615111ba

Device     Boot     Start       End   Sectors  Size Id Type
/dev/sda1  *         2048 115230719 115228672 54,9G 83 Linux
/dev/sda2       115232766 117229567   1996802  975M  5 Extended
/dev/sda5       115232768 117229567   1996800  975M 82 Linux swap / Solaris


Disk /dev/sdb: 1,82 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: EFAX-68B2RN1    
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 97467A0B-2782-4D4E-AFCA-912D89DA9338

Device     Start        End    Sectors  Size Type
/dev/sdb1   2048 3907028991 3907026944  1,8T Microsoft basic data
root@isam:/home/user# 
root@isam:/home/user# mkdir /mnt/USB
root@isam:/home/user# mount /dev/sdb1 /mnt/USB/
Mount is denied because the NTFS volume is already exclusively opened.
The volume may be already mounted, or another software may use it which
could be identified for example by the help of the 'fuser' command.

root@isam:/home/user# `mount /dev/sdb1 /mnt/USB/`

root@isam:/home/user# `ls -l /mnt/USB/`
итого 48
drwxrwxrwx 1 user user    0 сен 22 23:29 '$RECYCLE.BIN'
drwxrwxrwx 1 user user 4096 июн 15 14:50  APK
-rwxrwxrwx 1 user user 2553 июл 20 05:25  Audio.lnk
drwxrwxrwx 1 user user 8192 сен 24 02:50  exe
drwxrwxrwx 1 user user 4096 авг 29 15:19  Games
drwxrwxrwx 1 user user    0 сен 24 02:42  ISO
-rwxrwxrwx 1 user user 2678 июл 20 05:25  Movies.lnk
drwxrwxrwx 1 user user 4096 июн 10 16:21 'Orange Pi'
-rwxrwxrwx 1 user user    0 июл 12 19:53 '#Storage02'
drwxrwxrwx 1 user user 4096 июн  8 21:13 'System Volume Information'
drwxrwxrwx 1 user user    0 авг 26 09:59  Torrents
-rwxrwxrwx 1 user user 2683 июл 20 05:24  TVShows.lnk
drwxrwxrwx 1 user user 8192 сен 24 02:49  usbTunes
drwxrwxrwx 1 user user 4096 сен 24 02:42  Work
root@isam:/home/user# chown $USER /mnt/USB/


root@isam:/home/user# `umount /mnt/USB/`

**Mount to FSTAB**

1. `sudo nano /etc/fstab`

and add the line below

UUID=2T /media auto nosuid,nodev,nofail 0 0

Replace the UUID in my example above with the UUID of your partition

sudo blkid /dev/sdb1 | awk -F'"' '{print $2}'

Note, the entry in your fstab doesn't mount the drive if it's not present during startup.

OR

/dev/sdb1   /mnt/USB   ntfs-3g defaults,user,permissions,locale=ru_RU.UTF-8,rw    0   0

OR
root@isam:/home/user#  `lsblk -f /dev/sdb1`
NAME FSTYPE FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINT
sdb1 ntfs         2T    AAAC3BE7AC3BACA7 

`sudo nano /etc/fstab`

UUID=AAAC3BE7AC3BACA7 /home/user/USB/2T ntfs defaults,noatime,nofail 0 2

UUID=5800506300504A60 /home/user/USB/torrents ntfs defaults,noatime,nofail 0 2

#UUID=DA44FC1644FBF35D /home/user/USB/05T ntfs defaults,noatime,nofail 0 2

