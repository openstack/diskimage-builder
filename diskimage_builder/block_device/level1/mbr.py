# Copyright 2016 Andreas Florath (andreas@florath.net)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import os
import random

from struct import pack


logger = logging.getLogger(__name__)


# Details of the MBR object itself can be found in the inline
# documentation.
#
# General design and implementation remarks:
# o Because the whole GNU parted and co. (e.g. the python-parted that
#   is based on GNU parted) cannot be used because of the license:
#   everything falls under GPL2 (not LGPL2!) and therefore does not
#   fit into the Apache License here.
# o It looks that there is no real alternative available (2016-06).
# o The interface of python-parted is not that simple to handle - and
#   the initial try to use GNU (python-)parted was not that much
#   easier and shorter than this approach.
# o When using tools (like fdisk or parted) they try to optimize the
#   alignment of partitions based on the data found on the host
#   system.  These might be misleading and might lead to (very) poor
#   performance.
# o These ready-to-use tools typically also change the CHS layout
#   based on the disk size.  In case that the disk is enlarged (which
#   is a normal use case for golden images), the CHS layout of the
#   disk changes for those tools (and is not longer correct).
#   In the DIB implementation the CHS are chosen that way, that also
#   for very small disks the maximum heads/cylinder and sectors/track
#   is used: even if the disk size in increased, the CHS numbers will
#   not change.
# o In the easy and straight forward way when only using one
#   partition, exactly 40 bytes (!) must be written - and the biggest
#   part of this data is fixed (same in all cases).
#
# Limitations and Incompatibilities
# o With the help of this class it is possible to create an
#   arbitrarily number of extended partitions (tested with over 1000).
# o There are limitations and shortcomings in the OS and in tools
#   handling these partitions.
# o Under Linux the loop device is able to handle a limited number of
#   partitions. The module parameter max_loop can be set - the maximum
#   number might vary depending on the distribution and kernel build.
# o Under Linux fdisk is able to handle 'only' 60 partitions. Only
#   those are listed, can be changed or written.
# o Under Linux GNU parted can handle about 60 partitions.
#
# Be sure only to pass in the number of partitions that the host OS
# and target OS are able to handle.

