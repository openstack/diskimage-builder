Design
======

Images are built using a chroot and bind mounted /proc /sys and /dev. The goal
of the image building process is to produce blank slate machines that have all
the necessary bits to fulfill a specific purpose in the running of an OpenStack
cloud: e.g. a nova-compute node. Images produce either a filesystem image with
a label of cloudimg-rootfs, or can be customised to produce whole disk images
(but will still contain a filesystem labelled cloudimg-rootfs). Once the file
system tree is assembled a loopback device with filesystem (or partition table
and file system) is created and the tree copied into it. The file system
created is an ext4 filesystem just large enough to hold the file system tree
and can be resized up to 1PB in size.

To produce the smallest image the utility fstrim is used. When deleting a file
the space is simply marked as free on the disk, the file is still there until
it is overwritten. fstrim informs the underlying disk to drop those bytes the
end result of which is like writting zeros over those sectors. The same effect
could be achieved by creating a large file full of zeros and removing that
file, however that method is far more IO intensive.

An element is a particular set of code that alters how the image is built, or
runs within the chroot to prepare the image. E.g. the local-config element
copies in the http proxy and ssh keys of the user running the image build
process into the image, whereas the vm element makes the image build a regular
VM image with partition table and installed grub boot sector. The mellanox
element adds support for mellanox infiniband hardware to both the deploy
ramdisk and the built images.

Images must specify a base distribution image element. Currently base
distribution elements exist for fedora, rhel, ubuntu, debian and
opensuse. Other distributions may be added in future, the
infrastructure deliberately makes few assumptions about the exact
operating system in use.  The base image has opensshd running (a new
key generated on first boot) and accepts keys via the cloud metadata
service, loading them into the distribution specific default user
account.

The goal of a built image is to have any global configuration ready to roll,
but nothing that ties it to a specific cloud instance: images should be able to
be dropped into a test cloud and validated, and then deployed into a production
cloud (usually via bare metal nova) for production use. As such, the image
contents can be modelled as three distinct portions:

- global content: the actual code, kernel, always-applicable config (like
  disabling password authentication to sshd).
- metadata / config management provided configuration: user ssh keys, network
  address and routes, configuration management server location and public key,
  credentials to access other servers in the cloud. These are typically
  refreshed on every boot.
- persistent state: sshd server key, database contents, swift storage areas,
  nova instance disk images, disk image cache. These would typically be stored
  on a dedicated partition and not overwritten when re-deploying the image.

The goal of the image building tools is to create machine images that contain
the correct global content and are ready for 'last-mile' configuration by the
nova metadata API, after which a configuration management system can take over
(until the next deploy, when it all starts over from scratch).
