===============================
architecture-emulation-binaries
===============================

This element enables execution for different architectures

When building an image for an architecture that the host machine
can not execute, we need to chroot into the image to execute code,
and if the host architecture does not match, we need to emulate
the instructions.

This element does the following:

 * copies the binary file into chroot /usr/bin environment.
   Binary file is chosen based on host architecture and
   image architecture the user is trying to build.

   If an image we are building for an architecture is not the host
   architecture, install tools provided by qemu-user-static
   (which needs to be installed) to allow us to run commands
   inside the building image.

   This is tested on amd64/i386 architecture to build armhf and arm64
   ubuntu cloud images.
