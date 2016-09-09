===================
partitioning-sfdisk
===================
Sets up a partitioned disk using sfdisk, according to user needs.

Environment Variables
---------------------
DIB_PARTITIONING_SFDISK_SCHEMA
  : Required: Yes
  : Default: 2048,,L *
             0 0;
             0 0;
             0 0;
  : Description: A multi-line string specifying a disk schema in sectors.
  : Example: ``DIB_PARTITIONING_SFDISK_SCHEMA="
    2048,10000,L *
    10248,,L
    0 0;
    " will create two partitions on disk, first one will be bootable.