class MBR(object):
    """MBR Disk / Partition Table Layout

    Primary partitions are created first - and must also be passed in
    first.

    The extended partition layout is done in the way, that there is
    one entry in the MBR (the last) that uses the whole disk.
    EBR (extended boot records) are used to describe the partitions
    themselves.  This has the advantage, that the same procedure can
    be used for all partitions and arbitrarily many partitions can be
    created in the same way (the EBR is placed as block 0 in each
    partition itself).

    In conjunction with a fixed and 'fits all' partition alignment the
    major design focus is maximum performance for the installed image
    (vs. minimal size).

    Because of the chosen default alignment of 1MiB there will be
    (1MiB - 512B) unused disk space for the MBR and also the same
    size unused in every partition.

    Assuming that 512 byte blocks are used, the resulting layout for
    extended partitions looks like (blocks offset in extended
    partition given):

    ======== ==============================================
    Offset    Description
    ======== ==============================================
        0     MBR - 2047 blocks unused
     2048     EBR for partition 1 - 2047 blocks unused
     4096     Start of data for partition 1
     ...     ...
      X       EBR for partition N - 2047 blocks unused
      X+2048  Start of data for partition N
    ======== ==============================================

    Direct (native) writing of MBR, EBR (partition table) is
    implemented - no other partitioning library or tools is used -
    to be sure to get the correct CHS and alignment for a wide range
    of host systems.
    """

    # Design & Implementation details:
    # o A 'block' is a storage unit on disk. It is similar (equal) to a
    #   sector - but with LBA addressing.
    # o It is assumed that a disk block has that number of bytes
    bytes_per_sector = 512
    # o CHS is the 'good and very old way' specifying blocks.
    #   When passing around these numbers, they are also ordered like 'CHS':
    #   (cylinder, head, sector).
    # o The computation from LBA to CHS is not unique (it is based
    #   on the 'real' (or assumed) number of heads/cylinder and
    #   sectors/track), these are the assumed numbers.  Please note
    #   that these are also the maximum numbers:
    heads_per_cylinder = 254
    sectors_per_track = 63
    max_cylinders = 1023
    # o There is the need for some offsets that are defined in the
    #   MBR/EBR domain.
    MBR_offset_disk_id = 440
    MBR_offset_signature = 510
    MBR_offset_first_partition_table_entry = 446
    MBR_partition_type_extended_chs = 0x5
    MBR_partition_type_extended_lba = 0xF
    MBR_signature = 0xAA55

    def __init__(self, name, disk_size, alignment):
        """Initialize a disk partitioning MBR object.

        The name is the (existing) name of the disk.
        The disk_size is the (used) size of the disk. It must be a
        proper multiple of the disk bytes per sector (currently 512)
        """
        logger.info("Create MBR disk partitioning object")

        assert disk_size % MBR.bytes_per_sector == 0

        self.disk_size = disk_size
        self.disk_size_in_blocks \
            = self.disk_size // MBR.bytes_per_sector
        self.alignment_blocks = alignment // MBR.bytes_per_sector
        # Because the extended partitions are a chain of blocks, when
        # creating a new partition, the reference in the already
        # existing EBR must be updated. This holds a reference to the
        # latest EBR. (A special case is the first: when it points to
        # 0 (MBR) there is no need to update the reference.)
        self.disk_block_last_ref = 0

        self.name = name
        self.partition_abs_start = None
        self.partition_abs_next_free = None
        # Start of partition number
        self.partition_number = 0

        self.primary_partitions_created = 0
        self.extended_partitions_created = 0

    def __enter__(self):
        # Open existing file for writing (r+)
        self.image_fd = open(self.name, "r+b")
        self.write_mbr()
        self.write_mbr_signature(0)
        self.partition_abs_start = self.align(1)
        self.partition_abs_next_free \
            = self.partition_abs_start
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.image_fd.flush()
        os.fsync(self.image_fd.fileno())
        self.image_fd.close()

    def lba2chs(self, lba):
        """Converts a LBA block number to CHS

        If the LBA block number is bigger than the max (1023, 63, 254)
        the maximum is returned.
        """
        if lba > MBR.heads_per_cylinder * MBR.sectors_per_track \
           * MBR.max_cylinders:
            return MBR.max_cylinders, MBR.heads_per_cylinder, \
                MBR.sectors_per_track

        cylinder = lba // (MBR.heads_per_cylinder * MBR.sectors_per_track)
        head = (lba // MBR.sectors_per_track) % MBR.heads_per_cylinder
        sector = (lba % MBR.sectors_per_track) + 1

        logger.debug("Convert LBA to CHS [%d] -> [%d, %d, %d]",
                     lba, cylinder, head, sector)
        return cylinder, head, sector

    def encode_chs(self, cylinders, heads, sectors):
        """Encodes a CHS triple into disk format"""
        # Head - nothing to convert
        assert heads <= MBR.heads_per_cylinder
        eh = heads

        # Sector
        assert sectors <= MBR.sectors_per_track
        es = sectors
        # top two bits are set in cylinder conversion

        # Cylinder
        assert cylinders <= MBR.max_cylinders
        ec = cylinders % 256  # lower part
        hc = cylinders // 4   # extract top two bits and
        es = es | hc          # pass them into the top two bits of the sector

        logger.debug("Encode CHS to disk format [%d %d %d] "
                     "-> [%02x %02x %02x]", cylinders, heads, sectors,
                     eh, es, ec)
        return eh, es, ec

    def write_mbr(self):
        """Write MBR

        This method writes the MBR to disk. It creates a random disk
        id as well that it creates the extended partition (as
        first partition) which uses the whole disk.
        """
        disk_id = random.randint(0, 0xFFFFFFFF)
        self.image_fd.seek(MBR.MBR_offset_disk_id)
        self.image_fd.write(pack("<I", disk_id))

    def write_mbr_signature(self, blockno):
        """Writes the MBR/EBR signature to a block

        The signature consists of a 0xAA55 in the last two bytes of the
        block.
        """
        self.image_fd.seek(blockno *
                           MBR.bytes_per_sector +
                           MBR.MBR_offset_signature)
        self.image_fd.write(pack("<H", MBR.MBR_signature))

    def write_partition_entry(self, bootflag, blockno, entry, ptype,
                              lba_start, lba_length):
        """Writes a partition entry

        The entries are always the same and contain 16 bytes. The MBR
        and also the EBR use the same format.
        """
        logger.info("Write partition entry blockno [%d] entry [%d] "
                    "start [%d] length [%d]", blockno, entry,
                    lba_start, lba_length)

        self.image_fd.seek(
            blockno * MBR.bytes_per_sector +
            MBR.MBR_offset_first_partition_table_entry +
            16 * entry)
        # Boot flag
        self.image_fd.write(pack("<B", 0x80 if bootflag else 0x00))

        # Encode lba start / length into CHS
        chs_start = self.lba2chs(lba_start)
        chs_end = self.lba2chs(lba_start + lba_length)
        # Encode CHS into disk format
        chs_start_bin = self.encode_chs(*chs_start)
        chs_end_bin = self.encode_chs(*chs_end)

        # Write CHS start
        self.image_fd.write(pack("<BBB", *chs_start_bin))
        # Write partition type
        self.image_fd.write(pack("<B", ptype))
        # Write CHS end
        self.image_fd.write(pack("<BBB", *chs_end_bin))
        # Write LBA start & length
        self.image_fd.write(pack("<I", lba_start))
        self.image_fd.write(pack("<I", lba_length))

    def align(self, blockno):
        """Align the blockno to next alignment count"""
        if blockno % self.alignment_blocks == 0:
            # Already aligned
            return blockno

        return (blockno // self.alignment_blocks + 1) \
            * self.alignment_blocks

    def compute_partition_lbas(self, abs_start, size):
        lba_partition_abs_start = self.align(abs_start)
        lba_partition_rel_start \
            = lba_partition_abs_start - self.partition_abs_start
        lba_partition_length = size // MBR.bytes_per_sector
        lba_abs_partition_end \
            = self.align(lba_partition_abs_start + lba_partition_length)
        logger.info("Partition absolute [%d] relative [%d] "
                    "length [%d] absolute end [%d]",
                    lba_partition_abs_start, lba_partition_rel_start,
                    lba_partition_length, lba_abs_partition_end)
        return lba_partition_abs_start, lba_partition_length, \
            lba_abs_partition_end

    def add_primary_partition(self, bootflag, size, ptype):
        lba_partition_abs_start, lba_partition_length, lba_abs_partition_end \
            = self.compute_partition_lbas(self.partition_abs_next_free, size)

        self.write_partition_entry(
            bootflag, 0, self.partition_number, ptype,
            self.align(lba_partition_abs_start), lba_partition_length)

        self.partition_abs_next_free = lba_abs_partition_end
        logger.debug("Next free [%d]", self.partition_abs_next_free)
        self.primary_partitions_created += 1
        self.partition_number += 1
        return self.partition_number

    def add_extended_partition(self, bootflag, size, ptype):
        lba_ebr_abs = self.partition_abs_next_free
        logger.info("EBR block absolute [%d]", lba_ebr_abs)

        _, lba_partition_length, lba_abs_partition_end \
            = self.compute_partition_lbas(lba_ebr_abs + 1, size)

        # Write the reference to the new partition
        if self.disk_block_last_ref != 0:
            partition_complete_len = lba_abs_partition_end - lba_ebr_abs
            self.write_partition_entry(
                False, self.disk_block_last_ref, 1,
                MBR.MBR_partition_type_extended_chs,
                lba_ebr_abs - self.partition_abs_start,
                partition_complete_len)

        self.write_partition_entry(
            bootflag, lba_ebr_abs, 0, ptype, self.align(1),
            lba_partition_length)
        self.write_mbr_signature(lba_ebr_abs)

        self.partition_abs_next_free = lba_abs_partition_end
        logger.debug("Next free [%d]", self.partition_abs_next_free)
        self.disk_block_last_ref = lba_ebr_abs
        self.extended_partitions_created += 1
        self.partition_number += 1
        return self.partition_number

    def add_partition(self, primaryflag, bootflag, size, ptype):
        """Adds a partition with the given type and size"""
        logger.debug("Add new partition primary [%s] boot [%s] "
                     "size [%d] type [%x]",
                     primaryflag, bootflag, size, ptype)

        # primaries must be created before extended
        if primaryflag and self.extended_partitions_created > 0:
            raise RuntimeError("All primary partitions must be "
                               "given first")

        if primaryflag:
            return self.add_primary_partition(bootflag, size, ptype)
        if self.extended_partitions_created == 0:
            # When this is the first extended partition, the extended
            # partition entry has to be written.
            self.partition_abs_start = self.partition_abs_next_free
            self.write_partition_entry(
                False, 0, self.partition_number,
                MBR.MBR_partition_type_extended_lba,
                self.partition_abs_next_free,
                self.disk_size_in_blocks - self.partition_abs_next_free)
            self.partition_number = 4

        return self.add_extended_partition(bootflag, size, ptype)

    def free(self):
        """Returns the free (not yet partitioned) size"""
        return self.disk_size \
            - (self.partition_abs_next_free + self.align(1)) \
            * MBR.bytes_per_sector
