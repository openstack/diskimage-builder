Building An Image
=================

Now that you have diskimage-builder properly :doc:`installed <installation>`
you can get started by building your first disk image.

VM Image
--------

Our first image is going to be a bootable vm image using one of the standard
supported distribution :doc:`elements <../elements>` (Ubuntu or Fedora).

The following command will start our image build (distro must be either
'ubuntu' or 'fedora'):

::

    disk-image-create <distro> vm

This will create a qcow2 file 'image.qcow2' which can then be booted.

Elements
--------

It is important to note that we are passing in a list of
:doc:`elements <../elements>` to disk-image-create in our above command. Elements
are how we decide what goes into our image and what modifications will be
performed.

Some elements provide a root filesystem, such as the ubuntu or fedora element
in our example above, which other elements modify to create our image. At least
one of these 'distro elements' must be specified when performing an image
build. It's worth pointing out that there are many distro elements (you can even
create your own), and even multiples for some of the distros. This is because
there are often multiple ways to install a distro which are very different.
For example: One distro element might use a cloud image while another uses
a package installation tool to build a root filesystem for the same distro.

Other elements modify our image in some way. The 'vm' element in our example
above ensures that our image has a bootloader properly installed. This is only
needed for certain use cases and certain output formats and therefore it is
not performed by default.
